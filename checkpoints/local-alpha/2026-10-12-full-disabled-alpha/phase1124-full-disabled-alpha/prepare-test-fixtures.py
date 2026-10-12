from pathlib import Path
import json,hashlib,shutil
R=Path(__file__).resolve().parent;P=R/'control-full-disabled-alpha-20261012';F=R/'fixtures-final';F.mkdir(exist_ok=False)
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,v):p.write_text(json.dumps(v,indent=2)+'\n')
def fixture(name):
    p=F/name;p.mkdir();shutil.copytree(P/'scripts',p/'scripts')
    for n in ('package-inventory.json','package-admission.json','windows11-launch-manifest.draft.json','packaging-status.json'):shutil.copyfile(P/n,p/n)
    return p
cases=[]
for name in ('missing','corrupt','wrong-manifest','unsafe-path','wrong-config','bad-disabled-type','wrong-external-pin'):
    p=fixture(name);a=json.loads((p/'package-admission.json').read_text());expected=a['inventorySha256'];code='HASH_MISMATCH'
    if name=='missing':code='START_FAILED'
    if name=='corrupt':
        i=json.loads((p/'package-inventory.json').read_text());k=next(iter(i));out=p/k;out.parent.mkdir(parents=True);out.write_bytes(b'X'*i[k]['bytes'])
    if name=='wrong-manifest':
        with (p/'package-inventory.json').open('a') as f:f.write(' ')
    if name in ('unsafe-path','wrong-config'):
        i=json.loads((p/'package-inventory.json').read_text());d=json.loads((p/'windows11-launch-manifest.draft.json').read_text());k=next(iter(i));row=i.pop(k);d['hashes'].pop(k)
        key='../unsafe' if name=='unsafe-path' else 'server/rogue.config'
        i={key:row,**i};d['hashes']={key:row['sha256'],**d['hashes']}
        save(p/'package-inventory.json',i);save(p/'windows11-launch-manifest.draft.json',d)
        a['inventorySha256']=h(p/'package-inventory.json');a['draftSha256']=h(p/'windows11-launch-manifest.draft.json');save(p/'package-admission.json',a);expected=a['inventorySha256'];code='UNSAFE_CONFIG'
    if name=='bad-disabled-type':a['launchEnabled']='false';save(p/'package-admission.json',a);code='UNSAFE_CONFIG'
    if name=='wrong-external-pin':expected='0'*64
    cases.append({'name':name,'root':str(p),'expectedInventorySha256':expected,'code':code})
save(R/'test-cases.json',cases)
