using System;
using System.IO;
using System.Linq;
using System.Collections;
using System.Collections.Generic;
using System.Diagnostics;
using System.Diagnostics.Tracing;
using System.Reflection;
using System.Runtime.Loader;
using System.Text.Json;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata;

sealed class ConnectionGuard : EventListener, IObserver<DiagnosticListener>, IObserver<KeyValuePair<string, object?>>
{
    public static string Output = "";
    public void OnNext(DiagnosticListener listener) { listener.Subscribe(this); }
    public void OnNext(KeyValuePair<string, object?> item)
    {
        if (item.Key.EndsWith("ConnectionOpening", StringComparison.Ordinal) || item.Key.EndsWith("CommandExecuting", StringComparison.Ordinal) || item.Key.EndsWith("HttpRequestOut.Start", StringComparison.Ordinal)) Stop(item.Key);
    }
    protected override void OnEventSourceCreated(EventSource source)
    {
        if (source.Name is "System.Net.Sockets" or "System.Net.Http") EnableEvents(source, EventLevel.LogAlways, EventKeywords.All);
    }
    protected override void OnEventWritten(EventWrittenEventArgs e)
    {
        if (e.EventName is "ConnectStart" or "RequestStart") Stop(e.EventSource.Name + "/" + e.EventName);
    }
    static void Stop(string name)
    {
        File.WriteAllText(Path.Combine(Output, "connection-attempt.json"), JsonSerializer.Serialize(new { status="STOPPED_CONNECTION_ATTEMPT", eventName=name, payload="not recorded" }));
        Environment.Exit(78);
    }
    public void OnError(Exception error) { }
    public void OnCompleted() { }
}

