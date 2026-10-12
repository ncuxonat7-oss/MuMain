from pathlib import Path
import re,json,hashlib,collections
r=Path(__file__).parent/'handoff'
s=(r/'output/game.sql').read_text()
contract=json.loads((r/'read-contract.json').read_text())
entries=[x for x in contract['entries'] if x['roleParameter']=='entity_role']
assert not (r/'pgdata').exists()
assert s.startswith('SET LOCAL jit = off;\n') and s.count(';')==1 and '--' not in s and '/*' not in s
refs=set('.'.join(x) for x in re.findall(r'\bfrom\s+(\w+)\."([^"]+)"',s))
assert refs=={x['table'] for x in entries}
plain=re.sub(r'"(?:[^"]|"")*"|\'(?:[^\']|\'\')*\'',' ',s)
allowed=set('GameConfiguration LOCAL SET a array_agg array_to_json as b c case coalesce config d data e else encode end f from g id is jit json json_build_object null off result row_to_json select then when where'.split())
assert set(re.findall(r'\b[A-Za-z_][A-Za-z_0-9]*\b',plain))<=allowed
assert set(re.findall(r'\b([a-zA-Z_]+)\s*\(',plain))==set('array_agg array_to_json coalesce encode from json_build_object row_to_json'.split())
depth=0;last={};projections=[]
for tok in re.finditer(r'"(?:[^"]|"")*"|\'(?:[^\']|\'\')*\'|[()]|\bselect\b|\bfrom\b',s):
 t=tok.group()
 if t=='(':depth+=1
 elif t==')':last.pop(depth,None);depth-=1
 elif t=='select':last[depth]=tok.end()
 elif t=='from':
  m=re.match(r'\s+(\w+)\."([^"]+)"(?:[ \t]+([a-g])\b)?',s[tok.end():])
  if not m:continue
  table=m[1]+'.'+m[2];e=next(x for x in entries if x['table']==table);proj=s[last[depth]:tok.start()];alias=m[3]
  if e['basis']=='fullRowProjectionTables':
   assert alias
   if table=='config.GameMapDefinition':
    prefix=proj.split(', (',1)[0];assert '.*' not in prefix
    columns=re.findall(r'\bb\."([^"]+)"',prefix)[1:]
    assert len(columns)==len(set(columns)) and set(columns)==set(e['selectColumns'])
    assert prefix.count('encode(')==1 and 'encode(b."TerrainData", \'base64\') as "TerrainData"' in prefix
   else:assert re.match(r'\s*'+alias+r'\."Id" as "\$id", '+alias+r'\.\*',proj)
  else:
   assert alias is None
   assert re.fullmatch(r'\s*"(?:'+ '|'.join(e['selectColumns'])+r')" as "\$ref"\s*',proj)
   tail=s[tok.end()+m.end():]
   where=re.match(r'\s*where "([^"]+)" = [a-g]\."Id"',tail)
   assert where and where[1] in e['selectColumns']
  projections.append(table)
assert set(projections)==refs and s.count('encode(')==1
observed=[]
for line in (r/'prepared-read-grants.sql').read_text().splitlines():
 if not line or line.startswith('--'):continue
 if re.fullmatch(r'GRANT USAGE ON SCHEMA "config"(?:, "data")? TO :"(?:entity|typed)_role";',line):continue
 m=re.fullmatch(r'GRANT SELECT \((.*)\) ON TABLE "([^"]+)"\."([^"]+)" TO :"(entity_role|typed_role)";',line);assert m,line
 cols=re.findall(r'"([^"]+)"',m[1]);assert len(cols)==len(set(cols));observed.append((m[4],m[2]+'.'+m[3],frozenset(cols)))
expected=[(x['roleParameter'],x['table'],frozenset(x['selectColumns'])) for x in contract['entries']]
assert len(observed)==len(expected) and set(observed)==set(expected)
counts=collections.Counter(x['basis'] for x in entries)
assert counts=={'fullRowProjectionTables':69,'joinColumnProjectionTables':12}
report={'status':'PASS_REVIEWED_BEFORE_DB_EXECUTION','gameQuerySha256':hashlib.sha256(s.encode()).hexdigest(),'gameQueryBytes':len(s.encode()),'fullRowTables':69,'joinTables':12,'physicalProjectionOccurrences':len(projections),'exactTableScope':True,'allowedExpressionsOnly':True,'binaryProjection':{'table':'config.GameMapDefinition','column':'TerrainData','encoding':'base64','occurrences':1,'allMappedColumnsExactlyOnce':True},'preparedGrantsExactContractMatch':True,'typedSqlGeneratedOnly':True,'authorizedActualReads':1,'actualReadType':'GameConfiguration','launchEnabled':False}
(r/'review-approved.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
