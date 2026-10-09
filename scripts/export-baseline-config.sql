-- Run on the existing restored PostgreSQL 17 database, not a new game initialization.
-- psql -X -A -t -q -v ON_ERROR_STOP=1 -d openmu -f export-baseline-config.sql
-- Output contains prototype configuration/item records; keep it in private evidence.
BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY;
\o baseline-config.jsonl
SELECT format('SELECT json_build_object(''schema'', %L, ''table'', %L, ''row'', row_to_json(t))::text FROM %I.%I t;', schemaname, tablename, schemaname, tablename)
FROM pg_tables
WHERE schemaname = 'config' OR (schemaname = 'data' AND tablename = 'Item')
ORDER BY schemaname, tablename
\gexec
\o baseline-constraints.jsonl
SELECT json_build_object(
  'kind', CASE c.contype WHEN 'f' THEN 'foreign_key' ELSE 'primary_key' END,
  'name', c.conname, 'schema', ns.nspname, 'table', cl.relname,
  'columns', (SELECT json_agg(a.attname ORDER BY k.ordinality)
              FROM unnest(c.conkey) WITH ORDINALITY k(attnum, ordinality)
              JOIN pg_attribute a ON a.attrelid = c.conrelid AND a.attnum = k.attnum),
  'target_schema', tn.nspname, 'target_table', tc.relname,
  'target_columns', (SELECT json_agg(a.attname ORDER BY k.ordinality)
                     FROM unnest(c.confkey) WITH ORDINALITY k(attnum, ordinality)
                     JOIN pg_attribute a ON a.attrelid = c.confrelid AND a.attnum = k.attnum),
  'match_type', c.confmatchtype::text
)::text
FROM pg_constraint c
JOIN pg_class cl ON cl.oid = c.conrelid
JOIN pg_namespace ns ON ns.oid = cl.relnamespace
LEFT JOIN pg_class tc ON tc.oid = c.confrelid
LEFT JOIN pg_namespace tn ON tn.oid = tc.relnamespace
WHERE (ns.nspname = 'config' OR (ns.nspname = 'data' AND cl.relname = 'Item'))
  AND (c.contype = 'p' OR (c.contype = 'f' AND tn.nspname = 'config'))
ORDER BY ns.nspname, cl.relname, c.conname;
\o
COMMIT;
