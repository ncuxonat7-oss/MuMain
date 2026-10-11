# Pure mocked guard tests only. No DB, processes, credentials or launcher activation.
#requires -Version 7.4
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$root=Split-Path (Split-Path $PSScriptRoot)
. (Join-Path $root 'scripts/windows11/Guards.ps1')
. (Join-Path $root 'scripts/windows11/Database.ps1')
$script:passed=0
function Check([string]$Name, [scriptblock]$Test) {
    & $Test
    $script:passed++
    Write-Output ('PASS ' + $Name)
}
function Require([bool]$Value) { if (!$Value) { throw 'ASSERTION_FAILED' } }
function Reject([scriptblock]$Test, [string]$Code='UNSAFE_CONFIG') {
    $caught=$false
    try { & $Test } catch { if ($_.Exception.Message -cne $Code) { throw }; $caught=$true }
    Require $caught
}
function New-Fixture {
    $c=Get-MuDatabaseSourceContract
    return @{ database=@{name='openmu';queryUser='probe';pgPassFile='private/probe.pgpass';
        systemIdentifier='1234567890123456789';runtimeRoles=@('runtime_game','runtime_admin');
        configurationIds=$c.configurationIds;migrationHistories=$c.migrationHistories};endpoints=$c.endpoints }
}
function New-Snapshot($Setup) {
    return @{database='openmu';port=5432;address='127.0.0.1';version='17.11';
        systems=@(@{id=(Get-MuDatabaseSourceContract).systemConfigurationId;readConsoleInput=$true;autoUpdateSchema=$false});
        configurationIds=$Setup.database.configurationIds;game=$Setup.endpoints.game;
        chat=$Setup.endpoints.chat;connect=$Setup.endpoints.connect}
}
function New-History($Setup,[string]$Context) {
    $h=$Setup.database.migrationHistories[$Context]
    return @{context=$Context;schema=$h.schema;table=$h.table;resolvedSchema=$h.schema;migrations=@($h.ids | ForEach-Object { @{id=$_;productVersion='10.0.2'} })}
}
Check 'exact source contracts accepted' { $s=New-Fixture; Assert-MuDatabaseShape $s.database }
Check 'both exact histories accepted separately' {
    $s=New-Fixture
    foreach ($c in @('EntityDataContext','AdminAuth.AdminPanelContext')) { Assert-MuHistory $s $c (New-History $s $c) }
}
Check 'old single-history manifest rejected' {
    $s=New-Fixture;$s.database.Remove('migrationHistories');$s.database.migrationSchema='public';$s.database.migrationIds=@('00000000000000_Initial')
    Reject { Assert-MuDatabaseShape $s.database }
}
Check 'missing admin contract rejected' { $s=New-Fixture;$s.database.migrationHistories.Remove('AdminAuth.AdminPanelContext');Reject {Assert-MuDatabaseShape $s.database} }
Check 'merged histories rejected' {
    $s=New-Fixture;$s.database.migrationHistories.EntityDataContext.ids+= $s.database.migrationHistories['AdminAuth.AdminPanelContext'].ids
    Reject {Assert-MuDatabaseShape $s.database}
}
Check 'extra game migration rejected' { $s=New-Fixture;$s.database.migrationHistories.EntityDataContext.ids+= '20990101000000_Unknown';Reject {Assert-MuDatabaseShape $s.database} }
Check 'missing game migration rejected' { $s=New-Fixture;$s.database.migrationHistories.EntityDataContext.ids=$s.database.migrationHistories.EntityDataContext.ids[1..62];Reject {Assert-MuDatabaseShape $s.database} }
Check 'duplicate migration rejected' { $s=New-Fixture;$s.database.migrationHistories.EntityDataContext.ids[1]=$s.database.migrationHistories.EntityDataContext.ids[0];Reject {Assert-MuDatabaseShape $s.database} }
Check 'wrong schema rejected' { $s=New-Fixture;$s.database.migrationHistories['AdminAuth.AdminPanelContext'].schema='public';Reject {Assert-MuDatabaseShape $s.database} }
Check 'schema interpolation injection rejected' { $s=New-Fixture;$s.database.migrationHistories.EntityDataContext.schema='public";DROP SCHEMA admin;--';Reject {Get-MuHistorySql $s 'EntityDataContext'} }
Check 'wrong history table rejected' { $s=New-Fixture;$s.database.migrationHistories.EntityDataContext.table='other';Reject {Assert-MuDatabaseShape $s.database} }
Check 'unknown context rejected' { $s=New-Fixture;Reject {Get-MuHistorySql $s 'UntrustedContext'} }
Check 'wrong configuration identity rejected' { $s=New-Fixture;$s.database.configurationIds=@('00000001-0002-0000-0000-000000000000');Reject {Assert-MuDatabaseShape $s.database} }
Check 'duplicate configuration identity rejected' { $s=New-Fixture;$s.database.configurationIds+= $s.database.configurationIds[0];Reject {Assert-MuDatabaseShape $s.database} }
Check 'scalar configuration identity rejected' { $s=New-Fixture;$s.database.configurationIds=$s.database.configurationIds[0];Reject {Assert-MuDatabaseShape $s.database} }
Check 'probe cannot also be runtime role' { $s=New-Fixture;$s.database.queryUser='runtime_game';Reject {Assert-MuDatabaseShape $s.database} }
Check 'snapshot expected settings accepted' { $s=New-Fixture;Assert-MuSnapshot $s (New-Snapshot $s) }
Check 'baseline AutoUpdateSchema true rejected' { $s=New-Fixture;$v=New-Snapshot $s;$v.systems[0].autoUpdateSchema=$true;Reject {Assert-MuSnapshot $s $v} }
Check 'baseline ReadConsoleInput false rejected' { $s=New-Fixture;$v=New-Snapshot $s;$v.systems[0].readConsoleInput=$false;Reject {Assert-MuSnapshot $s $v} }
Check 'string true cannot masquerade as bool' { $s=New-Fixture;$v=New-Snapshot $s;$v.systems[0].readConsoleInput='True';Reject {Assert-MuSnapshot $s $v} }
Check 'wrong system identity rejected' { $s=New-Fixture;$v=New-Snapshot $s;$v.systems[0].id='00000010-0001-0000-0000-000000000000';Reject {Assert-MuSnapshot $s $v} }
Check 'multiple system rows rejected' { $s=New-Fixture;$v=New-Snapshot $s;$v.systems+= $v.systems[0];Reject {Assert-MuSnapshot $s $v} }
Check 'observed configuration mismatch rejected' { $s=New-Fixture;$v=New-Snapshot $s;$v.configurationIds=@('00000001-0002-0000-0000-000000000000');Reject {Assert-MuSnapshot $s $v} }
Check 'empty admin history rejected despite good game history' {
    $s=New-Fixture;Assert-MuHistory $s 'EntityDataContext' (New-History $s 'EntityDataContext')
    $v=New-History $s 'AdminAuth.AdminPanelContext';$v.migrations=@();Reject {Assert-MuHistory $s 'AdminAuth.AdminPanelContext' $v}
}
Check 'admin missing migration rejected' { $s=New-Fixture;$v=New-History $s 'AdminAuth.AdminPanelContext';$v.migrations=@($v.migrations[0]);Reject {Assert-MuHistory $s 'AdminAuth.AdminPanelContext' $v} }
Check 'observed context spoof rejected' { $s=New-Fixture;$v=New-History $s 'AdminAuth.AdminPanelContext';$v.context='EntityDataContext';Reject {Assert-MuHistory $s 'AdminAuth.AdminPanelContext' $v} }
Check 'array history ID rejected before pipeline projection' { $s=New-Fixture;$v=New-History $s 'AdminAuth.AdminPanelContext';$v.migrations[0].id=@($v.migrations[0].id);Reject {Assert-MuHistory $s 'AdminAuth.AdminPanelContext' $v} }
Check 'null history ID rejected' { $s=New-Fixture;$v=New-History $s 'EntityDataContext';$v.migrations[0].id=$null;Reject {Assert-MuHistory $s 'EntityDataContext' $v} }
Check 'extra null ID row rejected' { $s=New-Fixture;$v=New-History $s 'EntityDataContext';$v.migrations+= @{id=$null;productVersion='10.0.2'};Reject {Assert-MuHistory $s 'EntityDataContext' $v} }
Check 'missing ProductVersion rejected' { $s=New-Fixture;$v=New-History $s 'EntityDataContext';$v.migrations[0].Remove('productVersion');Reject {Assert-MuHistory $s 'EntityDataContext' $v} }
Check 'null ProductVersion rejected' { $s=New-Fixture;$v=New-History $s 'AdminAuth.AdminPanelContext';$v.migrations[0].productVersion=$null;Reject {Assert-MuHistory $s 'AdminAuth.AdminPanelContext' $v} }
Check 'nonstring ProductVersion rejected' { $s=New-Fixture;$v=New-History $s 'EntityDataContext';$v.migrations[0].productVersion=10;Reject {Assert-MuHistory $s 'EntityDataContext' $v} }
Check 'empty ProductVersion rejected' { $s=New-Fixture;$v=New-History $s 'EntityDataContext';$v.migrations[0].productVersion='';Reject {Assert-MuHistory $s 'EntityDataContext' $v} }
Check 'both EF history columns queried' { $s=New-Fixture;$sql=Get-MuHistorySql $s 'EntityDataContext';Require ($sql.Contains('"MigrationId"'));Require ($sql.Contains('"ProductVersion"')) }
Check 'game default search path wrong resolution rejected' { $s=New-Fixture;$v=New-History $s 'EntityDataContext';$v.resolvedSchema='runtime_game';Reject {Assert-MuHistory $s 'EntityDataContext' $v} }
Check 'game default search path missing resolution rejected' { $s=New-Fixture;$v=New-History $s 'EntityDataContext';$v.resolvedSchema=$null;Reject {Assert-MuHistory $s 'EntityDataContext' $v} }
Check 'game SQL verifies actual unqualified resolution' { $s=New-Fixture;$sql=Get-MuHistorySql $s 'EntityDataContext';Require ($sql.Contains('pg_catalog.to_regclass'));Require ($sql.Contains('FROM "public"."__EFMigrationsHistory"')) }
Check 'admin SQL uses explicit schema' { $s=New-Fixture;$sql=Get-MuHistorySql $s 'AdminAuth.AdminPanelContext';Require ($sql.Contains('FROM "admin"."__EFMigrationsHistory"'));Require (!$sql.Contains('pg_catalog.to_regclass')) }
# Narrow mocks prevent every external dependency and record which actual context
# credentials the orchestration chooses. Password is an inert synthetic fixture.
function Get-MuConnections($Setup) {
    return @{'EntityDataContext'=@{user='runtime_game';password='fixture_only'};
        'AdminAuth.AdminPanelContext'=@{user='runtime_admin';password='fixture_only'}}
}
function Invoke-MuQuery($Setup,[string]$Sql,$Credential=$null,[switch]$PreserveSearchPath) {
    $u=if ($null -eq $Credential) {'probe'} else {$Credential.user}
    if ($Sql.Contains("'safe'")) {return @{user=$u;safe=$true}}
    if ($Sql.Contains("'resolvedSchema'")) {
        Require ([bool]$PreserveSearchPath)
        $c=if ($Sql.Contains("'AdminAuth.AdminPanelContext'")) {'AdminAuth.AdminPanelContext'} else {'EntityDataContext'}
        $script:calls+= ('{0}:{1}' -f $c,$u)
        if ($u -ceq 'runtime_admin' -and $script:adminDenied) {throw 'PROBE_FAILED'}
        return New-History $Setup $c
    }
    return New-Snapshot $Setup
}
Check 'both probe and correct runtime credential used per context' {
    $s=New-Fixture;$script:calls=@();$script:adminDenied=$false;Assert-MuDatabase $s
    Require (($script:calls -join '|') -ceq 'EntityDataContext:probe|EntityDataContext:runtime_game|AdminAuth.AdminPanelContext:probe|AdminAuth.AdminPanelContext:runtime_admin')
}
Check 'admin runtime ProductVersion SELECT denial blocks despite successful probe' {
    $s=New-Fixture;$script:calls=@();$script:adminDenied=$true;Reject {Assert-MuDatabase $s} 'PROBE_FAILED'
}
Write-Output ('PASS TOTAL ' + $script:passed)
