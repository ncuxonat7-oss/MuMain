param(
    [Parameter(Mandatory = $true)][string]$PgBin,
    [Parameter(Mandatory = $true)][string]$Evidence,
    [Parameter(Mandatory = $true)][ValidatePattern('^[a-zA-Z0-9-]{1,40}$')][string]$Stage
)

$ErrorActionPreference = 'Stop'
# Fixed read-only evidence for the approved actor; no caller-supplied SQL/identity.
$sql = @'
BEGIN TRANSACTION READ ONLY;
SELECT json_build_object(
  'character_id', '511da101-0000-7171-e6b7-6ed8654174ee',
  'actor_exists', EXISTS (SELECT 1 FROM data."Character"
    WHERE "Id" = '511da101-0000-7171-e6b7-6ed8654174ee' AND "Name" = 'test300Dk'),
  'skill_count', count(*),
  'skills', COALESCE(json_agg(row_to_json(s) ORDER BY s."SkillId", s."Id"), '[]'::json))
FROM data."SkillEntry" s
WHERE s."CharacterId" = '511da101-0000-7171-e6b7-6ed8654174ee';
COMMIT;
'@
$outputPath = Join-Path $Evidence "$Stage-skill41.json"
& "$PgBin/psql.exe" -X -q -h 127.0.0.1 -U postgres -d openmu -t -A -v ON_ERROR_STOP=1 -c $sql > $outputPath
if ($LASTEXITCODE) { throw 'Fixed read-only SkillEntry capture failed' }
$snapshot = Get-Content $outputPath -Raw | ConvertFrom-Json
if (!$snapshot.actor_exists -or $snapshot.skill_count -ne @($snapshot.skills).Count) {
    throw 'Skill41 capture identity/count guard failed'
}
if ($Stage -eq 'ready' -and @($snapshot.skills | Where-Object { $_.SkillId -eq '00000400-0029-0000-0000-000000000000' }).Count -gt 0) {
    throw 'STOP: skill 41 already exists; preserve evidence, no learning or replacement fixture'
}
