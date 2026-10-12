"""One fresh local disabled package; pinned existing inputs, no runtime execution."""
import pathlib,json,hashlib,importlib.util,sys,shutil
R=pathlib.Path(__file__).resolve().parent; W=R.parent
B=W/'phase2027-powershell-check/control-database-guards-20261011'; C=W/'phase1042-portable-publish/control-published-candidate-20261012';D=R/'control-full-disabled-alpha-20261012'
def h(p):
    if p.is_symlink() or not p.is_file():raise ValueError('Nonregular input')
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p,pin):
    if h(p)!=pin:raise ValueError('Pinned input differs: '+str(p))
    return json.loads(p.read_text())
def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
if D.exists():raise SystemExit('DESTINATION_EXISTS: no overwrite')
if shutil.disk_usage(R).free < 3*1024**3:raise SystemExit('Insufficient local disk headroom')
base=read(B/'package-inventory.json','85cf983cb786f284747763074b84cd0c6bae9c2b73bd6e0923e3849cefc15feb')
component=read(C/'candidate-integrity.json','8905dc32f34c756603c2fe8dc9a70f252d363a2c198a432c30db4c52d1064cc8')
read(C/'candidate-status.json','4dbaba3c1060a8ef8af4471c9e56ed3bdca77a29679d0f3f9e07eb38ce8db7e7')
p=W/'phase2104-admin-availability/source/scripts/package-windows11-local.py'
if h(p)!='c700e0ed3a0fe2a6bbd77de0f0bd5c60f814ca4dd49852cf15734473a53459e7':raise ValueError('Packager pin mismatch')
spec=importlib.util.spec_from_file_location('existing_packager',p);module=importlib.util.module_from_spec(spec);sys.dont_write_bytecode=True;spec.loader.exec_module(module)
rows={};sources={}
for path,row in base.items():
    if path.split('/')[0] in ('client','dotnet','postgres','powershell','prerequisites'):
        rows[path]={**row,'origin':'UNCHANGED_PHASE2027_PAYLOAD'};sources[path]=B/path
for row in component['files']:
    if row['target'].startswith('server/'):
        path=row['target'];rows[path]={'bytes':row['bytes'],'sha256':row['sha256'],'origin':row['origin'],'source':row['source']};sources[path]=C/path
for p in sorted((R/'source/scripts/windows11').iterdir()):
    if p.is_file():
        path='scripts/windows11/'+p.name;rows[path]={'bytes':p.stat().st_size,'sha256':h(p),'origin':'LOCAL_INTEGRATED_DISABLED_LAUNCHER'};sources[path]=p
assert len(rows)==24417
seen=set()
for path in rows:
    module.safe_path(path)
    if path.casefold() in seen:raise ValueError('Collision')
    seen.add(path.casefold())
D.mkdir()
save(D/'packaging-status.json',{'status':'INCOMPLETE_STAGING','launchEnabled':False,'approvedLaunchManifestSha256':None})
for path,row in rows.items():
    source=sources[path]
    if source.is_symlink() or not source.is_file():raise ValueError('Invalid input')
    # Existing helper creates every destination exclusively and hashes actual copied bytes.
    target=D/path;target.parent.mkdir(parents=True,exist_ok=True)
    with source.open('rb') as f:module.copy_checked(f,target,row['bytes'],row['sha256'])
rows=dict(sorted(rows.items()));save(D/'package-inventory.json',rows)
draft=json.loads((B/'windows11-launch-manifest.draft.json').read_text());draft.pop('runtimeArchive');draft.update(schema=3,hashes={p:r['sha256'] for p,r in rows.items()},runtimeProvenance=json.loads((D/'scripts/windows11/runtime-pin.json').read_text()),launchEnabled=False,approvedLaunchManifestSha256=None)
save(D/'windows11-launch-manifest.draft.json',draft)
status={'status':'FULL_PACKAGE_STAGED_AWAITING_POWERSHELL_INTEGRITY','launchEnabled':False,'approvedLaunchManifestSha256':None,'windowsAcceptance':'NOT_RUN','runtimeGrantStatus':'RUNTIME_GRANTS_UNRESOLVED','payloadFiles':len(rows),'payloadBytes':sum(x['bytes'] for x in rows.values()),'blockers':['RUNTIME_GRANTS_UNRESOLVED','WINDOWS_ACCEPTANCE_REQUIRED','WEB_HTTP_ACCEPTANCE_NOT_RUN'],'originalPackagesModified':False}
save(D/'packaging-status.json',status)
admission={'schema':1,'kind':'FULL_DISABLED_ALPHA','inventorySha256':h(D/'package-inventory.json'),'draftSha256':h(D/'windows11-launch-manifest.draft.json'),'statusSha256':h(D/'packaging-status.json'),'payloadFiles':len(rows),'serverFiles':8440,'launchEnabled':False,'approvedLaunchManifestSha256':None,'windowsAcceptance':'NOT_RUN','runtimeGrantStatus':'RUNTIME_GRANTS_UNRESOLVED','provenance':{'baseInventorySha256':h(B/'package-inventory.json'),'publishedComponentIntegritySha256':h(C/'candidate-integrity.json'),'sourceCheckpoint':'7f1f061f9201f460cd13a3dc8cd9a455870bdc36','publishedCheckpoint':'35f0ab6eab69974cab60f30780daed019cc0f8d5','originalRuntimeArchiveCertifiesNewServer':False}}
save(D/'package-admission.json',admission)
save(R/'staging-result.json',{'status':'COPY_HASH_PASS','payloadFiles':len(rows),'payloadBytes':status['payloadBytes'],'inventorySha256':admission['inventorySha256'],'admissionSha256':h(D/'package-admission.json'),'draftSha256':admission['draftSha256'],'destination':str(D.relative_to(W)),'launchEnabled':False,'approvedLaunchManifestSha256':None,'readBackPowerShellVerification':'PENDING','baseComponents':{k:sum(p.startswith(k+'/') for p in rows) for k in ('client','dotnet','postgres','powershell','prerequisites','server','scripts')}})
print(json.dumps({'status':'COPY_HASH_PASS','files':len(rows),'bytes':status['payloadBytes'],'inventorySha256':admission['inventorySha256']}))
