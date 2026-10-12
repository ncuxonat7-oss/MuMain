from pathlib import Path
import hashlib,json,os,subprocess,time

ROOT=Path(__file__).parent
STAGE=ROOT.parent
OLD=Path('/workspace/openmu-single-read-20261012')
PG=Path('/workspace/mumain-tools/postgresql-17.11/usr/lib/postgresql/17/bin')
DOT=Path('/workspace/mumain-tools/dotnet-10.0.401')
DATA=STAGE/'pgdata'
ENV={'PATH':'/usr/bin:/bin','HOME':str(ROOT/'home'),'LANG':'C','TZ':'UTC','PGHOST':str(STAGE/'socket'),'PGPORT':'55433','PGDATABASE':'alpha_role_probe','PGUSER':'agent','PGCLIENTENCODING':'SQL_ASCII'}
report={'status':'FAIL','grantApplied':False,'runnerInvocations':0,'launchEnabled':False}
def utility(name,args):
    p=subprocess.run([str(PG/name),*args],env=ENV,capture_output=True,timeout=120)
    if p.returncode:raise RuntimeError(name+'_exit_'+str(p.returncode))
    return p.stdout
def query(sql):return utility('psql',['-X','-qAt','-v','ON_ERROR_STOP=1','-c',sql]).decode().strip()
def snapshot():
    data=utility('pg_dump',['--data-only','--no-owner','--no-privileges'])
    return hashlib.sha256(b'\n'.join(x for x in data.splitlines() if not x.startswith((b'\\restrict ',b'\\unrestrict ')))).hexdigest()
started=time.monotonic()
try:
    assert DATA.exists() and not (DATA/'postmaster.pid').exists()
    assert hashlib.sha256((ROOT/'app/AccountAcceptance.dll').read_bytes()).hexdigest()=='fcb3db8b19f58e0a99cda1c87925081487bc6a99a3a4a45e88365cbe435f4d4a'
    assert hashlib.sha256((ROOT/'app/MUnique.OpenMU.Persistence.EntityFramework.dll').read_bytes()).hexdigest()=='67adf087ec8f0d3de395740f0ce09e8040777698085747fdb23d89fee4f393a1'
    utility('pg_ctl',['-D',str(DATA),'-l',str(ROOT/'postgres-run.log'),'-w','start'])
    assert query("SELECT current_setting('data_directory')='"+str(DATA)+"' AND current_setting('listen_addresses')='' AND current_database()='alpha_role_probe'")=='t'
    report['beforeDataSha256']=snapshot()
    report['approvedGrantAlreadyPresent']=True
    assert query("SELECT count(*)=2 AND bool_and(has_column_privilege('alpha_account',c.oid,a.attnum,'SELECT') AND NOT has_column_privilege('alpha_account',c.oid,a.attnum,'INSERT,UPDATE,REFERENCES')) AND NOT bool_or(has_table_privilege('alpha_account',c.oid,'SELECT,INSERT,UPDATE,DELETE,TRUNCATE,TRIGGER,REFERENCES')) FROM pg_attribute a JOIN pg_class c ON c.oid=a.attrelid JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='data' AND c.relname='AccountCharacterClass' AND a.attnum>0 AND NOT a.attisdropped AND a.attname IN ('AccountId','CharacterClassId')")=='t'
    report['exactTwoColumnGrantVerified']=True
    report['newGrantChanges']=False
    env={'PATH':'/usr/bin:/bin','DOTNET_ROOT':str(DOT),'HOME':str(ROOT/'home'),'DOTNET_CLI_HOME':str(ROOT/'home'),'DOTNET_CLI_TELEMETRY_OPTOUT':'1','DOTNET_NOLOGO':'1','DOTNET_GENERATE_ASPNET_CERTIFICATE':'false','DOTNET_EnableDiagnostics':'0','TMPDIR':str(ROOT/'tmp')}
    args=[str(DOT/'dotnet'),'exec','--depsfile',str(ROOT/'app/MUnique.OpenMU.Persistence.EntityFramework.deps.json'),'--runtimeconfig',str(ROOT/'app/MUnique.OpenMU.Persistence.EntityFramework.runtimeconfig.json'),str(ROOT/'app/AccountAcceptance.dll'),str(ROOT),'run']
    (ROOT/'run-invocation.json').write_text(json.dumps({'argv':args,'environment':env},indent=2)+'\n')
    report['runnerInvocations']=1
    p=subprocess.run(args,env=env,cwd=ROOT,capture_output=True,timeout=120)
    (ROOT/'run.stdout').write_bytes(p.stdout);(ROOT/'run.stderr').write_bytes(p.stderr)
    report['runnerExitCode']=p.returncode
    report['runnerResult']=json.loads((ROOT/'output/result.json').read_text())
    report['afterDataSha256']=snapshot()
    report['dataUnchanged']=report['beforeDataSha256']==report['afterDataSha256']
    if p.returncode:raise RuntimeError('first_runner_failure_no_retry')
    assert report['dataUnchanged']
    report['status']='PASS_REAL_ACCOUNT_LOAD_SAVE_ROLLBACK'
except Exception as error:report['error']=str(error)
finally:
    if (DATA/'postmaster.pid').exists():
        try:(ROOT/'shutdown-run.log').write_bytes(utility('pg_ctl',['-D',str(DATA),'-m','fast','-w','stop']))
        except Exception as error:report['shutdownError']=str(error)
    p=subprocess.run([str(PG/'pg_ctl'),'-D',str(DATA),'status'],env=ENV,capture_output=True)
    (ROOT/'shutdown-run-status.txt').write_bytes(p.stdout+p.stderr)
    report['shutdown']={'statusExit':p.returncode,'pidAbsent':not (DATA/'postmaster.pid').exists(),'socketAbsent':not (STAGE/'socket/.s.PGSQL.55433').exists()}
    prior=json.loads((STAGE/'prior-tree-preservation-before.json').read_text())
    changed=[name for name,sha in prior.items() if not (OLD/name).is_file() or hashlib.sha256((OLD/name).read_bytes()).hexdigest()!=sha]
    report['priorSingleReadPreservation']={'filesChecked':len(prior),'changedPaths':changed}
    report['candidateDllSha256']=hashlib.sha256((ROOT/'app/MUnique.OpenMU.Persistence.EntityFramework.dll').read_bytes()).hexdigest()
    report['elapsedSeconds']=round(time.monotonic()-started,2)
    (ROOT/'repaired-execution-results.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
