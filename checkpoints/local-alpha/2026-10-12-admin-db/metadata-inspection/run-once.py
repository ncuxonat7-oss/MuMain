from pathlib import Path
import subprocess,json,time,resource,os,hashlib
r=Path(__file__).parent
claim=r/'candidate-attempt.claim'
with claim.open('x') as f:f.write('One authorized candidate attempt; no retry.\n')
dotnet='/workspace/mumain-tools/dotnet-10.0.401/dotnet'
args=[dotnet,'exec','--depsfile',str(r/'app/MUnique.OpenMU.Persistence.EntityFramework.deps.json'),'--runtimeconfig',str(r/'app/MUnique.OpenMU.Persistence.EntityFramework.runtimeconfig.json'),str(r/'app/Inspector.dll'),str(r/'app/MUnique.OpenMU.Persistence.EntityFramework.dll'),str(r/'output')]
env={'PATH':'/usr/bin:/bin','DOTNET_ROOT':'/workspace/mumain-tools/dotnet-10.0.401','DOTNET_CLI_HOME':str(r/'dotnet-home'),'DOTNET_CLI_TELEMETRY_OPTOUT':'1','DOTNET_SKIP_FIRST_TIME_EXPERIENCE':'1','DOTNET_GENERATE_ASPNET_CERTIFICATE':'false','DOTNET_NOLOGO':'1','DOTNET_EnableDiagnostics':'0','XDG_CACHE_HOME':str(r/'cache'),'XDG_CONFIG_HOME':str(r/'config'),'XDG_DATA_HOME':str(r/'data'),'TMPDIR':str(r/'tmp'),'LANG':'C.UTF-8','TZ':'UTC'}
(r/'invocation.json').write_text(json.dumps({'argv':args,'environment':env,'cwd':str(r/'work'),'timeoutSeconds':120,'attemptLimit':1,'isolation':'unchanged platform restrictions; residual network/socket access risk accepted; no bwrap or escalation'},indent=2))
start=time.monotonic();status='FINISHED'
with (r/'stdout.private.log').open('wb') as out,(r/'stderr.private.log').open('wb') as err:
 p=subprocess.Popen(args,env=env,cwd=r/'work',stdin=subprocess.DEVNULL,stdout=out,stderr=err)
 try:code=p.wait(timeout=120)
 except subprocess.TimeoutExpired:p.kill();code=p.wait();status='TIMEOUT_KILLED'
usage=resource.getrusage(resource.RUSAGE_CHILDREN)
result={'status':status,'exitCode':code,'elapsedSeconds':round(time.monotonic()-start,3),'userCpuSeconds':usage.ru_utime,'systemCpuSeconds':usage.ru_stime,'maxRssKiB':usage.ru_maxrss,'attempts':1,'connectionAttemptSentinelPresent':(r/'output/connection-attempt.json').exists(),'stdoutBytes':(r/'stdout.private.log').stat().st_size,'stderrBytes':(r/'stderr.private.log').stat().st_size,'inspectorSha256':hashlib.sha256((r/'app/Inspector.dll').read_bytes()).hexdigest()}
(r/'execution.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
if (r/'output/result.json').exists():print((r/'output/result.json').read_text())
if (r/'output/connection-attempt.json').exists():print((r/'output/connection-attempt.json').read_text())
