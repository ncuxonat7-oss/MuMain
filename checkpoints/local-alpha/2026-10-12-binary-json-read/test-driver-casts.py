from pathlib import Path
import ast, difflib, hashlib, json, re

root = Path(__file__).parent
r = root / 'handoff'
old = (r / 'run-database.py.before-cast-fix').read_text()
new = (r / 'run-database.py').read_text()
before = 'text|interval|boolean|integer|real|double precision'
after = before + '|character varying|uuid'
assert old.count(before) == 1
assert new == old.replace(before, after)
ast.parse(new)
patterns = [node.args[0].value for node in ast.walk(ast.parse(new))
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name) and node.func.value.id == 're'
            and node.func.attr == 'fullmatch']
assert len(patterns) == 1
pattern = patterns[0]
positive = ['0', '-42', '1.5', '-0.5', 'true', 'false', "'abc'::text",
            "'1 day'::interval", "'true'::boolean", "'42'::integer",
            "'1.5'::real", "'1.5'::double precision", "'it''s'::text",
            "'en'::character varying", "''::character varying",
            "'00000000-0000-0000-0000-000000000000'::uuid"]
negative = ['gen_random_uuid()', "nextval('sequence')", "('a' || 'b')::character varying",
            "'a'::text || 'b'::text", "'x'::custom_type", "'x'::public.uuid",
            "'x'::pg_catalog.uuid", "'x'::text::uuid", "'x'::uuid; SELECT 1",
            "'x'::uuid -- comment", "'x'::uuid/*comment*/", "/*comment*/'x'::uuid",
            "'x'::uuid\n", "'unterminated::uuid", "E'x'::character varying",
            "$$x$$::character varying", "'x'::character varying(3)", '1+2', '(SELECT 1)']
results = []
for expected, cases in [(True, positive), (False, negative)]:
    for value in cases:
        observed = re.fullmatch(pattern, value) is not None
        results.append({'input': value, 'expectedAccepted': expected, 'accepted': observed,
                        'status': 'PASS' if observed == expected else 'FAIL'})
assert all(x['status'] == 'PASS' for x in results)
# Recheck retained schema text only; never execute the driver or database here.
defaults = []
for line in (r / 'restored-schema-review.sql').read_text().splitlines():
    if ' DEFAULT ' in line:
        expression = line.split(' DEFAULT ', 1)[1].removesuffix(',').removesuffix(' NOT NULL')
        defaults.append(expression)
assert all(re.fullmatch(pattern, value) for value in defaults)
report = {'status': 'PASS', 'onlyApprovedTwoTypeAddition': True,
          'positiveCases': len(positive), 'negativeCases': len(negative), 'cases': results,
          'retainedSchemaDefaultsAccepted': len(defaults),
          'testsAreDriverGuardOnly': True,
          'originalDriverSha256': hashlib.sha256(old.encode()).hexdigest(),
          'correctedDriverSha256': hashlib.sha256(new.encode()).hexdigest()}
(root / 'driver-cast-tests.json').write_text(json.dumps(report, indent=2) + '\n')
(root / 'driver-cast-fix.diff').write_text(''.join(difflib.unified_diff(
    old.splitlines(True), new.splitlines(True), fromfile='run-database.py.before-cast-fix',
    tofile='run-database.py')))
print(json.dumps({key: value for key, value in report.items() if key != 'cases'}, indent=2))
