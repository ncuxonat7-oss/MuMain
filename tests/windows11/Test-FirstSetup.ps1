# New first-setup mock-only checks. No DB utility, credentials, ACL or OS mutation.
# Downstream orchestration is simulated; the real pinned grant gate is tested first.
#requires -Version 7.4
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$root=Split-Path (Split-Path $PSScriptRoot)
. (Join-Path $root 'scripts/windows11/Guards.ps1')
. (Join-Path $root 'scripts/windows11/Database.ps1')
. (Join-Path $root 'scripts/windows11/FirstSetup.ps1')
$script:passed=0;$script:utilityCalls=@()
function Check([string]$Name,[scriptblock]$Test) { & $Test;$script:passed++;Write-Output ('PASS '+$Name) }
function Require([bool]$Value) { if (!$Value) {throw 'ASSERTION_FAILED'} }
function Reject([scriptblock]$Test,[string]$Code) {
    $caught=$false;try {& $Test} catch {if ($_.Exception.Message -cne $Code) {throw};$caught=$true};Require $caught
}
function New-Request {
    return @{packageRoot=[IO.Path]::GetFullPath('/mock/package');setupRelative='database/setup-test';
        archive=[IO.Path]::GetFullPath('/mock/baseline.zip');credentialBundle=[IO.Path]::GetFullPath('/mock/owner-input.json');
        confirmNewDatabase=$true;confirmCredentialHandling=$true;applyReviewedFlags=$true}
}
function Invoke-MuSetupUtility($State,$Tool,$Arguments,$InputSql='',$Seconds=30,[switch]$DaemonStart) {
    $script:utilityCalls+=@{tool=$Tool;arguments=$Arguments;stdin=$InputSql;seconds=$Seconds;daemon=[bool]$DaemonStart}
    return ''
}
Check 'pinned real policy remains blocked' { Require ((Get-MuFirstSetupPolicy).runtimeGrantStatus -ceq 'BLOCKED_SOURCE_BINARY_ALIGNMENT') }
Check 'real entry stops before any filesystem credential or utility stage' {
    $script:utilityCalls=@();$r=Invoke-MuFirstSetup (New-Request)
    Require ($r.status -ceq 'BLOCKED_RUNTIME_GRANTS');Require ($r.stage -ceq 'runtime-grants')
    Require (!$r.databaseReady);Require (!$r.launchEnabled);Require ($null -eq $r.approvedLaunchManifestSha256)
    Require ($null -eq $r.setupDirectory);Require ($script:utilityCalls.Count -eq 0)
}
Check 'status-only grant approval cannot enable incomplete grant implementation' {
    Reject {Set-MuSetupRuntimeGrants @{policy=@{runtimeGrantStatus='APPROVED_FOR_DEPLOYMENT';runtimeSourceStatus='REVIEWED';runtimeBinaryAlignment=$true;liveValidationStatus='PASSED'}}} 'RUNTIME_GRANTS_UNRESOLVED'
}
foreach ($case in @(
    @{runtimeSourceStatus='PATCH_REVIEW_ONLY';runtimeBinaryAlignment=$true;liveValidationStatus='PASSED'},
    @{runtimeSourceStatus='REVIEWED';runtimeBinaryAlignment=$false;liveValidationStatus='PASSED'},
    @{runtimeSourceStatus='REVIEWED';runtimeBinaryAlignment='true';liveValidationStatus='PASSED'},
    @{runtimeSourceStatus='REVIEWED';runtimeBinaryAlignment=$true;liveValidationStatus='NOT_RUN'}
)) {
    Check ('source binary validation gate: '+($case.Values -join ',')) {
        $case.runtimeGrantStatus='APPROVED_FOR_DEPLOYMENT'
        Reject {Assert-MuSetupGrantPolicy $case} 'SOURCE_BINARY_VALIDATION_REQUIRED'
    }
}
function New-MockConnectionXml([string]$Extra='') {
    [xml]$xml='<Connection xmlns="http://www.munique.net/ConnectionSettings"><ContextTypeName>placeholder</ContextTypeName><ConnectionString>placeholder</ConnectionString><DatabaseEngine>Npgsql</DatabaseEngine>'+ $Extra +'</Connection>'
    return $xml.DocumentElement
}
Check 'external admin schema mode explicitly accepted' {
    Assert-MuConnectionSchemaMode (New-MockConnectionXml '<AdminSchemaManagement>ExternallyProvisioned</AdminSchemaManagement>') 'AdminAuth.AdminPanelContext'
}
foreach ($extra in @('','<AdminSchemaManagement>RuntimeMigrations</AdminSchemaManagement>',
    '<AdminSchemaManagement>externallyprovisioned</AdminSchemaManagement>',
    '<AdminSchemaManagement>ExternallyProvisioned</AdminSchemaManagement><AdminSchemaManagement>ExternallyProvisioned</AdminSchemaManagement>',
    '<AdminSchemaManagement xmlns="wrong">ExternallyProvisioned</AdminSchemaManagement>')) {
    Check ('invalid admin mode rejected: '+$extra) { Reject {Assert-MuConnectionSchemaMode (New-MockConnectionXml $extra) 'AdminAuth.AdminPanelContext'} 'UNSAFE_CONFIG' }
}
Check 'other connection legacy shape remains accepted' { Assert-MuConnectionSchemaMode (New-MockConnectionXml) 'EntityDataContext' }
Check 'admin mode cannot be applied to unrelated context' {
    Reject {Assert-MuConnectionSchemaMode (New-MockConnectionXml '<AdminSchemaManagement>ExternallyProvisioned</AdminSchemaManagement>') 'EntityDataContext'} 'UNSAFE_CONFIG'
}
foreach ($key in @('confirmNewDatabase','confirmCredentialHandling','applyReviewedFlags')) {
    Check ('explicit approval required: '+$key) { $r=New-Request;$r[$key]=$false;Reject {Assert-MuSetupRequest $r} 'SETUP_APPROVAL_REQUIRED' }
}
Check 'string approval is not a boolean approval' { $r=New-Request;$r.confirmNewDatabase='true';Reject {Assert-MuSetupRequest $r} 'SETUP_APPROVAL_REQUIRED' }
foreach ($bad in @('../existing','database/../existing','server','database/setup-X','database/setup-test/cluster','database/setup-')) {
    Check ('unsafe dedicated destination rejected: '+$bad) { $r=New-Request;$r.setupRelative=$bad;Reject {Assert-MuSetupRequest $r} 'UNSAFE_CONFIG' }
}
Check 'relative input paths rejected' { $r=New-Request;$r.archive='baseline.zip';Reject {Assert-MuSetupRequest $r} 'UNSAFE_CONFIG' }
Check 'unexpected request field rejected' { $r=New-Request;$r.force=$true;Reject {Assert-MuSetupRequest $r} 'UNSAFE_CONFIG' }
Check 'source snapshot and SQL_ASCII identity retained' {
    $p=Get-MuFirstSetupPolicy;Require ($p.archiveBytes -eq 2091291);Require ($p.dumpBytes -eq 1367029)
    Require ($p.encoding -ceq 'SQL_ASCII');Require ($p.locale -ceq 'C');Require (!$p.launchEnabled)
}
Check 'sanitized journal has only fixed fields' {
    $s=@{events=@();journalReady=$false};Write-MuSetupEvent $s 'restore' 'failed'
    Require (($s.events[0].Keys | Sort-Object) -join ',' -ceq 'result,stage,utc')
}
Check 'raw error cannot be used as journal stage' {
    $s=@{events=@();journalReady=$false};Reject {Write-MuSetupEvent $s 'PASSWORD=not-a-log-value' 'failed'} 'UNSAFE_CONFIG'
}
Check 'journal has bounded event count' {
    $s=@{events=@(1..64);journalReady=$false};Reject {Write-MuSetupEvent $s 'restore' 'failed'} 'SETUP_JOURNAL_LIMIT'
}
Check 'flag transaction changes exactly reviewed columns and checks other fields' {
    $sql=Get-MuSetupFlagsSql
    Require ($sql.Contains('BEGIN;'));Require ($sql.Contains('COMMIT;'));Require ($sql.Contains('LOCK TABLE config."SystemConfiguration"'))
    Require ($sql.Contains('SET "ReadConsoleInput"=true,"AutoUpdateSchema"=false'))
    Require ($sql.Contains('before_other IS DISTINCT FROM after_other'));Require ($sql.Contains('changed<>1'))
    Require ($sql.Contains('00000010-0000-0000-0000-000000000000'))
    Require ($sql.Contains("SETUP_FLAG_AFTER"));Require ($sql.Contains('AND "ReadConsoleInput"=true AND "AutoUpdateSchema"=false'))
}
Check 'known grant subset never gives owner or schema CREATE to runtime' {
    $sql=Get-MuSetupKnownGrantsSql
    Require (!$sql.Contains('GRANT ALL'));Require (!$sql.Contains('GRANT CREATE'))
    Require (!$sql.Contains('TO mu_entity;'));Require (!$sql.Contains('TO mu_typed;'))
    Require ($sql.Contains('GRANT SELECT ("Id") ON config."GameConfiguration" TO mu_probe'))
}
function Assert-MuSetupPgOwner($State) { if ($script:ownerLost) {throw 'OWNER_LOST'} }
$script:ownerLost=$false
Check 'restore targets only fixed database with no overwrite or owner restore' {
    $script:utilityCalls=@();Restore-MuSetupSnapshot @{dump='/mock/baseline.dump'}
    $x=$script:utilityCalls[0];Require ($x.tool -ceq 'pg_restore');Require ($x.seconds -eq 180)
    foreach ($v in @('--single-transaction','--no-owner','--no-acl','--role=mu_owner','openmu')) {Require ($v -in $x.arguments)}
    Require ('--clean' -notin $x.arguments);Require ('--create' -notin $x.arguments)
}
Check 'restore refuses unknown process ownership' {
    $script:utilityCalls=@();$script:ownerLost=$true;Reject {Restore-MuSetupSnapshot @{dump='/mock/baseline.dump'}} 'OWNER_LOST'
    Require ($script:utilityCalls.Count -eq 0);$script:ownerLost=$false
}
function Set-Content {param($LiteralPath,$Encoding,[Parameter(ValueFromPipeline)]$Value) process { } }
Check 'initdb command uses SCRAM and preserved encoding without trust' {
    $script:utilityCalls=@();Initialize-MuSetupCluster @{pgData='/mock/cluster';bootstrapPassword='/mock/bootstrap.pw'}
    $x=$script:utilityCalls[0];Require ($x.tool -ceq 'initdb')
    foreach ($v in @('--auth-local=scram-sha-256','--auth-host=scram-sha-256','--encoding=SQL_ASCII','--locale=C')) {Require ($v -in $x.arguments)}
    Require ('trust' -notin $x.arguments)
}
Check 'role passwords travel only through stdin and never arguments' {
    $script:utilityCalls=@();$credentials=@{}
    foreach ($n in @('mu_entity','mu_typed','mu_admin','mu_account','mu_config','mu_friend','mu_guild','mu_probe')) {$credentials[$n]='MOCK_ONLY_NOT_A_REAL_SECRET_12345678'}
    New-MuSetupRolesAndDatabase @{credentials=$credentials}
    $x=$script:utilityCalls[0];Require (!$x.arguments.Contains('MOCK_ONLY_NOT_A_REAL_SECRET_12345678'))
    Require ($x.stdin.Contains('NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS'))
    Require ($x.stdin.Contains('CREATE DATABASE openmu OWNER mu_owner TEMPLATE template0'))
}
# Simulated future resolved policy: every potentially mutating stage is replaced.
# These tests prove control flow only, not Windows implementations or safe grants.
function Assert-MuSetupGrantPolicy($Policy) { }
$script:calls=@();$script:failAt='';$script:failStop=$false
function Hit($State,[string]$Name) { $script:calls+=$Name;if ($script:failAt -ceq $Name) {throw 'MOCK_ONLY_SECRET_MUST_NOT_LEAK'} }
function Assert-MuSetupHostAndInputs($State) {Hit $State 'preflight';$State.directory='/mock/new-setup'}
function Initialize-MuSetupPrivateArea($State) {Hit $State 'private-area'}
function Read-MuSetupCredentials($State) {Hit $State 'credentials';$State.credentials=@{private='MOCK_ONLY_SECRET_MUST_NOT_LEAK'}}
function Expand-MuSetupDump($State) {Hit $State 'dump'}
function Initialize-MuSetupCluster($State) {Hit $State 'initialize'}
function Start-MuSetupCluster($State) {$State.pgStartAttempted=$true;Hit $State 'start';$State.pgOwner=@{pid=42;ticks=1}}
function New-MuSetupRolesAndDatabase($State) {Hit $State 'roles'}
function Restore-MuSetupSnapshot($State) {Hit $State 'restore'}
function Set-MuSetupRuntimeGrants($State) {Hit $State 'grants'}
function Set-MuSetupReviewedFlags($State) {Hit $State 'flags'}
function Prepare-MuSetupAcceptance($State) {Hit $State 'prepare-acceptance';$State.acceptanceSetup=@{}}
function Test-MuSetupReadOnlyAcceptance($State) {Hit $State 'acceptance'}
function Seal-MuSetupPrivateOutput($State) {Hit $State 'seal'}
function Stop-MuSetupCluster($State) {$script:calls+='stop';if ($script:failStop) {throw 'OWNER_LOST'};$State.pgOwner=$null;$State.pgStopped=$true}
Check 'simulated complete sequence stays launch-disabled' {
    $script:calls=@();$script:failAt='';$r=Invoke-MuFirstSetup (New-Request)
    Require ($r.status -ceq 'DB_PREPARED_LAUNCH_DISABLED');Require (!$r.launchEnabled)
    Require (($script:calls -join ',') -ceq 'preflight,private-area,credentials,dump,initialize,start,roles,restore,grants,flags,prepare-acceptance,acceptance,seal,stop')
}
foreach ($stage in @('preflight','private-area','credentials','dump','initialize')) {
    Check ('failure before PG start never stops any cluster: '+$stage) {
        $script:calls=@();$script:failAt=$stage;$r=Invoke-MuFirstSetup (New-Request)
        Require (!$r.databaseReady);Require ('stop' -notin $script:calls)
        Require (!(($r | ConvertTo-Json -Depth 10).Contains('MOCK_ONLY_SECRET_MUST_NOT_LEAK')))
    }
}
Check 'uncertain failed PG start retained for owner review' {
    $script:calls=@();$script:failAt='start';$r=Invoke-MuFirstSetup (New-Request)
    Require ($r.status -ceq 'FAILED_OWNER_REVIEW_REQUIRED');Require ('stop' -notin $script:calls)
}
foreach ($stage in @('roles','restore','grants','flags','prepare-acceptance','acceptance','seal')) {
    Check ('owned setup failure stops owned PG and retains directory: '+$stage) {
        $script:calls=@();$script:failAt=$stage;$r=Invoke-MuFirstSetup (New-Request)
        Require ($r.status -ceq 'FAILED_RETAINED');Require ($script:calls[-1] -ceq 'stop');Require (!$r.databaseReady)
        Require (!(($r | ConvertTo-Json -Depth 10).Contains('MOCK_ONLY_SECRET_MUST_NOT_LEAK')))
    }
}
Check 'ownership lost during cleanup retains for owner review' {
    $script:calls=@();$script:failAt='restore';$script:failStop=$true;$r=Invoke-MuFirstSetup (New-Request)
    Require ($r.status -ceq 'FAILED_OWNER_REVIEW_REQUIRED');Require (!$r.launchEnabled);$script:failStop=$false
}
# Exercise the exact final PG config allowlist change without filesystem/Windows I/O.
function Resolve-MuFile($Root,$Relative) {return [IO.Path]::Combine('/mock',$Relative)}
function Get-Content {param($LiteralPath,[switch]$Raw) return '17'}
function Get-ChildItem {param($LiteralPath,[switch]$Recurse,[switch]$Force) return @()}
$script:logStatement='none';$script:logMinError='panic'
function Read-MuConfigLines($Path) {
    if ($Path.EndsWith('postgresql.conf')) {return @("listen_addresses = '127.0.0.1'","port = 5432","password_encryption = 'scram-sha-256'","log_statement = '$script:logStatement'","log_min_error_statement = '$script:logMinError'")}
    if ($Path.EndsWith('pg_hba.conf')) {return @('host openmu mu_entity 127.0.0.1/32 scram-sha-256','host openmu mu_probe 127.0.0.1/32 scram-sha-256')}
    return @()
}
$loggingSetup=@{root='/mock';pgData='database/cluster';hashes=@{};database=@{name='openmu';runtimeRoles=@('mu_entity');queryUser='mu_probe'}}
Check 'sealed statement-log suppression accepted by exact launcher allowlist' {Assert-MuPostgresConfig $loggingSetup}
Check 'statement logging cannot be enabled through added config keys' {$script:logStatement='all';Reject {Assert-MuPostgresConfig $loggingSetup} 'UNSAFE_CONFIG';$script:logStatement='none'}
Check 'error statement logging cannot be enabled through added config keys' {$script:logMinError='error';Reject {Assert-MuPostgresConfig $loggingSetup} 'UNSAFE_CONFIG';$script:logMinError='panic'}
Write-Output ('PASS TOTAL '+$script:passed)
