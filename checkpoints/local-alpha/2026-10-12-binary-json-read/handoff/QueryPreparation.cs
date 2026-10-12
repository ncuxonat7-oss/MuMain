using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using System.Data;
using System.Data.Common;
using System.Diagnostics;
using System.Reflection;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Diagnostics;
using Microsoft.EntityFrameworkCore.Storage;
using Microsoft.Extensions.Logging.Abstractions;
using MUnique.OpenMU.Persistence;
using MUnique.OpenMU.Persistence.EntityFramework;
using MUnique.OpenMU.Persistence.EntityFramework.Json;
using MUnique.OpenMU.DataModel.Configuration;
using MUnique.OpenMU.PlugIns;
using Npgsql;

sealed class Guard : IObserver<DiagnosticListener>, IObserver<KeyValuePair<string,object?>>, IDisposable {
 public DbConnection? Allowed; public bool Opening; public string? Sql; public int Commands;
 readonly List<IDisposable> subs=new();
 public void OnNext(DiagnosticListener l){if(l.Name=="Microsoft.EntityFrameworkCore")subs.Add(l.Subscribe(this));}
 public void OnNext(KeyValuePair<string,object?> e){
  if(e.Key.EndsWith("ConnectionOpening") && e.Value is ConnectionEventData c){if(!Opening || !ReferenceEquals(c.Connection,Allowed))throw new InvalidOperationException("UNEXPECTED_CONNECTION");}
  if(e.Key.EndsWith("CommandExecuting") && e.Value is CommandEventData d){if(!ReferenceEquals(d.Command.Connection,Allowed)||Norm(d.Command.CommandText)!=Norm(Sql??""))throw new InvalidOperationException("UNREVIEWED_EF_COMMAND");Commands++;}
 }
 public static string Norm(string s)=>s.Trim().TrimEnd(';').Trim();
 public void OnError(Exception e){} public void OnCompleted(){} public void Dispose(){foreach(var x in subs)x.Dispose();}
}
static class ReadHarness {
 static string Root="",Stage="bootstrap";static Guard guard=new();static List<object> results=new();static JsonSerializerOptions json=new(){WriteIndented=true};
 static void Save(string name,object o)=>File.WriteAllText(Path.Combine(Root,"output",name),JsonSerializer.Serialize(o,json));
 static string Hash(string s)=>Convert.ToHexString(SHA256.HashData(Encoding.UTF8.GetBytes(s))).ToLowerInvariant();
 static DbContext Db(IContext c){for(Type? t=c.GetType();t!=null;t=t.BaseType){var p=t.GetProperty("Context",BindingFlags.Instance|BindingFlags.NonPublic|BindingFlags.DeclaredOnly);if(p!=null)return (DbContext)p.GetValue(c)!;}throw new InvalidOperationException("CONTEXT_PROPERTY_MISSING");}
 static string Query<T>(DbContext db,bool game) where T:class {
  var entity=db.Model.GetEntityTypes().Single(t=>typeof(T).IsAssignableFrom(t.ClrType));
  if(game)return "SET LOCAL jit = off;"+Environment.NewLine+new GameConfigurationJsonQueryBuilder().BuildJsonQueryForEntity(entity);
  var set=typeof(DbContext).GetMethods().Single(m=>m.Name=="Set"&&m.IsGenericMethod&&m.GetParameters().Length==0).MakeGenericMethod(entity.ClrType).Invoke(db,null);
  return ((System.Linq.IQueryable)set!).ToQueryString();
 }
 static async Task<object> Identity(DbConnection c,DbTransaction tx){await using var cmd=c.CreateCommand();cmd.Transaction=tx;cmd.CommandText="SELECT current_user,session_user,current_database(),current_setting('transaction_read_only'),current_setting('listen_addresses')";await using var rd=await cmd.ExecuteReaderAsync();await rd.ReadAsync();var a=Enumerable.Range(0,5).Select(rd.GetString).ToArray();return new{role=a[0],sessionUser=a[1],database=a[2],readOnly=a[3],listenAddresses=a[4]};}
 static async Task Read<T>(PersistenceContextProvider provider,string name,string role,bool game,bool prepare) where T:class {
  Stage=name+":context";using var context=game?provider.CreateNewContext():provider.CreateNewTypedContext(typeof(T),false);
  var db=Db(context);var sql=Query<T>(db,game);var queryFile=Path.Combine(Root,"output",name+".sql");
  if(prepare){File.WriteAllText(queryFile,sql);results.Add(new{name,status="QUERY_PREPARED",sha256=Hash(sql)});return;}
  if(!File.Exists(Path.Combine(Root,"review-approved.json"))||File.ReadAllText(queryFile)!=sql)throw new InvalidOperationException("QUERY_REVIEW_MISSING_OR_MISMATCH");
  var c=db.Database.GetDbConnection();var cs=new NpgsqlConnectionStringBuilder(c.ConnectionString);
  if(cs.Host!=Path.Combine(Root,"socket")||cs.Port!=55432||cs.Database!="scoped_reads"||cs.Username!="agent"||cs.Pooling||cs.Options!="-c default_transaction_read_only=on")throw new InvalidOperationException("CONNECTION_TARGET_REJECTED");
  guard.Allowed=c;guard.Sql=sql;guard.Commands=0;int opens=0;c.StateChange+=(o,e)=>{if(e.CurrentState==ConnectionState.Open && ++opens!=1)throw new InvalidOperationException("REOPEN_REJECTED");};
  Stage=name+":open";guard.Opening=true;try{await db.Database.OpenConnectionAsync();}finally{guard.Opening=false;}
  await using var tx=await db.Database.BeginTransactionAsync();var native=tx.GetDbTransaction();
  try{
   await using(var identity=c.CreateCommand()){identity.Transaction=native;identity.CommandText="SELECT current_setting('data_directory')";if((string?)await identity.ExecuteScalarAsync()!=Path.Combine(Root,"pgdata"))throw new InvalidOperationException("CLUSTER_IDENTITY_REJECTED");}
   await using(var cmd=c.CreateCommand()){cmd.Transaction=native;cmd.CommandText="SET TRANSACTION READ ONLY; SET LOCAL ROLE \""+role+"\"; SET LOCAL statement_timeout='60s'; SET LOCAL lock_timeout='1s'; SET LOCAL search_path=pg_catalog;";await cmd.ExecuteNonQueryAsync();}
   var before=await Identity(c,native);var b=JsonSerializer.SerializeToElement(before);if(b.GetProperty("role").GetString()!=role||b.GetProperty("database").GetString()!="scoped_reads"||b.GetProperty("readOnly").GetString()!="on"||b.GetProperty("listenAddresses").GetString()!="")throw new InvalidOperationException("SESSION_IDENTITY_REJECTED");
   Stage=name+":candidate-read";var data=(await context.GetAsync<T>(default)).ToList();
   var ids=data.Select(o=>o.GetType().GetProperty("Id")?.GetValue(o)?.ToString()??throw new InvalidOperationException("ROOT_ID_UNAVAILABLE")).OrderBy(x=>x,StringComparer.Ordinal).ToArray();
   var after=await Identity(c,native);if(JsonSerializer.Serialize(before)!=JsonSerializer.Serialize(after))throw new InvalidOperationException("SESSION_CHANGED");
   results.Add(new{name,status="PASS",rootCount=data.Count,rootIdSetSha256=Hash(string.Join("\n",ids)),hashScope="sorted materialized root identifiers only; no values output",querySha256=Hash(sql),roleIdentity=after,opens,efCommandsObserved=guard.Commands,rawJsonCommandSourceReviewed=game});
  }finally{await tx.RollbackAsync();await db.Database.CloseConnectionAsync();guard.Allowed=null;guard.Sql=null;Save("read-results.json",results);}
 }
 public static async Task<int> Main(string[] args){Root=args[0];bool prepare=args[1]=="prepare";using var sub=DiagnosticListener.AllListeners.Subscribe(guard);try{
   var provider=new PersistenceContextProvider(NullLoggerFactory.Instance,null);
   await Read<GameConfiguration>(provider,"game","entity_read_probe",true,prepare);
   await Read<PlugInConfiguration>(provider,"plugin","typed_read_probe",false,prepare);
   await Read<SystemConfiguration>(provider,"system","typed_read_probe",false,prepare);
   Save(prepare?"prepare-result.json":"harness-result.json",new{status="PASS",mode=args[1],results,networkIsolationGuaranteed=false});return 0;
  }catch(Exception ex){var chain=new List<string>();string? state=null;for(Exception? e=ex;e!=null;e=e.InnerException){chain.Add(e.GetType().FullName!);if(e is PostgresException p)state=p.SqlState;}
   Save(prepare?"prepare-result.json":"harness-result.json",new{status="FAIL",mode=args[1],stage=Stage,exceptionTypes=chain,sqlState=state,message="omitted",results});return 1;
  }finally{guard.Dispose();}}
}
