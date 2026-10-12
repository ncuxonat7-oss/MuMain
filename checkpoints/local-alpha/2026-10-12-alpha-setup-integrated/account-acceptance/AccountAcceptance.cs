using System;
using System.Collections.Generic;
using System.Data;
using System.Data.Common;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using System.Text.RegularExpressions;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Diagnostics;
using Microsoft.EntityFrameworkCore.Metadata;
using Microsoft.EntityFrameworkCore.Storage;
using Microsoft.Extensions.Logging.Abstractions;
using MUnique.OpenMU.Persistence;
using MUnique.OpenMU.Persistence.EntityFramework;
using MUnique.OpenMU.Persistence.EntityFramework.Json;
using Npgsql;
using GameConfiguration = MUnique.OpenMU.DataModel.Configuration.GameConfiguration;
using Account = MUnique.OpenMU.DataModel.Entities.Account;

sealed class AcceptanceStop : Exception { public AcceptanceStop(string reason) : base(reason) { } }

sealed class CommandGuard : IObserver<DiagnosticListener>, IObserver<KeyValuePair<string,object?>>, IDisposable
{
    readonly List<IDisposable> subscriptions = new();
    public DbConnection? Allowed;
    public DbTransaction? Transaction;
    public bool Opening, Cleanup, Beginning, Saving;
    public int SaveCommands;
    public Guid CharacterId;
    public byte Position;
    public readonly List<object> Commands = new();
    public readonly CancellationTokenSource Cancellation = new();
    public void OnNext(DiagnosticListener listener) { if (listener.Name == "Microsoft.EntityFrameworkCore") subscriptions.Add(listener.Subscribe(this)); }
    public void OnNext(KeyValuePair<string,object?> item)
    {
        if (item.Key.EndsWith("CommandError")) Cancellation.Cancel();
        if (item.Key.EndsWith("TransactionCommitting")) throw new AcceptanceStop("COMMIT_FORBIDDEN");
        if (item.Key.EndsWith("TransactionStarting") && !Beginning) throw new AcceptanceStop("UNEXPECTED_TRANSACTION");
        if (item.Key.EndsWith("ConnectionOpening") && item.Value is ConnectionEventData connection &&
            (!Opening || !ReferenceEquals(connection.Connection, Allowed))) throw new AcceptanceStop("UNEXPECTED_CONNECTION");
        if (item.Key.EndsWith("ConnectionClosing") && !Cleanup) throw new AcceptanceStop("PREMATURE_CONNECTION_CLOSE");
        if (!item.Key.EndsWith("CommandExecuting") || item.Value is not CommandEventData data) return;
        string shape = Regex.Replace(data.Command.CommandText, @"\s+", " ").Trim();
        bool syntax = Regex.IsMatch(shape, "^UPDATE data\\.\"Character\" SET \"PositionX\" = @([A-Za-z0-9_]+) WHERE \"Id\" = @([A-Za-z0-9_]+)(?: RETURNING 1)?;$");
        bool parameters = data.Command.Parameters.Count == 2 && data.Command.Parameters.Cast<DbParameter>().Any(p => p.Value is Guid id && id == CharacterId) &&
            data.Command.Parameters.Cast<DbParameter>().Any(p => p.Value is not Guid && Convert.ToInt32(p.Value) == Position);
        if (!Saving || ++SaveCommands != 1 || !syntax || !parameters || !ReferenceEquals(data.Command.Connection, Allowed) ||
            !ReferenceEquals(data.Command.Transaction, Transaction)) throw new AcceptanceStop("UNEXPECTED_EF_COMMAND");
        Commands.Add(new { shape, parameterTypes = data.Command.Parameters.Cast<DbParameter>().Select(p => p.DbType.ToString()).ToArray(), values = "omitted" });
    }
    public void OnError(Exception error) { } public void OnCompleted() { }
    public void Dispose() { foreach (var subscription in subscriptions) subscription.Dispose(); Cancellation.Dispose(); }
}

