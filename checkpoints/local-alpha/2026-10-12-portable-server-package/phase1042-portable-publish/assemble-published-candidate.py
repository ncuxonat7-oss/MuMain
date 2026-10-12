"""One local publish-layout continuation; pinned corrected EF, no execution."""
import importlib.util
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parent.parent
PHASE=ROOT/'phase1042-portable-publish'
PUBLISH=PHASE/'publish-output-20261012'
OLD=ROOT/'phase1022-windows-candidate/control-server-candidate-20261012'
DEST=PHASE/'control-published-candidate-20261012'
PUB_HASH='69c131ec847e6a730b13e53e49cf97f038003849b96bd83b810c3f415e0ce660'
VERIFIER_HASH='155f569c117134a7ec66ecd84edb09a880cf6fddbdc9dd9d26a841145ad9fc86'
EF='MUnique.OpenMU.Persistence.EntityFramework.dll'
PDB='MUnique.OpenMU.Persistence.EntityFramework.pdb'
BLOCKERS=['NOT_WINDOWS_ACCEPTED','RUNTIME_GRANTS_UNRESOLVED',
          'COMPONENT_ONLY_NOT_FULL_PACKAGE','LEGACY_LAUNCHER_RUNTIME_CONTRACT_NOT_ALIGNED',
          'PUBLISHED_WEB_HTTP_BEHAVIOR_NOT_RUN']


def digest(p):
    with p.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def load_verifier():
    p=ROOT/'phase1022-windows-candidate/source/scripts/package-windows-candidate.py'
    if p.is_symlink() or digest(p)!=VERIFIER_HASH:raise ValueError('Verifier pin mismatch')
    spec=importlib.util.spec_from_file_location('candidate',p)
    module=importlib.util.module_from_spec(spec)
    previous=sys.dont_write_bytecode
    try:
        sys.dont_write_bytecode=True
        spec.loader.exec_module(module)
    finally:sys.dont_write_bytecode=previous
    return module


def status():
    return {'status':'VERIFIED_PUBLISH_LAYOUT_NOT_RUNNABLE','launchEnabled':False,
            'approvedLaunchManifestSha256':None,'windowsAcceptance':'NOT_RUN',
            'webAssetLayout':'PUBLISH_REFERENCES_VERIFIED','webHttpAcceptance':'NOT_RUN',
            'setupExecution':'BLOCKED','runtimeGrantStatus':'RUNTIME_GRANTS_UNRESOLVED',
            'blockers':BLOCKERS}


def contract(c):
    pub=c.pinned_json(ROOT,'phase1042-portable-publish/publish-inventory.json',PUB_HASH)
    old=c.load_contract(ROOT)
    c.verify(OLD,old)
    originals={r['target']:r for r in old['files']}
    rows=[]
    for item in pub['files']:
        target='server/'+item['path']
        source=PUBLISH/item['path'];digest_value=item['sha256'];size=item['bytes']
        origin='SDK_PUBLISH_ONLY'
        if item['path'] in (EF,PDB):
            row=originals[target];source=OLD/target;digest_value=row['sha256'];size=row['bytes']
            origin='ACCEPTED_BINARY_JSON_OVERLAY_NOT_STALE_PUBLISH_COPY'
        rows.append({'target':target,'source':source.relative_to(ROOT).as_posix(),
                     'bytes':size,'sha256':digest_value,'origin':origin})
    for row in old['files']:
        if row['target'].startswith('scripts/'):
            rows.append({'target':row['target'],'source':(OLD/row['target']).relative_to(ROOT).as_posix(),
                         'bytes':row['bytes'],'sha256':row['sha256'],'origin':'UNCHANGED_BLOCKED_SOURCE_SNAPSHOT'})
    c.check_rows(rows)
    return {'schema':1,'kind':'DISABLED_PUBLISHED_SERVER_COMPONENT_ONLY','files':rows,
            'publishInventorySha256':PUB_HASH,'parentOverlayPlanSha256':old['planSha256'],
            'originalRuntimeArchiveCertifiesNewCandidate':False,
            'launchEnabled':False,'approvedLaunchManifestSha256':None,
            'serverCount':len(pub['files']),'sourceSnapshotCount':12,'blockers':BLOCKERS}


