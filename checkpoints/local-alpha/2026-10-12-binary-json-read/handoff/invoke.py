from pathlib import Path
import subprocess,json,sys
r=Path(__file__).parent;root=r;dot='/workspace/mumain-tools/dotnet-10.0.401/dotnet';mode=sys.argv[1]
assert mode in ('run','report-selfcheck'), 'No build/other mode authorized by handoff'
env={'PATH':'/usr/bin:/bin','DOTNET_ROOT':str(Path(dot).parent),'DOTNET_CLI_HOME':str(r/'home'),'DOTNET_CLI_TELEMETRY_OPTOUT':'1','DOTNET_NOLOGO':'1','DOTNET_GENERATE_ASPNET_CERTIFICATE':'false','DOTNET_EnableDiagnostics':'0','HOME':str(r/'home'),'TMPDIR':str(r/'tmp')}
args=[dot,'exec','/workspace/mumain-tools/dotnet-10.0.401/sdk/10.0.401/Roslyn/bincore/csc.dll','@'+str(r/'compile.rsp')] if mode=='compile' else [dot,'exec','--depsfile',str(r/'app/MUnique.OpenMU.Persistence.EntityFramework.deps.json'),'--runtimeconfig',str(r/'app/MUnique.OpenMU.Persistence.EntityFramework.runtimeconfig.json'),str(r/'app/ReadHarness.dll'),str(root),mode,str(r)]
(r/(mode+'-invocation.json')).write_text(json.dumps({'argv':args,'environment':env,'cwd':str(r)},indent=2)+'\n')
p=subprocess.run(args,env=env,cwd=r,capture_output=True,timeout=120);(r/(mode+'.stdout')).write_bytes(p.stdout);(r/(mode+'.stderr')).write_bytes(p.stderr);(r/(mode+'-exit.json')).write_text(json.dumps({'exitCode':p.returncode})+'\n');print(mode,p.returncode);print(p.stdout.decode()[:1200]);sys.exit(p.returncode)
