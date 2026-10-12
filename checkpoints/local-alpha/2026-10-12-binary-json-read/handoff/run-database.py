from pathlib import Path
import subprocess,os,json,hashlib,re,time
r=Path(__file__).parent;pg=Path('/workspace/mumain-tools/postgresql-17.11/usr/lib/postgresql/17/bin');base=Path(os.environ['HANDOFF_INPUT_ROOT']).resolve();contract=json.loads((r/'read-contract.json').read_text());cluster=r/'pgdata';sock=r/'socket';start=time.monotonic()
env={'PATH':'/usr/bin:/bin','HOME':str(r/'home'),'PGHOST':str(sock),'PGPORT':'55432','PGDATABASE':'scoped_reads','PGUSER':'agent','PGCLIENTENCODING':'SQL_ASCII','LANG':'C','TZ':'UTC'}
report={'status':'FAIL','stage':'preflight','checks':{},'candidateReadAttempts':0,'shutdown':'NOT_STARTED','networkIsolationGuaranteed':False}
def run(tool,args,log=None):
 p=subprocess.run([str(pg/tool),*args],env=env,capture_output=True,timeout=120)
 if log:(r/log).write_bytes(p.stdout+p.stderr)
 if p.returncode:
  (r/'first-failure.stderr').write_bytes(p.stderr)
  raise RuntimeError(tool+':exit='+str(p.returncode))
 return p.stdout.decode()
def q(sql):return run('psql',['-X','-A','-t','-v','ON_ERROR_STOP=1','-c',sql]).strip()
def jq(sql):return json.loads(q(sql))
def check(n,b):
 report['checks'][n]='PASS' if b else 'FAIL'
 if not b:raise RuntimeError(n)
def snap():
 b=run('pg_dump',['--data-only','--no-owner','--no-privileges']).encode();b=b'\n'.join(x for x in b.splitlines() if not x.startswith((b'\\restrict ',b'\\unrestrict ')));return hashlib.sha256(b).hexdigest()
