from pathlib import Path
import os, subprocess, json, time, signal, hashlib
root=Path.cwd(); phase=root/'phase1042-portable-publish'; build=root/'phase2129-csharp-build'
output=phase/'publish-output-20261012'
if output.exists() or (phase/'attempt-claimed.json').exists():raise SystemExit('Single attempt already claimed')
args=[str(build/'dotnet/dotnet'),'publish','src/Startup/MUnique.OpenMU.Startup.csproj',
      '--no-build','--no-restore','--configuration','Release','--self-contained','false',
      '-p:UseAppHost=false','-p:BuildProjectReferences=false','-p:ci=true',
      '-p:CustomBeforeMicrosoftCommonTargets='+str(phase/'NoBuildOrRestore.targets'),
      '-p:UseSharedCompilation=false','-m:1','-v:normal','--output',str(output)]
env={'PATH':str(build/'dotnet')+':/usr/bin:/bin','HOME':str(build/'session/home'),
     'DOTNET_ROOT':str(build/'dotnet'),'DOTNET_CLI_HOME':str(build/'session/home'),
     'DOTNET_CLI_TELEMETRY_OPTOUT':'1','DOTNET_SKIP_FIRST_TIME_EXPERIENCE':'1',
     'DOTNET_NOLOGO':'1','DOTNET_GENERATE_ASPNET_CERTIFICATE':'false','DOTNET_PROCESSOR_COUNT':'2',
     'DOTNET_CLI_WORKLOAD_UPDATE_NOTIFY_DISABLE':'1','MSBUILDDISABLENODEREUSE':'1',
     'NUGET_PACKAGES':str(build/'session/nuget-packages'),
     'NUGET_HTTP_CACHE_PATH':str(build/'session/nuget-http'),'LANG':'C.UTF-8',
     'TMPDIR':str(build/'session/tmp')}
record={'command':args,'cwd':str(build/'openmu'),'secondsLimit':240,'attempt':1,
        'output':str(output),'restoreApproved':False,'compilationApproved':False}
(phase/'attempt-claimed.json').write_text(json.dumps(record,indent=2)+'\n')
start=time.monotonic();timedout=False
with (phase/'publish.log').open('w') as log:
 p=subprocess.Popen(args,cwd=build/'openmu',env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
 try:code=p.wait(timeout=240)
 except subprocess.TimeoutExpired:
  timedout=True;os.killpg(p.pid,signal.SIGTERM)
  try:code=p.wait(timeout=5)
  except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);code=p.wait()
record.update(exitCode=code,elapsedSeconds=round(time.monotonic()-start,3),timedOut=timedout)
(phase/'attempt-result.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record,indent=2))