static class AccountAcceptance
{
    static string Root = "", Stage = "bootstrap";
    static readonly Dictionary<string,object?> Result = new() { ["status"] = "FAIL", ["accountLoadAttempts"] = 0, ["saveAttempts"] = 0, ["launchEnabled"] = false };
    static readonly CommandGuard Guard = new();
    static void Require(bool condition, string name) { if (!condition) throw new AcceptanceStop(name); }
    static string Hash(string value) => Convert.ToHexString(SHA256.HashData(Encoding.UTF8.GetBytes(value))).ToLowerInvariant();
    static void Save() => File.WriteAllText(Path.Combine(Root,"output","result.json"), JsonSerializer.Serialize(Result, new JsonSerializerOptions { WriteIndented = true }));
    static DbContext Db(IContext context)
    {
        for (Type? type=context.GetType(); type!=null; type=type.BaseType)
            if (type.GetProperty("Context",BindingFlags.Instance|BindingFlags.NonPublic|BindingFlags.DeclaredOnly) is { } property) return (DbContext)property.GetValue(context)!;
        throw new AcceptanceStop("CONTEXT_UNAVAILABLE");
    }
    static IModel CompleteModel() => (IModel)typeof(PersistenceContextProvider).Assembly.GetType("MUnique.OpenMU.Persistence.EntityFramework.EntityDataContext")!
        .GetProperty("CompleteModel",BindingFlags.Static|BindingFlags.Public|BindingFlags.NonPublic)!.GetValue(null)!;
    static string AccountQuery()
    {
        var type = CompleteModel().GetEntityTypes().Single(t => typeof(Account).IsAssignableFrom(t.ClrType));
        return "SET LOCAL jit = off;" + Environment.NewLine + new JsonQueryBuilder().BuildJsonQueryForEntity(type) + " where result.\"Id\" = @id;";
    }
    static string GameQuery(DbContext context)
    {
        var type=context.Model.GetEntityTypes().Single(t=>typeof(GameConfiguration).IsAssignableFrom(t.ClrType));
        return "SET LOCAL jit = off;" + Environment.NewLine + new GameConfigurationJsonQueryBuilder().BuildJsonQueryForEntity(type);
    }
    static async Task<object?> Scalar(DbConnection connection, DbTransaction? transaction, string sql, Guid? id=null)
    {
        await using var command=connection.CreateCommand(); command.Transaction=transaction; command.CommandText=sql;
        if (id.HasValue) { var parameter=command.CreateParameter();parameter.ParameterName="id";parameter.Value=id.Value;command.Parameters.Add(parameter); }
        return await command.ExecuteScalarAsync(Guard.Cancellation.Token);
    }
    static async Task Identity(DbContext context, IDbContextTransaction transaction, string role)
    {
        var native=transaction.GetDbTransaction(); var connection=context.Database.GetDbConnection();
        var sql="SELECT current_user=session_user AND current_user='"+role+"' AND current_database()='alpha_role_probe' AND current_setting('listen_addresses')=''";
        Require((bool)(await Scalar(connection,native,sql))!,"IDENTITY_REJECTED");
        Result[role+"Identity"]=new { role, sessionUser=role, database="alpha_role_probe", tcp=false };
    }
    static async Task Open(DbContext context, string role)
    {
        var connection=context.Database.GetDbConnection();var cs=new NpgsqlConnectionStringBuilder(connection.ConnectionString);
        Require(cs.Host==Path.GetDirectoryName(Root)+"/socket" && cs.Port==55433 && cs.Database=="alpha_role_probe" && cs.Username==role && !cs.Pooling,"TARGET_REJECTED");
        Require(!context.Database.CreateExecutionStrategy().RetriesOnFailure,"EF_RETRY_STRATEGY_REJECTED");
        Guard.Allowed=connection;Guard.Cleanup=false;Guard.Opening=true;
        try { await context.Database.OpenConnectionAsync(); } finally { Guard.Opening=false; }
    }
    static async Task<IDbContextTransaction> Begin(DbContext context)
    {
        Guard.Beginning=true;
        try { return await context.Database.BeginTransactionAsync(); } finally { Guard.Beginning=false; }
    }
    static async Task<GameConfiguration> Configuration(PersistenceContextProvider provider)
    {
        Stage="configuration-dependency";using var context=provider.CreateNewContext();var db=Db(context);
        Require(GameQuery(db)==File.ReadAllText(Path.Combine(Root,"output","game.sql")),"GAME_SQL_CHANGED");
        await Open(db,"alpha_entity");await using var transaction=await Begin(db);
        try {
            await Scalar(db.Database.GetDbConnection(),transaction.GetDbTransaction(),"SET TRANSACTION READ ONLY;");
            await Identity(db,transaction,"alpha_entity");
            Result["configurationDependencyReads"]=1;
            var configurations=(await context.GetAsync<GameConfiguration>(default)).ToList();
            Require(configurations.Count==1,"CONFIGURATION_COUNT");return configurations[0];
        } finally { await transaction.RollbackAsync();Guard.Cleanup=true;await db.Database.CloseConnectionAsync(); }
    }
    static async Task Run(PersistenceContextProvider provider)
    {
        var configuration=await Configuration(provider);
        Stage="account-context";using var context=provider.CreateNewPlayerContext(configuration);var db=Db(context);
        Require(AccountQuery()==File.ReadAllText(Path.Combine(Root,"output","account.sql")),"ACCOUNT_SQL_CHANGED");
        await Open(db,"alpha_account");await using var transaction=await Begin(db);
        var native=transaction.GetDbTransaction();var connection=db.Database.GetDbConnection();Guard.Transaction=native;
        Guid characterId=default;byte oldPosition=0;bool mutated=false;
        try {
            await Identity(db,transaction,"alpha_account");
            var xid=await Scalar(connection,native,"SELECT txid_current();");
            var id=(Guid?)await Scalar(connection,native,"SELECT a.\"Id\" FROM data.\"Account\" a WHERE NOT a.\"IsTemplate\" AND NOT a.\"IsBot\" AND EXISTS(SELECT 1 FROM data.\"Character\" c WHERE c.\"AccountId\"=a.\"Id\") ORDER BY a.\"Id\" LIMIT 1;");
            Require(id.HasValue,"NO_EXISTING_TEST_ACCOUNT");Stage="account-load";Result["accountLoadAttempts"]=1;
            var account=await context.GetByIdAsync<Account>(id!.Value);
            Require(account!=null && account.Characters.Count>0,"NO_EXISTING_CHARACTER");
            Require(ReferenceEquals(db.Database.CurrentTransaction,transaction) && connection.State==ConnectionState.Open,"LOAD_LOST_TRANSACTION");
            db.ChangeTracker.DetectChanges();Require(db.ChangeTracker.Entries().All(e=>e.State==EntityState.Unchanged),"LOAD_DIRTY_GRAPH");
            var character=account!.Characters.OrderBy(c=>c.Id).First();characterId=character.Id;oldPosition=character.PositionX;
            Guard.CharacterId=characterId;Guard.Position=(byte)((oldPosition+1)%256);
            Stage="mutation-preflight";character.PositionX=Guard.Position;db.ChangeTracker.DetectChanges();
            var changed=db.ChangeTracker.Entries().Where(e=>e.State!=EntityState.Unchanged).ToArray();
            Require(changed.Length==1 && ReferenceEquals(changed[0].Entity,character) && changed[0].State==EntityState.Modified &&
                changed[0].Properties.Where(p=>p.IsModified).Select(p=>p.Metadata.Name).SequenceEqual(new[]{"PositionX"}),"UNEXPECTED_TRACKED_CHANGE");
            Stage="real-save";Guard.Saving=true;Result["saveAttempts"]=1;
            try { Require(await context.SaveChangesAsync(Guard.Cancellation.Token),"SAVE_RETURNED_FALSE"); } finally { Guard.Saving=false; }
            Require(Guard.SaveCommands==1,"SAVE_COMMAND_COUNT");
            Require(ReferenceEquals(db.Database.CurrentTransaction,transaction) && Equals(xid,await Scalar(connection,native,"SELECT txid_current();")),"SAVE_LOST_TRANSACTION");
            Require(Convert.ToByte(await Scalar(connection,native,"SELECT \"PositionX\" FROM data.\"Character\" WHERE \"Id\"=@id;",characterId))==Guard.Position,"IN_TRANSACTION_VALUE_MISMATCH");
            mutated=true;Result["realSaveVerifiedInsideTransaction"]=true;
        } finally {
            Stage+="/rollback";await transaction.RollbackAsync();Result["rollbackCompleted"]=true;Guard.Cleanup=true;
            if(mutated) Require(Convert.ToByte(await Scalar(connection,null,"SELECT \"PositionX\" FROM data.\"Character\" WHERE \"Id\"=@id;",characterId))==oldPosition,"ROLLBACK_VALUE_MISMATCH");
            await db.Database.CloseConnectionAsync();
        }
        Result["status"]="PASS_ACCOUNT_LOAD_REAL_SAVE_ROLLBACK";
    }
    public static async Task<int> Main(string[] args)
    {
        Root=args[0];using var subscription=DiagnosticListener.AllListeners.Subscribe(Guard);
        try {
            var provider=new PersistenceContextProvider(NullLoggerFactory.Instance,null);
            if(args[1]=="prepare") {
                using var context=provider.CreateNewContext();
                File.WriteAllText(Path.Combine(Root,"output","game.sql"),GameQuery(Db(context)));
                File.WriteAllText(Path.Combine(Root,"output","account.sql"),AccountQuery());
                Result["status"]="PREPARED_OFFLINE";return 0;
            }
            Require(args[1]=="run" && File.Exists(Path.Combine(Root,"review-approved.json")),"REVIEW_REQUIRED");
            await Run(provider);return 0;
        } catch(Exception error) {
            Result["stage"]=Stage;var details=new List<object>();
            for(Exception? e=error;e!=null;e=e.InnerException) details.Add(new { type=e.GetType().FullName,
                guardReason=e is AcceptanceStop?e.Message:null, sqlState=(e as PostgresException)?.SqlState,
                frames=(new StackTrace(e,false).GetFrames()??Array.Empty<StackFrame>()).Select(f=>new { type=f.GetMethod()?.DeclaringType?.FullName, method=f.GetMethod()?.Name }).ToArray(),message="omitted" });
            Result["exceptions"]=details;return 1;
        } finally { Result["observedEfCommands"]=Guard.Commands;Save();Guard.Dispose(); }
    }
}