def normalize(s):return '\n'.join(x for x in s.splitlines() if not x.startswith(('\\restrict ','\\unrestrict ')))
try:
 check('new_private_cluster_path',not cluster.exists())
 check('review_gate',json.loads((r/'review-approved.json').read_text())['status']=='PASS_REVIEWED_BEFORE_DB_EXECUTION')
 for p,sha in [(base/'baseline/gameplay-test-db.dump','0a4b0744cb9be77c8f53a6f4a73e729402d17382069ba93261d394cbadf19478'),(base/'github-actions-artifact-11651520969.zip','b40fbdbdb5c3bd9630331e0b9cb3bc7c1860db041a928bb976555635e03f79ea'),(r/'app/MUnique.OpenMU.Persistence.EntityFramework.dll','67adf087ec8f0d3de395740f0ce09e8040777698085747fdb23d89fee4f393a1')]:check('sha256:'+p.name,hashlib.sha256(p.read_bytes()).hexdigest()==sha)
 s=run('pg_restore',['--schema-only','--no-owner','--no-privileges','--file=-',str(base/'baseline/gameplay-test-db.dump')]);(r/'restored-schema-review.sql').write_text(s)
 # Fresh verified archive extraction: old baseline-schema.sql is not required in this handoff.
 check('no_executable_objects',not re.search(r'CREATE (?:OR REPLACE )?(?:FUNCTION|PROCEDURE|TRIGGER|RULE|POLICY|EXTENSION|SERVER|FOREIGN|EVENT)|SECURITY DEFINER|ENABLE ROW LEVEL',s,re.I))
 defaults=[]
 for line in s.splitlines():
  if ' DEFAULT ' in line:
   expr=line.split(' DEFAULT ',1)[1].removesuffix(',').removesuffix(' NOT NULL');defaults.append(expr)
 check('constant_defaults_only',all(re.fullmatch(r"(?:-?\d+(?:\.\d+)?|true|false|'(?:[^']|'')*'::(?:text|interval|boolean|integer|real|double precision|character varying|uuid))",x) for x in defaults))
 report['stage']='initialize';run('initdb',['-D',str(cluster),'--encoding=SQL_ASCII','--locale=C','--auth-local=peer','--auth-host=reject'],'initdb.log')
 with (cluster/'postgresql.conf').open('a') as f:f.write("\nlisten_addresses = ''\nunix_socket_directories = '"+str(sock)+"'\nunix_socket_permissions = 0700\nport = 55432\n")
 report['stage']='start';run('pg_ctl',['-D',str(cluster),'-l',str(r/'postgres.log'),'-w','start'],'pg-start.log');report['shutdown']='REQUIRED'
 run('createdb',['--maintenance-db=postgres','--encoding=SQL_ASCII','--locale=C','--template=template0','scoped_reads'],'createdb.log')
 check('cluster_identity',q("SELECT current_user='agent' AND current_database()='scoped_reads' AND current_setting('data_directory')='"+str(cluster)+"' AND current_setting('listen_addresses')='' AND current_setting('server_encoding')='SQL_ASCII' AND (SELECT datcollate='C' AND datctype='C' FROM pg_database WHERE datname=current_database())")=='t')
 check('peer_only',q("SELECT count(*)=0 FROM pg_hba_file_rules WHERE (type='local' AND auth_method<>'peer') OR (type<>'local' AND auth_method<>'reject') OR error IS NOT NULL")=='t')
 report['stage']='restore';run('pg_restore',['--exit-on-error','--no-owner','--no-privileges','--dbname=scoped_reads',str(base/'baseline/gameplay-test-db.dump')],'restore.log')
 check('ordinary_tables_no_rls',q("SELECT bool_and(relkind='r' AND NOT relrowsecurity AND NOT relforcerowsecurity) FROM pg_class WHERE relnamespace IN (SELECT oid FROM pg_namespace WHERE nspname IN ('config','data','friend','guild','public')) AND relkind IN ('r','p','v','m','f')")=='t')
 check('no_user_executable_paths',q("SELECT NOT EXISTS(SELECT FROM pg_proc WHERE pronamespace IN (SELECT oid FROM pg_namespace WHERE nspname IN ('config','data','friend','guild','public'))) AND NOT EXISTS(SELECT FROM pg_trigger WHERE NOT tgisinternal) AND NOT EXISTS(SELECT FROM pg_policy) AND NOT EXISTS(SELECT FROM pg_rewrite WHERE ev_class IN (SELECT c.oid FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname IN ('config','data','friend','guild','public'))) AND NOT EXISTS(SELECT FROM pg_constraint WHERE contype='c' AND connamespace IN (SELECT oid FROM pg_namespace WHERE nspname IN ('config','data','friend','guild','public')))")=='t')
 actual=jq("SELECT json_agg(t) FROM (SELECT n.nspname schema,c.relname tab,a.attname col FROM pg_attribute a JOIN pg_class c ON c.oid=a.attrelid JOIN pg_namespace n ON n.oid=c.relnamespace WHERE a.attnum>0 AND NOT a.attisdropped AND c.relkind='r' AND n.nspname IN ('config','data'))t")
 physical={}
 for x in actual:physical.setdefault(x['schema']+'.'+x['tab'],set()).add(x['col'])
 check('live_projection_columns',all(set(x['selectColumns'])<=physical[x['table']] and (x['basis']!='fullRowProjectionTables' or set(x['selectColumns'])==physical[x['table']]) for x in contract['entries']))
 report['stage']='roles_and_column_grants';sql=''
 for role in ['entity_read_probe','typed_read_probe']:sql+='CREATE ROLE '+role+' NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS;\n'
 sql+='REVOKE ALL ON DATABASE scoped_reads FROM PUBLIC;\nGRANT CONNECT ON DATABASE scoped_reads TO entity_read_probe,typed_read_probe;\nREVOKE ALL ON SCHEMA public,config,data,friend,guild FROM PUBLIC;\n'
 sql+=(r/'prepared-read-grants.sql').read_text().replace(':"entity_role"','"entity_read_probe"').replace(':"typed_role"','"typed_read_probe"');(r/'applied-read-grants.sql').write_text(sql);run('psql',['-X','-v','ON_ERROR_STOP=1','-f',str(r/'applied-read-grants.sql')],'grants.log')
 check('role_attributes',q("SELECT count(*)=2 AND bool_and(NOT(rolsuper OR rolcanlogin OR rolcreatedb OR rolcreaterole OR rolreplication OR rolbypassrls)) FROM pg_roles WHERE rolname IN ('entity_read_probe','typed_read_probe')")=='t')
 check('no_membership_or_ownership',q("SELECT NOT EXISTS(SELECT FROM pg_auth_members WHERE member IN (SELECT oid FROM pg_roles WHERE rolname IN ('entity_read_probe','typed_read_probe'))) AND NOT EXISTS(SELECT FROM pg_shdepend WHERE refclassid='pg_authid'::regclass AND refobjid IN (SELECT oid FROM pg_roles WHERE rolname IN ('entity_read_probe','typed_read_probe')) AND deptype='o')")=='t')
 for role,param in [('entity_read_probe','entity_role'),('typed_read_probe','typed_role')]:
  check(role+':no_create_temp',q("SELECT NOT has_database_privilege('"+role+"',current_database(),'CREATE,TEMP') AND NOT EXISTS(SELECT FROM pg_namespace WHERE has_schema_privilege('"+role+"',oid,'CREATE'))")=='t')
  acl=jq("SELECT json_agg(t) FROM (SELECT n.nspname schema,c.relname tab,a.attname col,has_column_privilege('"+role+"',c.oid,a.attnum,'SELECT') sel,has_column_privilege('"+role+"',c.oid,a.attnum,'INSERT,UPDATE,REFERENCES') wr,has_table_privilege('"+role+"',c.oid,'INSERT,UPDATE,DELETE,TRUNCATE,REFERENCES,TRIGGER') tw FROM pg_attribute a JOIN pg_class c ON c.oid=a.attrelid JOIN pg_namespace n ON n.oid=c.relnamespace WHERE a.attnum>0 AND NOT a.attisdropped AND c.relkind='r' AND n.nspname IN ('config','data','friend','guild','public'))t")
  wanted={(x['table'],col) for x in contract['entries'] if x['roleParameter']==param for col in x['selectColumns']};observed={(x['schema']+'.'+x['tab'],x['col']) for x in acl if x['sel']};check(role+':exact_columns_no_writes',wanted==observed and not any(x['wr'] or x['tw'] for x in acl));report[role]={'selectedColumnPrivileges':len(observed),'exactMatch':True}
 report['beforeDataSha256']=snap();report['stage']='candidate_reads';report['candidateReadAttempts']=1
 p=subprocess.run(['/usr/bin/python3',str(r/'invoke.py'),'run'],cwd=r,capture_output=True,timeout=200);(r/'harness-run-driver.log').write_bytes(p.stdout+p.stderr);report['harnessExitCode']=p.returncode
 if (r/'output/harness-result.json').exists():report['candidate']=json.loads((r/'output/harness-result.json').read_text())
 if p.returncode:raise RuntimeError('candidate_first_error_no_retry')
 report['afterDataSha256']=snap();check('restored_data_unchanged',report['beforeDataSha256']==report['afterDataSha256']);report['status']='PASS_SELECTED_READS_ONLY'
except Exception as e:report['error']=str(e)
finally:
 if (cluster/'postmaster.pid').exists():
  try:run('pg_ctl',['-D',str(cluster),'-m','fast','-w','stop'],'shutdown.log')
  except Exception as e:report['shutdownError']=str(e)
 if cluster.exists():
  p=subprocess.run([str(pg/'pg_ctl'),'-D',str(cluster),'status'],env=env,capture_output=True);(r/'shutdown-status.log').write_bytes(p.stdout+p.stderr);report['shutdown']={'statusExit':p.returncode,'pidAbsent':not (cluster/'postmaster.pid').exists(),'socketAbsent':not (sock/'.s.PGSQL.55432').exists()}
 report['elapsedSeconds']=round(time.monotonic()-start,2);(r/'database-results.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
