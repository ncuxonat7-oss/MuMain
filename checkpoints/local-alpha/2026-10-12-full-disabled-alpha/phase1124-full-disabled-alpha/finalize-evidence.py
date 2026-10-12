from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parent;D=R/'control-full-disabled-alpha-20261012'
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,v):p.write_text(json.dumps(v,indent=2)+'\n')
assert (R/'full-powershell-verify-final.exit').read_text().strip()=='0'
assert 'PACKAGE_INTEGRITY_OK' in (R/'full-powershell-verify-final.txt').read_text()
assert (R/'integration-tests-final.exit').read_text().strip()=='0'
a=json.loads((D/'package-admission.json').read_text());s=json.loads((D/'packaging-status.json').read_text());i=json.loads((D/'package-inventory.json').read_text());s.update(status='FULL_PACKAGE_INTEGRITY_VERIFIED_LAUNCH_DISABLED',payloadBytes=sum(x['bytes'] for x in i.values()),payloadVerification='ACTUAL_POWERSHELL_7_4_20_PASS');save(D/'packaging-status.json',s);a['statusSha256']=h(D/'packaging-status.json');save(D/'package-admission.json',a)
r=json.loads((R/'staging-result.json').read_text());r.update(admissionSha256=h(D/'package-admission.json'),readBackPowerShellVerification='PASS');save(R/'staging-result.json',r)
print(json.dumps({'inventorySha256':a['inventorySha256'],'admissionSha256':r['admissionSha256'],'payloadFiles':len(i),'payloadBytes':s['payloadBytes']}))