static class Inspector
{
    static string Stage = "bootstrap";
    static string Output = "";
    static Assembly Candidate = null!;
    static MethodInfo[] AggregateMethods = Array.Empty<MethodInfo>();
    static List<string> Gaps = new();
    static readonly JsonSerializerOptions JsonOptions = new() { WriteIndented=true };
    static void Save(string name, object value) => File.WriteAllText(Path.Combine(Output, name), JsonSerializer.Serialize(value, JsonOptions));
    static bool? Aggregate(INavigation nav)
    {
        var methods=AggregateMethods.Where(m => m.GetParameters()[0].ParameterType.IsInstanceOfType(nav)).ToArray();
        if (methods.Length != 1) { Gaps.Add("aggregate-method-resolution:"+nav.DeclaringEntityType.Name+"."+nav.Name+":"+methods.Length); return null; }
        return (bool)methods[0].Invoke(null, new object[] { nav })!;
    }
    static object Property(IProperty p, IEntityType type)
    {
        string? table=type.GetTableName();
        var store=table is null ? (StoreObjectIdentifier?)null : StoreObjectIdentifier.Table(table,type.GetSchema());
        return new { name=p.Name, column=store is null ? null : p.GetColumnName(store.Value), columnType=p.GetColumnType(), clrType=p.ClrType.FullName, nullable=p.IsNullable, shadow=p.IsShadowProperty(), propertyInfo=p.PropertyInfo?.Name, fieldInfo=p.FieldInfo?.Name };
    }
    static object Entity(IEntityType type, object? typedContext=null)
    {
        var navs=type.GetNavigations().OrderBy(n=>n.Name,StringComparer.Ordinal).Select(n => new {
            name=n.Name, declaringType=n.DeclaringEntityType.Name, targetType=n.TargetEntityType.Name,
            targetTable=n.TargetEntityType.GetTableName(), targetSchema=n.TargetEntityType.GetSchema(),
            collection=n.IsCollection, propertyInfo=n.PropertyInfo?.Name, aggregate=Aggregate(n),
            propertyAttributeTypes=n.PropertyInfo?.CustomAttributes.Select(a=>a.AttributeType.FullName).ToArray(),
            inverse=n.Inverse?.Name, fkDeclaringType=n.ForeignKey.DeclaringEntityType.Name,
            fkProperties=n.ForeignKey.Properties.Select(p=>new {name=p.Name,shadow=p.IsShadowProperty(),propertyInfo=p.PropertyInfo?.Name}).ToArray(),
            principalKey=n.ForeignKey.PrincipalKey.Properties.Select(p=>p.Name).ToArray(),
            principalToDependent=n.ForeignKey.PrincipalToDependent?.Name,
            collectionBackReference=n.ForeignKey.PrincipalToDependent?.IsCollection ?? false
        }).ToArray();
        bool? backReference=typedContext is null ? null : (bool)typedContext.GetType().GetMethod("IsBackReference",BindingFlags.Instance|BindingFlags.Public)!.Invoke(typedContext,new object[]{type.ClrType})!;
        return new { name=type.Name, clrType=type.ClrType.FullName, baseClrType=type.ClrType.BaseType?.FullName,
            schema=type.GetSchema(), table=type.GetTableName(), properties=type.GetProperties().Select(p=>Property(p,type)).ToArray(),
            primaryKey=type.FindPrimaryKey()?.Properties.Select(p=>p.Name).ToArray(),
            keys=type.GetKeys().Select(k=>k.Properties.Select(p=>p.Name).ToArray()).ToArray(),
            foreignKeys=type.GetForeignKeys().Select(f=>new {properties=f.Properties.Select(p=>p.Name).ToArray(),principalType=f.PrincipalEntityType.Name,principalKey=f.PrincipalKey.Properties.Select(p=>p.Name).ToArray(),unique=f.IsUnique,required=f.IsRequired}).ToArray(),
            navigations=navs, skipNavigations=type.GetSkipNavigations().Select(n=>n.Name).ToArray(), typedBackReference=backReference };
    }
    static void Walk(IEntityType type,int depth,Dictionary<string,object> entities,HashSet<string> visited,List<object> edges)
    {
        entities.TryAdd(type.Name,Entity(type));
        if (!visited.Add(type.Name+":"+depth) || depth>=7) return;
        foreach (var nav in type.GetNavigations().OrderBy(n=>n.Name,StringComparer.Ordinal))
        {
            string action;IEntityType? target=null;bool recurse=false;
            var fk=nav.ForeignKey;
            if (nav.IsCollection)
            {
                target=fk.DeclaringEntityType;var pk=target.FindPrimaryKey();
                if (pk is null || pk.DeclaringEntityType != target) action="skip-no-declared-pk";
                else if (pk.Properties.Count>1) action="join-columns-only";
                else { var agg=Aggregate(nav);recurse=agg==true;action=agg is null ? "unresolved-aggregate" : recurse ? "aggregate-full-row" : "key-fk-only"; }
            }
            else if (fk.DeclaringEntityType != nav.DeclaringEntityType) action="skip-inverse";
            else if (fk.Properties[0].IsShadowProperty()) action="skip-shadow-fk";
            else if (fk.PrincipalToDependent?.IsCollection==true) action="parent-fk-reference-only";
            else {var agg=Aggregate(nav);recurse=agg==true;action=agg is null ? "unresolved-aggregate" : recurse ? "aggregate-full-row" : "parent-fk-reference-only";target=nav.TargetEntityType;}
            edges.Add(new { from=type.Name,navigation=nav.Name,depth,action,target=target?.Name });
            if (target is not null) entities.TryAdd(target.Name,Entity(target));
            if (recurse && target is not null) Walk(target,depth+1,entities,visited,edges);
        }
    }
    static void Typed(Type typedType,IModel complete,string shortName)
    {
        Stage="typed-model-"+shortName;
        var persistent=complete.GetEntityTypes().Single(t=>t.ClrType.Name==shortName);
        var editType=persistent.ClrType.BaseType ?? throw new InvalidOperationException("Missing edit base type");
        using var ctx=(DbContext)typedType.GetMethod("Create",BindingFlags.NonPublic|BindingFlags.Static)!.Invoke(null,new object[]{editType})!;
        var model=ctx.Model;
        var readOnly=typedType.GetProperty("ReadOnlyTypes",BindingFlags.NonPublic|BindingFlags.Instance)?.GetValue(ctx) as IEnumerable;
        Save("typed-"+shortName+".json", new { contextType=ctx.GetType().FullName,modelType=model.GetType().FullName,editType=editType.FullName,
            readOnlyTypes=readOnly?.Cast<Type>().Select(t=>t.FullName).OrderBy(x=>x).ToArray(),
            entities=model.GetEntityTypes().OrderBy(t=>t.Name).Select(t=>Entity(t,ctx)).ToArray() });
    }
    public static int Main(string[] args)
    {
        Output=args[1];ConnectionGuard.Output=Output;
        using var guard=new ConnectionGuard();using var diagnostics=DiagnosticListener.AllListeners.Subscribe(guard);
        try
        {
            string app=Path.GetDirectoryName(args[0])!;
            AssemblyLoadContext.Default.Resolving+=(_,name)=>{var path=Path.Combine(app,name.Name+".dll");return File.Exists(path)?AssemblyLoadContext.Default.LoadFromAssemblyPath(path):null;};
            Stage="load-candidate";Candidate=AssemblyLoadContext.Default.LoadFromAssemblyPath(args[0]);
            Stage="complete-model";
            var entityType=Candidate.GetType("MUnique.OpenMU.Persistence.EntityFramework.EntityDataContext",true)!;
            var complete=(IModel)entityType.GetProperty("CompleteModel",BindingFlags.NonPublic|BindingFlags.Static)!.GetValue(null)!;
            Stage="aggregate-method-metadata";
            AggregateMethods=AppDomain.CurrentDomain.GetAssemblies().Where(a=>a.GetName().Name!.StartsWith("MUnique.OpenMU",StringComparison.Ordinal)).SelectMany(a=>a.GetTypes()).SelectMany(t=>t.GetMethods(BindingFlags.Public|BindingFlags.NonPublic|BindingFlags.Static)).Where(m=>m.Name=="IsMemberOfAggregate" && !m.ContainsGenericParameters && m.ReturnType==typeof(bool) && m.GetParameters().Length==1).ToArray();
            Save("aggregate-methods.json",AggregateMethods.Select(m=>new{type=m.DeclaringType!.FullName,method=m.Name,argument=m.GetParameters()[0].ParameterType.FullName,assembly=m.DeclaringType.Assembly.GetName().Name}).ToArray());
            Stage="game-configuration-navigation";
            var game=complete.GetEntityTypes().Single(t=>t.ClrType.Name=="GameConfiguration");
            var entities=new Dictionary<string,object>();var edges=new List<object>();
            Walk(game,0,entities,new HashSet<string>(),edges);
            Save("game-navigation.json",new {modelType=complete.GetType().FullName,root=game.Name,maximumExpandedDepth=7,entities=entities.OrderBy(e=>e.Key).Select(e=>e.Value).ToArray(),edges});
            var typedType=Candidate.GetType("MUnique.OpenMU.Persistence.EntityFramework.TypedContext",true)!;
            Typed(typedType,complete,"PlugInConfiguration");Typed(typedType,complete,"SystemConfiguration");
            Save("result.json",new {status=Gaps.Count==0?"PASS_METADATA_EXPORTED":"PARTIAL_METADATA_EXPORTED",stage="complete",unresolved=Gaps.Distinct().ToArray(),queryBuilderInvoked=false,databaseApisInvoked=false,connectionEventsObserved=false,networkIsolationGuaranteed=false});
            return Gaps.Count==0?0:2;
        }
        catch(Exception ex)
        {
            var types=new List<string>();for(Exception? e=ex;e is not null;e=e.InnerException) types.Add(e.GetType().FullName!);
            Save("result.json",new {status="FAILED_SINGLE_ATTEMPT",stage=Stage,exceptionTypes=types,hresult=ex.HResult,message="omitted to avoid configuration/connection details",stack=ex.StackTrace,networkIsolationGuaranteed=false});
            return 1;
        }
    }
}
