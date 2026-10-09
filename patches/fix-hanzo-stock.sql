\set ON_ERROR_STOP on
BEGIN;
LOCK TABLE data."Item" IN SHARE ROW EXCLUSIVE MODE;
CREATE TEMP TABLE baseline_item_before AS SELECT "Id", to_jsonb(i) AS record FROM data."Item" i;
DO $$
DECLARE target data."Item"%ROWTYPE;
BEGIN
  SELECT * INTO STRICT target FROM data."Item" WHERE "Id"='511da101-0000-7e0d-4efa-d1d99c7aa175';
  IF target."DefinitionId" <> '00000080-0000-0007-0000-000000000000'
     OR target."ItemStorageId" <> '00001000-00fb-0000-0000-000000000000'
     OR target."ItemSlot" NOT IN (73,76) THEN
    RAISE EXCEPTION 'Hanzo Falchion identity/storage/slot differs; refusing mutation';
  END IF;
  IF EXISTS (
    SELECT 1 FROM data."Item" i JOIN config."ItemDefinition" d ON d."Id"=i."DefinitionId"
    CROSS JOIN LATERAL generate_series(0,d."Width"-1) dx
    CROSS JOIN LATERAL generate_series(0,d."Height"-1) dy
    WHERE i."ItemStorageId"=target."ItemStorageId" AND i."Id"<>target."Id"
      AND mod(i."ItemSlot",8)+dx=4 AND i."ItemSlot"/8+dy BETWEEN 9 AND 11
  ) THEN RAISE EXCEPTION 'Reviewed replacement rectangle at76 is not empty'; END IF;
END $$;
UPDATE data."Item" SET "ItemSlot"=76
WHERE "Id"='511da101-0000-7e0d-4efa-d1d99c7aa175' AND "ItemSlot"=73;
DO $$
BEGIN
  IF EXISTS (
    SELECT 1 FROM baseline_item_before b FULL JOIN data."Item" i ON i."Id"=b."Id"
    WHERE b."Id" IS NULL OR i."Id" IS NULL OR
      CASE WHEN b."Id"='511da101-0000-7e0d-4efa-d1d99c7aa175'
           THEN b.record-'ItemSlot' IS DISTINCT FROM to_jsonb(i)-'ItemSlot'
           ELSE b.record IS DISTINCT FROM to_jsonb(i) END
  ) THEN RAISE EXCEPTION 'Unexpected item insertion/deletion/change'; END IF;
END $$;
SELECT 'HANZO_SLOT_76_VERIFIED' AS status, count(*) AS target_count
FROM data."Item" WHERE "Id"='511da101-0000-7e0d-4efa-d1d99c7aa175' AND "ItemSlot"=76;
COMMIT;
