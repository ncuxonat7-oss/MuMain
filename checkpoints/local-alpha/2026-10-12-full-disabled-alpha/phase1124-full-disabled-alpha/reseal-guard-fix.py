from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parent;D=R/'control-full-disabled-alpha-20261012';S=R/'source/scripts/windows11/Guards.ps1'
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
i=json.loads((D/'package-inventory.json').read_text());key='scripts/windows11/Guards.ps1';assert h(D/key)==i[key]['sha256']
s=S.read_text();old='(Get-Item -LiteralPath $path).Length -ne $row.bytes';assert s.count(old)==1;s=s.replace(old,'(Get-Item -LiteralPath $path -Force).Length -ne $row.bytes');S.write_text(s);(D/key).write_bytes(S.read_bytes())
i[key]['bytes']=S.stat().st_size;i[key]['sha256']=h(S);save(D/'package-inventory.json',i)
d=json.loads((D/'windows11-launch-manifest.draft.json').read_text());d['hashes'][key]=h(S);save(D/'windows11-launch-manifest.draft.json',d)
a=json.loads((D/'package-admission.json').read_text());a['inventorySha256']=h(D/'package-inventory.json');a['draftSha256']=h(D/'windows11-launch-manifest.draft.json');save(D/'package-admission.json',a)
r=json.loads((R/'staging-result.json').read_text());r.update(inventorySha256=a['inventorySha256'],admissionSha256=h(D/'package-admission.json'),draftSha256=a['draftSha256'],payloadBytes=sum(x['bytes'] for x in i.values()),guardFix='Get-Item -Force for legitimate hidden .NET .version payload; no payload changes');save(R/'staging-result.json',r)
# Staging status is a historical record and deliberately not rewritten.
print(a['inventorySha256'])
