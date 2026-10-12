"""Read saved JSON only; no assembly, process, database or permission execution."""
from pathlib import Path
import json,hashlib,collections
r=Path(__file__).parent
m=json.loads((r/'output/game-navigation.json').read_text());entities={e['name']:e for e in m['entities']}
full={m['root']};joins=set()
for edge in m['edges']:
 if edge['action']=='aggregate-full-row':full.add(edge['target'])
 elif edge['action']=='join-columns-only':joins.add(edge['target'])
join_rows=[]
for t in sorted(joins):
 e=entities[t];cols=set()
 for edge in (x for x in m['edges'] if x['action']=='join-columns-only' and x['target']==t):
  nav=next(n for n in entities[edge['from']]['navigations'] if n['name']==edge['navigation'])
  other=[f for f in e['foreignKeys'] if f['principalType']!=edge['from']]
  assert len(other)==1 and len(other[0]['properties'])==1
  cols.add(nav['fkProperties'][0]['name'])
  cols.add(next(p['column'] for p in e['properties'] if p['name']==other[0]['properties'][0]))
 join_rows.append({'table':e['schema']+'.'+e['table'],'columns':sorted(cols),'basis':'observed single other FK and pinned JSON join-column branch'})
prior=Path('/workspace/admin-overnight-checkpoint/checkpoints/local-alpha/2026-10-12-admin-db/evidence/startup-read-contract.json')
p=json.loads(prior.read_text());root=entities[m['root']]
assert sorted(x['column'] for x in root['properties'])==sorted(p['entityJsonRoot']['mappedColumns'])
typed=[]
for name in ['PlugInConfiguration','SystemConfiguration']:
 t=json.loads((r/('output/typed-'+name+'.json')).read_text());e=next(x for x in t['entities'] if x['clrType'].endswith('.'+name))
 assert e['navigations']==[]
 old=next(x for x in p['typedRoots'] if x['table']=='config.'+name)
 assert sorted(x['column'] for x in e['properties'])==sorted(old['mappedColumns'])
 typed.append({'table':'config.'+name,'columns':[x['column'] for x in e['properties']],'outgoingNavigations':0})
result={'status':'STATIC_RECONCILIATION_ONLY_NOT_GRANT_AUTHORITY','fullRowProjectionTables':[{'table':entities[t]['schema']+'.'+entities[t]['table'],'columns':[p['column'] for p in entities[t]['properties']],'projection':'alias.*; mapped columns captured, not live-schema validation'} for t in sorted(full)],'joinColumnProjectionTables':join_rows,'typedScalarRoots':typed,'counts':{'fullRowTables':len(full),'joinTables':len(joins)},'limits':['Depends on saved inspector branch decisions and pinned builder semantics; generated SQL was not captured.','No complete startup role/conditional-data-source attribution or feature/write closure.','Key declaring-entity identity is not separately serialized; recorded traversal actions encode the inspected declared-PK branch. If independent replay requires that raw field, it remains absent.']}
(r/'reconciliation.json').write_text(json.dumps(result,indent=2)+'\n')
files=['output/game-navigation.json','output/typed-PlugInConfiguration.json','output/typed-SystemConfiguration.json','output/aggregate-methods.json','output/result.json','Inspector.cs','execution.json','invocation.json']
(r/'reconciliation-input-hashes.json').write_text(json.dumps([{'path':n,'sha256':hashlib.sha256((r/n).read_bytes()).hexdigest(),'bytes':(r/n).stat().st_size} for n in files]+[{'path':str(prior),'sha256':hashlib.sha256(prior.read_bytes()).hexdigest(),'sourceCommit':'07eceffcf1059ba861c929b3725ed2a2e23d3f56'}],indent=2)+'\n')
print(json.dumps(result['counts']));print('Prior root/typed column lists match saved candidate metadata.')
