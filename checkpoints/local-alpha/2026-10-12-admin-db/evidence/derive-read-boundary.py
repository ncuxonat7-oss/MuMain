"""Static extraction of selected startup read roots only; no assembly or DB execution."""
from pathlib import Path
import argparse,json,re,hashlib
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--source-root',type=Path,required=True)
parser.add_argument('--baseline-schema',type=Path,required=True)
parser.add_argument('--output',type=Path,required=True)
args=parser.parse_args()
root=args.source_root
model_path='src/Persistence/EntityFramework/Migrations/20261006212931_AddCashShop.Designer.cs'
text=(root/model_path).read_text(encoding='utf-8-sig')
pattern=r'            modelBuilder.Entity\("([^"]+)", b =>\s*\{(.*?)\n                \}\);'
blocks={}
for match in re.finditer(pattern,text,re.S):
 blocks.setdefault(match[1],[]).append((match[2],text[:match.start()].count('\n')+1,text[:match.end()].count('\n')+1))
prefix='MUnique.OpenMU.Persistence.EntityFramework.Model.'
def entity(short):
 entries=blocks[prefix+short];definition=next((b,a,z) for b,a,z in entries if 'b.ToTable(' in b)
 b,a,z=definition;table,schema=re.search(r'b.ToTable\("([^"]+)", "([^"]+)"\)',b).groups()
 cols=[]
 for prop in re.finditer(r'b.Property<[^\n]+>\("([^"]+)"\)(.*?);',b,re.S):
  override=re.search(r'HasColumnName\("([^"]+)"\)',prop[2]);cols.append(override[1] if override else prop[1])
 pk=re.findall(r'"([^"]+)"',re.search(r'b.HasKey\((.*?)\);',b,re.S)[1])
 return {'table':schema+'.'+table,'mappedColumns':cols,'primaryKey':pk,'modelLines':[a,z]}
game=entity('GameConfiguration');root_name=prefix+'GameConfiguration'
collection_navs=[];rows=[]
for name,entries in blocks.items():
 for b,a,z in entries:
  for fk in re.finditer(r'b.HasOne\("'+re.escape(root_name)+r'", (?:null|"[^"]+")\)(.*?);',b,re.S):
   nav=re.search(r'WithMany\("([^"]+)"\)',fk[1]);key=re.search(r'HasForeignKey\((.*?)\)',fk[1],re.S)
   if not nav:continue
   target=entity(name.split('.')[-1]);keys=re.findall(r'"([^"]+)"',key[1]);assert len(keys)==1 and target['primaryKey']==['Id']
   rows.append({'navigation':nav[1],'table':target['table'],'provenMinimumColumns':sorted(set(['Id']+keys)),
    'ifAggregateColumns':target['mappedColumns'],'scope':'mandatory first-hop table and key-column read once JSON GameConfiguration query is issued; aggregate flag determines full-row projection and recursion',
    'aggregateProjectionStatus':'conditional on generated navigation IsMemberOfAggregate; base property is annotated but generated navigation bridge not established',
    'relationshipLines':[a,z],'columnDefinitionLines':target['modelLines']})
   collection_navs.append(nav[1])
navblocks=[(b,a,z) for b,a,z in blocks[root_name] if 'b.Navigation("RawAttributes")' in b];assert len(navblocks)==1
expected=re.findall(r'b.Navigation\("([^"]+)"\)',navblocks[0][0]);assert sorted(collection_navs)==sorted(expected);assert len(rows)==21
# Inspect only selected schemas already saved by the completed diagnostic; no database access.
schema=(args.baseline_schema).read_text()
def saved_columns(qualified):
 sch,table=qualified.split('.');m=re.search(r'CREATE TABLE '+re.escape(sch)+r'\."'+re.escape(table)+r'" \((.*?)\n\);',schema,re.S);assert m,qualified
 return re.findall(r'^    "([^"]+)" ',m[1],re.M)
selected=[game,entity('PlugInConfiguration'),entity('SystemConfiguration')]
for e in selected:assert sorted(e['mappedColumns'])==sorted(saved_columns(e['table'])),e['table']
for row in rows:assert sorted(row['ifAggregateColumns'])==sorted(saved_columns(row['table'])),row['table']
refs=[]
for b,a,z in blocks[root_name]:
 for fk in re.finditer(r'b.HasOne\("([^"]+)", "([^"]+)"\)(.*?);',b,re.S):
  target=entity(fk[1].split('.')[-1]);keys=re.findall(r'"([^"]+)"',re.search(r'HasForeignKey\((.*?)\)',fk[3],re.S)[1]);refs.append({'navigation':fk[2],'targetTable':target['table'],'parentForeignKeyColumn':keys[-1],'targetMappedColumns':target['mappedColumns'],'condition':'no target table read for shadow FK, inverse or nonaggregate reference; full row and recursion only for real aggregate FK without collection back-reference','relationshipLines':[a,z]})
assert len(refs)==3
for name in ['PlugInConfiguration','SystemConfiguration']:
 assert not any('b.Navigation(' in b for b,_,_ in blocks[prefix+name]),name
output={'status':'PARTIAL_STATIC_READ_CONTRACT_NOT_EXECUTABLE','activationAllowed':False,'permissionListKind':'necessary static lower bound, insufficient for execution; no grant authority','sourceModelToCandidateQueryParity':'NOT_ESTABLISHED','sourceCommit':'d067b3c11c23c3145de6e2c76201ab9a93b267c8','modelSource':model_path,
 'candidatePersistenceSha256':'f12b509a8e99453bec482049cc92c2ec677c424accf6e3b019c155c342437014','compiledNavigationParity':'NOT_ESTABLISHED; saved compiled metadata proves migration IDs/contexts only',
 'entityJsonRoot':dict(game,projection='alias.*; all physical columns of this pinned baseline table',condition='Program.CreateMissingPlugInConfigurations only after missing known plugins; other data-source invocations not promoted to Entity-role evidence'),
 'entityFirstHopCollections':sorted(rows,key=lambda x:x['table']), 'entityFirstHopReferences':refs,
 'typedRoots':[dict(entity(n),projection='Set<T>().ToListAsync materializes all mapped properties',navigationScope='pinned migration model has no outgoing navigation; parent collection membership alone is not a query',compiledTypedModelParity='NOT_ESTABLISHED') for n in ['PlugInConfiguration','SystemConfiguration']],
 'unresolved':['Generated persistent navigation aggregate flags and FK shadow/CLR status for root Raw* properties and reachable descendants; base MemberOfAggregate attributes alone do not certify generated navigation metadata.', 'Concrete compiled typed-model projection parity with migration model, including property inclusion and navigation set.', 'Recursive aggregate descendants versus reference-only targets, join-column traversal and alias depth cutoff; no blanket table allowlist.', 'Conditional plugin custom-reference resolution can load GameConfiguration through a separate data-source path; exact runtime activation/connection attribution not established by this bounded source set.'],
 'notRun':['database','migrations','grants','assembly loading','builds','tests','Windows','workflows','write closure'],
 'savedSchemaSha256':hashlib.sha256(args.baseline_schema.read_bytes()).hexdigest()}
args.output.write_text(json.dumps(output,indent=2)+'\n')
print('Root physical columns:',len(game['mappedColumns']));print('Mandatory first-hop tables:',len(rows));print('Typed model scalar roots:',[(x['table'],len(x['mappedColumns'])) for x in output['typedRoots']]);print('\n'.join(x['navigation']+' -> '+x['table']+' ('+', '.join(x['provenMinimumColumns'])+')' for x in output['entityFirstHopCollections']))