def check_web(c,destination):
    server=destination/'server'
    if list(server.glob('*.staticwebassets.runtime.json')):raise ValueError('Development runtime manifest carried forward')
    manifests=list(server.glob('*.staticwebassets.endpoints.json'))
    if [p.name for p in manifests]!=['MUnique.OpenMU.Startup.staticwebassets.endpoints.json']:
        raise ValueError('Unexpected publish endpoint manifest set')
    web=json.loads(manifests[0].read_text())
    if web['ManifestType']!='Publish':raise ValueError('Expected publish endpoints')
    if '/workspace/' in json.dumps(web):raise ValueError('Absolute build path in endpoints')
    refs={row['AssetFile'] for row in web['Endpoints']}
    for ref in refs:c.regular(server/'wwwroot',ref)
    actual={p.relative_to(server/'wwwroot').as_posix() for p in (server/'wwwroot').rglob('*') if p.is_file()}
    if refs!=actual:raise ValueError('Published asset file/reference mismatch')
    for p in list(server.glob('*.json'))+list(server.glob('*.config')):
        if '/workspace/' in p.read_text(errors='replace'):raise ValueError('Build path in active top-level configuration')
    return {'endpointCount':len(web['Endpoints']),'uniqueAssetFiles':len(refs),
            'allReferencesResolve':True,'runtimeBuildManifests':0,
            'activeTopLevelBuildPathReferences':0,'httpTest':'NOT_RUN'}


def verify(c,expected):
    c.verify_payload(DEST,expected)
    c.verify_guards(DEST)
    if json.loads((DEST/c.STATUS).read_text())!=status():raise ValueError('Incomplete/altered status')
    web=check_web(c,DEST)
    if digest(DEST/'server'/EF)!='67adf087ec8f0d3de395740f0ce09e8040777698085747fdb23d89fee4f393a1':
        raise ValueError('Corrected EF missing')
    return {'result':'PASS_PUBLISH_LAYOUT_AND_INTEGRITY_ONLY','fileCount':len(expected['files']),
            'bytes':sum(r['bytes'] for r in expected['files']),'serverFiles':expected['serverCount'],
            'sourceSnapshots':12,'web':web,'correctedEfSha256':digest(DEST/'server'/EF),
            'matchingPdbSha256':digest(DEST/'server'/PDB),'oldCandidateVerifiedUnchanged':True,
            'launchEnabled':False,'approvedLaunchManifestSha256':None,'blockers':BLOCKERS}


def stage(c,expected):
    c.no_links(DEST)
    if DEST.exists():raise ValueError('Overwrite refused')
    helper=c.load_helper(ROOT)
    DEST.mkdir()
    c.save_new(DEST/c.STATUS,c.disabled_status())
    for row in expected['files']:
        target=DEST/row['target'];target.parent.mkdir(parents=True,exist_ok=True)
        with c.regular(ROOT,row['source']).open('rb') as stream:
            helper.copy_checked(stream,target,row['bytes'],row['sha256'])
    c.save_new(DEST/c.CONTRACT,expected)
    c.verify_payload(DEST,expected)
    c.verify_guards(DEST)
    check_web(c,DEST)
    (DEST/c.STATUS).write_text(json.dumps(status(),indent=2)+'\n')
    return verify(c,expected)


if __name__=='__main__':
    action=sys.argv[1] if len(sys.argv)==2 else ''
    if action not in ('stage','verify','launch-check'):raise SystemExit('stage, verify or launch-check required')
    c=load_verifier();expected=contract(c)
    if action=='stage':result=stage(c,expected)
    else:
        result=verify(c,expected)
        if action=='launch-check':raise SystemExit('LAUNCH_DENIED: Windows/setup/runtime admission unresolved')
    print(json.dumps(result,indent=2))
