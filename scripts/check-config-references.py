#!/usr/bin/env python3
"""Validate exported PostgreSQL configuration references without running game clients."""
import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path


EXPORT_SQL = "-- Run on the existing restored PostgreSQL 17 database, not a new game initialization.\n-- psql -X -A -t -q -v ON_ERROR_STOP=1 -d openmu -f export-baseline-config.sql\n-- Output contains prototype configuration/item records; keep it in private evidence.\nBEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY;\n\\o baseline-config.jsonl\nSELECT format('SELECT json_build_object(''schema'', %L, ''table'', %L, ''row'', row_to_json(t))::text FROM %I.%I t;', schemaname, tablename, schemaname, tablename)\nFROM pg_tables\nWHERE schemaname = 'config' OR (schemaname = 'data' AND tablename = 'Item')\nORDER BY schemaname, tablename\n\\gexec\n\\o baseline-constraints.jsonl\nSELECT json_build_object(\n  'kind', CASE c.contype WHEN 'f' THEN 'foreign_key' ELSE 'primary_key' END,\n  'name', c.conname, 'schema', ns.nspname, 'table', cl.relname,\n  'columns', (SELECT json_agg(a.attname ORDER BY k.ordinality)\n              FROM unnest(c.conkey) WITH ORDINALITY k(attnum, ordinality)\n              JOIN pg_attribute a ON a.attrelid = c.conrelid AND a.attnum = k.attnum),\n  'target_schema', tn.nspname, 'target_table', tc.relname,\n  'target_columns', (SELECT json_agg(a.attname ORDER BY k.ordinality)\n                     FROM unnest(c.confkey) WITH ORDINALITY k(attnum, ordinality)\n                     JOIN pg_attribute a ON a.attrelid = c.confrelid AND a.attnum = k.attnum),\n  'match_type', c.confmatchtype::text\n)::text\nFROM pg_constraint c\nJOIN pg_class cl ON cl.oid = c.conrelid\nJOIN pg_namespace ns ON ns.oid = cl.relnamespace\nLEFT JOIN pg_class tc ON tc.oid = c.confrelid\nLEFT JOIN pg_namespace tn ON tn.oid = tc.relnamespace\nWHERE (ns.nspname = 'config' OR (ns.nspname = 'data' AND cl.relname = 'Item'))\n  AND (c.contype = 'p' OR (c.contype = 'f' AND tn.nspname = 'config'))\nORDER BY ns.nspname, cl.relname, c.conname;\n\\o\nCOMMIT;\n"


def read_lines(path):
    return [json.loads(line) for line in path.read_text(encoding='utf-8-sig').splitlines() if line.strip()]


def key(row, columns):
    return tuple(row[column] for column in columns)


def check_constraint(constraint, tables):
    table = (constraint['schema'], constraint['table'])
    if table not in tables:
        return {'constraint': constraint['name'], 'table': list(table), 'status': 'NOT_CHECKED', 'reason': 'No exported rows; empty table or missing export.'}
    rows = tables[table]
    columns = constraint['columns']
    problems = []
    if constraint['kind'] == 'primary_key':
        counts = Counter(key(row, columns) for row in rows)
        problems = [list(value) for value, count in counts.items() if count > 1 or None in value]
    else:
        target = (constraint['target_schema'], constraint['target_table'])
        target_keys = {key(row, constraint['target_columns']) for row in tables.get(target, [])}
        for row in rows:
            value = key(row, columns)
            nulls = sum(part is None for part in value)
            if nulls:
                if constraint['match_type'] == 'f' and nulls != len(value):
                    problems.append({'id': row.get('Id'), 'key': list(value), 'reason': 'Partially null MATCH FULL key'})
                continue
            if value not in target_keys:
                problems.append({'id': row.get('Id'), 'key': list(value), 'reason': 'Referenced row missing'})
    return {'constraint': constraint['name'], 'table': list(table), 'status': 'FAIL' if problems else 'PASS', 'rows': len(rows), 'problem_count': len(problems), 'problems': problems}


def run(evidence, output):
    tables = defaultdict(list)
    for record in read_lines(evidence / 'baseline-config.jsonl'):
        tables[(record['schema'], record['table'])].append(record['row'])
    constraints = read_lines(evidence / 'baseline-constraints.jsonl')
    if not constraints or not tables:
        raise ValueError('Configuration export or constraint metadata is empty.')
    results = [check_constraint(constraint, tables) for constraint in constraints]
    output.mkdir(parents=True, exist_ok=True)
    report = {'tables': {'.'.join(table): len(rows) for table, rows in sorted(tables.items())}, 'checks': results,
              'scope': 'Exported primary keys and database-declared references to config tables only. No client rendering, gameplay semantics, drop balance or event runtime proof.'}
    (output / 'config-reference-check.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    counts = Counter(result['status'] for result in results)
    print(json.dumps({'tables': len(tables), 'rows': sum(map(len, tables.values())), 'results': dict(counts)}))
    return int(bool(counts['FAIL']))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--export-sql', type=Path, help='Write read-only SQL for existing PostgreSQL 17 instance; does not connect.')
    parser.add_argument('--evidence', type=Path)
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    if args.export_sql:
        args.export_sql.write_text(EXPORT_SQL, encoding='utf-8')
        raise SystemExit(0)
    if not args.evidence or not args.out:
        parser.error('--evidence and --out are required unless --export-sql is used')
    raise SystemExit(run(args.evidence, args.out))
