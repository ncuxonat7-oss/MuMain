import json,hashlib,importlib.util,sys,shutil
from pathlib import Path
R=Path(__file__).resolve().parent;W=R.parent;B=W/'phase1250-sanitized-transfer/control-sanitized-transfer-20261012';S=R/'source/scripts/windows11';D=R/'control-admin-integrated-disabled-20261012'
def h(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,j):
 with p.open('x') as f:json.dump(j,f,indent=2);f.write('\n')
parent='69f7a0700ef387a23c75e0427044674974a54c0a987e6a788ab5bbf3c9aa2d5f'
assert h(B/'package-inventory.json')==parent
if D.exists():raise SystemExit('DESTINATION_EXISTS')
assert shutil.disk_usage(R).free>=4*1024**3
helper=W/'phase2104-admin-availability/source/scripts/package-windows11-local.py';assert h(helper)=='c700e0ed3a0fe2a6bbd77de0f0bd5c60f814ca4dd49852cf15734473a53459e7'
spec=importlib.util.spec_from_file_location('packager',helper);m=importlib.util.module_from_spec(spec);sys.dont_write_bytecode=True;spec.loader.exec_module(m)
old=json.loads((B/'package-inventory.json').read_text());assert len(old)==24417
sources={f'scripts/windows11/{p.name}':p for p in S.iterdir() if p.is_file()}
added=set(sources)-set(old)
assert added=={f'scripts/windows11/{n}' for n in ['disposable-role-profile.json','AdminProvisioning.ps1','admin-provisioning-contract.json','admin-provisioning.original.sql','admin-provisioning.sql']}
assert len(sources)==12
D.mkdir();inventory={};changed=[]
for rel in sorted(set(old)|set(sources)):
 m.safe_path(rel);src=sources.get(rel,B/rel);assert src.is_file() and not src.is_symlink()
 if rel in sources:
  size=src.stat().st_size;sha=h(src)
 else:size=old[rel]['bytes'];sha=old[rel]['sha256']
 row=old.get(rel)
 if row is None or row['sha256']!=sha:
  row={'bytes':size,'sha256':sha,'origin':'ADMIN_SETUP_SOURCE_INTEGRATION','sourceBundleSha256':'28a139de1113f47ef47d36972f70c2684e655887e82dd1180fe6bec76483994e','parentSha256':old.get(rel,{}).get('sha256')};changed.append({'path':rel,**row})
 out=D/rel;out.parent.mkdir(parents=True,exist_ok=True)
 with src.open('rb') as stream:m.copy_checked(stream,out,size,sha)
 inventory[rel]=row
assert len(inventory)==24422
save(D/'package-inventory.json',inventory)
draft=json.loads((B/'windows11-launch-manifest.draft.json').read_text());draft['hashes']={k:v['sha256'] for k,v in inventory.items()};assert draft['launchEnabled'] is False and draft['approvedLaunchManifestSha256'] is None
save(D/'windows11-launch-manifest.draft.json',draft)
status={'status':'ADMIN_SETUP_INTEGRATED_DISABLED_NOT_LIVE_VALIDATED','launchEnabled':False,'approvedLaunchManifestSha256':None,'windowsAcceptance':'NOT_RUN','liveValidationStatus':'NOT_RUN','runtimeGrantStatus':'DISPOSABLE_PROFILE_PREPARED','credentialStatus':'REQUIRED_AT_SEPARATE_SETUP','setupApplicationApprovalSha256':None,'payloadFiles':len(inventory),'payloadBytes':sum(x['bytes'] for x in inventory.values()),'blockers':['SETUP_APPLICATION_APPROVAL_REQUIRED','CREDENTIALS_REQUIRED','WINDOWS_RUNTIME_ACCEPTANCE_NOT_RUN','LIVE_ADMIN_AND_GRANTS_NOT_RUN','WEB_HTTP_ACCEPTANCE_NOT_RUN']}
save(D/'packaging-status.json',status)
admission=json.loads((B/'package-admission.json').read_text());admission.update(inventorySha256=h(D/'package-inventory.json'),draftSha256=h(D/'windows11-launch-manifest.draft.json'),statusSha256=h(D/'packaging-status.json'),payloadFiles=len(inventory),runtimeGrantStatus='DISPOSABLE_PROFILE_PREPARED');save(D/'package-admission.json',admission)
assert h(B/'package-inventory.json')==parent
result={'status':'COPY_HASH_PASS_NOT_YET_POWERSHELL_VERIFIED','parentInventorySha256':parent,'inventorySha256':admission['inventorySha256'],'payloadFiles':len(inventory),'payloadBytes':status['payloadBytes'],'addedFiles':sorted(added),'changedFiles':changed,'controlFiles':{n:{'bytes':(D/n).stat().st_size,'sha256':h(D/n)} for n in ['package-inventory.json','package-admission.json','windows11-launch-manifest.draft.json','packaging-status.json']},'originalInventoryUnchanged':True,'launchEnabled':False,'approvedLaunchManifestSha256':None}
save(R/'candidate-identities.json',result);print(json.dumps({k:v for k,v in result.items() if k!='changedFiles'},indent=2))
