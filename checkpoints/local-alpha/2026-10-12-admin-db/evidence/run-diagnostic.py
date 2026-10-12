from pathlib import Path
import subprocess,os,json,hashlib,re,time
r=Path(__file__).parent; pg=Path('/workspace/mumain-tools/postgresql-17.11/usr/lib/postgresql/17/bin'); cluster=r/'pgdata'; sock=r/'socket';sock.mkdir(mode=0o700)
env={k:v for k,v in os.environ.items() if not k.startswith('PG')};env.update(PGHOST=str(sock),PGPORT='55432',PGDATABASE='admin_diagnostic',PGUSER='agent',PGCLIENTENCODING='SQL_ASCII')
report={'result':'FAIL','stage':'review','tests':{},'limits':['Entity/Typed complete permission closure BLOCKED','Windows readiness NOT RUN','Complete Alpha readiness NOT RUN'],'started':time.time()}
def run(tool,args,log=None,input=None):
 p=subprocess.run([str(pg/tool),*args],env=env,input=input,capture_output=True); 
 if log:(r/log).write_bytes(p.stdout+p.stderr)
 if p.returncode:raise RuntimeError(f'{tool} exit {p.returncode}; stage {report["stage"]}; see {log or "private command output"}')
 return p.stdout.decode('utf-8')
def query(sql):return run('psql',['-X','-A','-t','-v','ON_ERROR_STOP=1','-c',sql]).strip()
def jsonq(sql):return json.loads(query(sql))
def check(name,condition):
 report['tests'][name]='PASS' if condition else 'FAIL'
 if not condition:raise RuntimeError(name)
def snapshot():
 data=run('pg_dump',['--data-only','--no-owner','--no-privileges','--exclude-schema=admin']).encode()
 data=b'\n'.join(x for x in data.splitlines() if not x.startswith((b'\\restrict ',b'\\unrestrict ')))
 return hashlib.sha256(data).hexdigest()
try:
 s=(r/'baseline-schema.sql').read_text();check('baseline_no_executable_objects',not re.search(r'CREATE (?:OR REPLACE )?(?:FUNCTION|PROCEDURE|TRIGGER|RULE|POLICY|EXTENSION|SERVER|FOREIGN)|SECURITY DEFINER|ENABLE ROW LEVEL|CREATE EVENT',s,re.I))
 # All baseline defaults were reviewed as constants; no custom executable objects.
 a=(r/'admin-official.sql').read_text(encoding='utf-8-sig');check('admin_sql_scope',len(re.findall('CREATE TABLE',a))==3 and len(re.findall('CREATE UNIQUE INDEX',a))==2 and len(re.findall('INSERT INTO',a))==2 and not re.search(r'CREATE (FUNCTION|PROCEDURE|TRIGGER|RULE|POLICY|EXTENSION)|COPY |ALTER |DELETE |UPDATE |GRANT ',a))
 report['stage']='initdb';run('initdb',['-D',str(cluster),'--encoding=SQL_ASCII','--locale=C','--auth-local=peer','--auth-host=reject'],'initdb.log')
 with (cluster/'postgresql.conf').open('a') as f:f.write("\nlisten_addresses = ''\nunix_socket_directories = '"+str(sock)+"'\nunix_socket_permissions = 0700\nport = 55432\n")
 report['stage']='start';run('pg_ctl',['-D',str(cluster),'-l',str(r/'postgres.log'),'-w','start'],'pg-start.log')
 run('createdb',['--maintenance-db=postgres','--encoding=SQL_ASCII','--locale=C','--template=template0','admin_diagnostic'],'createdb.log')
 check('cluster_identity',query("SELECT current_database()='admin_diagnostic' AND current_user='agent' AND current_setting('data_directory')='"+str(cluster)+"' AND current_setting('listen_addresses')='' AND current_setting('server_encoding')='SQL_ASCII' AND current_setting('lc_collate')='C'")=='t')
 check('peer_authentication',query("SELECT count(*)=0 FROM pg_hba_file_rules WHERE (type='local' AND auth_method<>'peer') OR (type<>'local' AND auth_method<>'reject') OR error IS NOT NULL")=='t')
 report['stage']='restore';run('pg_restore',['--exit-on-error','--no-owner','--no-privileges','-d','admin_diagnostic',str(r/'baseline/gameplay-test-db.dump')],'restore.log')
 contract=json.loads((r/'contracts/database-source-contract.json').read_text())
 def game():return jsonq('SELECT json_agg(t ORDER BY "MigrationId") FROM public."__EFMigrationsHistory" t')
 before=game();check('game_before_63_exact',sorted(x['MigrationId'] for x in before)==sorted(contract['migrationHistories']['EntityDataContext']['ids']))
 check('admin_absent_before',query("SELECT count(*)=0 FROM pg_namespace WHERE nspname='admin'")=='t')
 def config():return jsonq('SELECT json_build_object(\'game\',(SELECT json_agg("Id" ORDER BY "Id") FROM config."GameConfiguration"),\'system\',(SELECT json_agg(t) FROM (SELECT "Id","AutoStart","AutoUpdateSchema","ReadConsoleInput" FROM config."SystemConfiguration")t))')
 cfg=config();check('baseline_config_flags',cfg=={'game':['00000001-0001-0000-0000-000000000000'],'system':[{'Id':'00000010-0000-0000-0000-000000000000','AutoStart':True,'AutoUpdateSchema':True,'ReadConsoleInput':False}]})
 report['data_before_sha256']=snapshot()
 report['stage']='apply_admin_sql';run('psql',['-X','-v','ON_ERROR_STOP=1','-f',str(r/'admin-official.sql')],'apply-admin.log')
 admin=jsonq('SELECT json_agg(t ORDER BY "MigrationId") FROM admin."__EFMigrationsHistory" t');check('admin_2_exact', [x['MigrationId'] for x in admin]==contract['migrationHistories']['AdminAuth.AdminPanelContext']['ids'] and all(x['ProductVersion']=='10.0.2' for x in admin));report['admin_history']=admin
 report['stage']='grant_review';run('psql',['-X','-v','ON_ERROR_STOP=1','-f',str(r/'admin-grants.sql')],'grants.log')
 check('role_flags',query("SELECT NOT (rolcanlogin OR rolsuper OR rolcreatedb OR rolcreaterole OR rolreplication OR rolbypassrls) FROM pg_roles WHERE rolname='admin_probe'")=='t')
 check('no_memberships',query("SELECT count(*)=0 FROM pg_auth_members WHERE member=(SELECT oid FROM pg_roles WHERE rolname='admin_probe')")=='t')
 check('no_ownership',query("SELECT NOT EXISTS(SELECT FROM pg_class WHERE relowner=(SELECT oid FROM pg_roles WHERE rolname='admin_probe')) AND NOT EXISTS(SELECT FROM pg_namespace WHERE nspowner=(SELECT oid FROM pg_roles WHERE rolname='admin_probe')) AND NOT EXISTS(SELECT FROM pg_database WHERE datdba=(SELECT oid FROM pg_roles WHERE rolname='admin_probe'))")=='t')
 check('trusted_admin_tables',query("SELECT count(*)=3 AND bool_and(relkind='r' AND NOT relrowsecurity AND NOT relforcerowsecurity) FROM pg_class WHERE relnamespace='admin'::regnamespace AND relkind IN ('r','p','v','f')")=='t')
 check('no_admin_triggers_rules_policies_defaults_checks',query("SELECT NOT EXISTS(SELECT FROM pg_trigger WHERE tgrelid IN (SELECT oid FROM pg_class WHERE relnamespace='admin'::regnamespace) AND NOT tgisinternal) AND NOT EXISTS(SELECT FROM pg_rewrite WHERE ev_class IN (SELECT oid FROM pg_class WHERE relnamespace='admin'::regnamespace)) AND NOT EXISTS(SELECT FROM pg_policy WHERE polrelid IN (SELECT oid FROM pg_class WHERE relnamespace='admin'::regnamespace)) AND NOT EXISTS(SELECT FROM pg_attrdef WHERE adrelid IN (SELECT oid FROM pg_class WHERE relnamespace='admin'::regnamespace)) AND NOT EXISTS(SELECT FROM pg_constraint WHERE connamespace='admin'::regnamespace AND contype NOT IN ('p','u')) AND NOT EXISTS(SELECT FROM pg_proc WHERE pronamespace='admin'::regnamespace)")=='t')
 check('no_database_create_temp',query("SELECT NOT has_database_privilege('admin_probe',current_database(),'CREATE') AND NOT has_database_privilege('admin_probe',current_database(),'TEMP')")=='t')
 check('no_schema_create',query("SELECT NOT bool_or(has_schema_privilege('admin_probe',oid,'CREATE')) FROM pg_namespace")=='t')
 check('history_select_only',query('SELECT has_table_privilege(\'admin_probe\',\'admin."__EFMigrationsHistory"\',\'SELECT\') AND NOT has_table_privilege(\'admin_probe\',\'admin."__EFMigrationsHistory"\',\'INSERT,UPDATE,DELETE,TRUNCATE,REFERENCES,TRIGGER\')')=='t')
 check('no_extra_table_privileges',query("SELECT NOT EXISTS(SELECT FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname IN ('admin','config','data','friend','guild','public') AND c.relkind IN ('r','p','v','S') AND (CASE WHEN n.nspname='admin' AND c.relname IN ('AdminUser','ApiKey') THEN has_table_privilege('admin_probe',c.oid,'TRUNCATE,REFERENCES,TRIGGER') WHEN n.nspname='admin' AND c.relname='__EFMigrationsHistory' THEN has_table_privilege('admin_probe',c.oid,'INSERT,UPDATE,DELETE,TRUNCATE,REFERENCES,TRIGGER') ELSE has_table_privilege('admin_probe',c.oid,'SELECT,INSERT,UPDATE,DELETE,TRUNCATE,REFERENCES,TRIGGER') END))")=='t')
 report['acl']=jsonq("SELECT json_agg(t ORDER BY table_name,privilege_type) FROM (SELECT table_schema,table_name,privilege_type,is_grantable FROM information_schema.role_table_grants WHERE grantee='admin_probe')t")
 report['stage']='zero_row_probes';run('psql',['-X','-v','ON_ERROR_STOP=1','-v','admin_role=admin_probe','-f',str(r/'admin-probes.sql')],'probes.log');check('admin_zero_row_probes_rollback',True)
 check('no_admin_records',query('SELECT NOT EXISTS(SELECT FROM admin."AdminUser") AND NOT EXISTS(SELECT FROM admin."ApiKey")')=='t')
 check('game_after_unchanged',game()==before);check('config_flags_unchanged',config()==cfg);report['game_history']={'before':len(before),'after':len(game()),'exact_ids_match':True,'product_versions_unchanged':True};report['config']=cfg
 report['data_after_sha256']=snapshot();check('all_nonadmin_data_unchanged',report['data_before_sha256']==report['data_after_sha256']);report['result']='PASS'
except Exception as e:report['error']=str(e)
finally:
 if (cluster/'postmaster.pid').exists():
  try:run('pg_ctl',['-D',str(cluster),'-m','fast','-w','stop'],'shutdown.log')
  except Exception as e:report['shutdown_error']=str(e);report['result']='FAIL'
 p=subprocess.run([str(pg/'pg_ctl'),'-D',str(cluster),'status'],capture_output=True,env=env);(r/'shutdown-status.log').write_bytes(p.stdout+p.stderr);report['shutdown']={'status_exit':p.returncode,'postmaster_pid_absent':not (cluster/'postmaster.pid').exists(),'socket_absent':not (sock/'.s.PGSQL.55432').exists()}
 report['elapsed_seconds']=round(time.time()-report['started'],2);(r/'results.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
