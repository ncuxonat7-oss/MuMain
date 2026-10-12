# Mock-only admin setup checks. No process, PostgreSQL, credential or migration execution.
#requires -Version 7.4
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$root=Split-Path (Split-Path $PSScriptRoot)
. (Join-Path $root 'scripts/windows11/Guards.ps1')
. (Join-Path $root 'scripts/windows11/Database.ps1')
. (Join-Path $root 'scripts/windows11/FirstSetup.ps1')
$script:passed=0
function Check([string]$Name,[scriptblock]$Test) { & $Test;$script:passed++;Write-Output ('PASS '+$Name) }
function Require([bool]$Value) { if (!$Value) {throw 'ASSERTION_FAILED'} }
function Reject([scriptblock]$Test,[string]$Code) {
    $caught=$false;try {& $Test} catch {if ($_.Exception.Message -cne $Code) {throw};$caught=$true};Require $caught
}
function Invoke-MuSetupUtility {throw 'REAL_UTILITY_FORBIDDEN'}
$contract=Get-MuAdminProvisioningContract
$source=Get-MuDatabaseSourceContract
function New-State {
    return @{request=@{packageRoot=$root};stage='admin-provision';pgOwner=@{pid=42;ticks=1};pgStartAttempted=$true;
        pgStopped=$false;pgData='/mock/owned-cluster';dump='/mock/baseline.dump';
        policy=Get-MuFirstSetupPolicy;inventory=@{'server/MUnique.OpenMU.Persistence.EntityFramework.dll'=@{sha256=$contract.persistenceSha256}}}
}
Check 'real contract pins independently verified candidate and migrations' {
    Require ($contract.productVersion -ceq '10.0.2')
    Require ($contract.persistenceSha256 -ceq 'f12b509a8e99453bec482049cc92c2ec677c424accf6e3b019c155c342437014')
    Assert-MuExactStrings $contract.migrationIds $source.migrationHistories['AdminAuth.AdminPanelContext'].ids '^[0-9]{14}_[A-Za-z0-9_]+$'
}
Check 'real SQL files exactly match reviewed original minus BOM' {
    $sql=Read-MuReviewedAdminSql (New-State) $contract
    Require ($sql.StartsWith('DO $EF$'));Require ($sql.Contains("'20260829110159_AddApiKeys', '10.0.2'"))
    Require (!$sql.Contains('CREATE ROLE'));Require (!$sql.Contains('GRANT '))
}
foreach ($field in @('originalSqlSha256','executionSqlSha256')) {
    Check ('changed SQL hash rejected: '+$field) {
        $bad=$contract.Clone();$bad[$field]='0'*64
        Reject {Read-MuReviewedAdminSql (New-State) $bad} 'HASH_MISMATCH'
    }
}
Check 'missing SQL refuses before utility calls' {
    $s=New-State;$s.request.packageRoot=Join-Path $root 'tests'
    $caught=$false;try {Read-MuReviewedAdminSql $s $contract} catch {$caught=$true};Require $caught
}
Check 'real policy blocks direct provisioning operation' {
    Reject {Invoke-MuSetupAdminProvisioning (New-State)} 'RUNTIME_GRANTS_UNRESOLVED'
}
Check 'real grant setter still independently blocks approved status' {
    Reject {Set-MuSetupRuntimeGrants @{policy=@{runtimeGrantStatus='APPROVED_FOR_DEPLOYMENT';runtimeSourceStatus='REVIEWED';runtimeBinaryAlignment=$true;liveValidationStatus='PASSED'}}} 'RUNTIME_GRANTS_UNRESOLVED'
}
Check 'launch contract remains disabled and unapproved' {
    $c=Read-MuJson (Join-Path $root 'scripts/windows11/local-session-contract.json')
    Require ($c.launchEnabled -eq $false);Require ($null -eq $c.approvedLaunchManifestSha256)
}
# Only external artifact location/hash checks are mocked; SQL and contract bytes stay real.
$script:realHash=${function:Assert-MuFileHash};$script:realResolve=${function:Resolve-MuFile}
$script:binaryBad=$false
function Resolve-MuFile($Root,$Relative) {
    if ($Relative -ceq 'server/MUnique.OpenMU.Persistence.EntityFramework.dll') {return '/mock/candidate.dll'}
    return & $script:realResolve $Root $Relative
}
function Assert-MuFileHash($Path,$Hash) {
    if ($Path -ceq '/mock/candidate.dll') {if ($script:binaryBad) {throw 'HASH_MISMATCH'};Require ($Hash -ceq $contract.persistenceSha256);return}
    if ($Path -ceq '/mock/baseline.dump') {Require ($Hash -ceq '0a4b0744cb9be77c8f53a6f4a73e729402d17382069ba93261d394cbadf19478');return}
    & $script:realHash $Path $Hash
}
Check 'source and actual candidate artifact checks precede any SQL' {$null=Assert-MuAdminProvisioningInputs (New-State) $contract}
foreach ($pair in @(@('stage','grants'),@('pgOwner',$null),@('pgStartAttempted',$false),@('pgStopped',$true))) {
    Check ('requires owned setup stage: '+$pair[0]) {
        $s=New-State;$s[$pair[0]]=$pair[1];Reject {Assert-MuAdminProvisioningInputs $s $contract} 'ADMIN_SETUP_REQUIRED'
    }
}
Check 'old packaged binary metadata rejected' {
    $s=New-State;$s.inventory.Values | ForEach-Object {$_.sha256='f05e117d596f6bb74f953d8b4cbe83c73c0b30a6acf94876b6e8619bf92f1042'}
    Reject {Assert-MuAdminProvisioningInputs $s $contract} 'ADMIN_BINARY_MISMATCH'
}
Check 'actual binary mismatch rejected despite matching inventory' {
    $script:binaryBad=$true;try {Reject {Assert-MuAdminProvisioningInputs (New-State) $contract} 'HASH_MISMATCH'} finally {$script:binaryBad=$false}
}
foreach ($count in @(0,2)) {
    Check ('requires one unambiguous candidate file: '+$count) {
        $s=New-State;if ($count -eq 0) {$s.inventory=@{}} else {$s.inventory['other/MUnique.OpenMU.Persistence.EntityFramework.dll']=@{sha256=$contract.persistenceSha256}}
        Reject {Assert-MuAdminProvisioningInputs $s $contract} 'ADMIN_BINARY_MISMATCH'
    }
}
function New-Snapshot([bool]$After=$false) {
    $admin=if ($After) {@($contract.migrationIds | ForEach-Object {@{MigrationId=$_;ProductVersion=$contract.productVersion}})} else {$null}
    return @{database='openmu';sessionUser='mu_setup';currentUser='mu_setup';directory='/mock/owned-cluster';encoding='SQL_ASCII';locale='C';ctype='C';adminAbsent=!$After;
        game=@($source.migrationHistories.EntityDataContext.ids | ForEach-Object {@{MigrationId=$_;ProductVersion='MOCK_VERSION'}});
        configurationIds=@($source.configurationIds);system=@(@{Id=$source.systemConfigurationId;AutoStart=$true;AutoUpdateSchema=$true;ReadConsoleInput=$false});admin=$admin}
}
Check 'independent restored target accepted before schema creation' {Assert-MuAdminTarget (New-State) (New-Snapshot) $source}
foreach ($key in @('database','sessionUser','currentUser','directory','encoding','locale','ctype')) {
    Check ('wrong target rejected: '+$key) {
        $s=New-Snapshot;$s[$key]=if ($key -ceq 'directory') {'/mock/other-cluster'} else {'wrong'}
        Reject {Assert-MuAdminTarget (New-State) $s $source} 'ADMIN_TARGET_MISMATCH'
    }
}
foreach ($value in @($false,'true')) {
    Check ('existing or malformed schema state rejected: '+$value) {
        $s=New-Snapshot;$s.adminAbsent=$value;Reject {Assert-MuAdminTarget (New-State) $s $source} 'ADMIN_SCHEMA_STATE_MISMATCH'
    }
}
Check 'runtime admin authority rejected' {
    $s=New-Snapshot;$s.currentUser='mu_admin';$s.sessionUser='mu_admin'
    Reject {Assert-MuAdminTarget (New-State) $s $source} 'ADMIN_TARGET_MISMATCH'
}
Check 'partial game history rejected' {$s=New-Snapshot;$s.game=$s.game[1..62];Reject {Assert-MuAdminTarget (New-State) $s $source} 'UNSAFE_CONFIG'}
Check 'duplicate game migration rejected' {$s=New-Snapshot;$s.game[1]=$s.game[0];Reject {Assert-MuAdminTarget (New-State) $s $source} 'UNSAFE_CONFIG'}
Check 'wrong configuration ID rejected' {$s=New-Snapshot;$s.configurationIds=@('00000000-0000-0000-0000-000000000000');Reject {Assert-MuAdminTarget (New-State) $s $source} 'UNSAFE_CONFIG'}
foreach ($key in @('AutoStart','AutoUpdateSchema','ReadConsoleInput')) {
    Check ('original flag required: '+$key) {$s=New-Snapshot;$s.system[0][$key]=!$s.system[0][$key];Reject {Assert-MuAdminTarget (New-State) $s $source} 'ADMIN_BASELINE_MISMATCH'}
}
Check 'extra system configuration rejected' {$s=New-Snapshot;$s.system+=@($s.system[0]);Reject {Assert-MuAdminTarget (New-State) $s $source} 'ADMIN_BASELINE_MISMATCH'}
Check 'exact admin postcondition accepted' {Assert-MuAdminProvisioningResult (New-Snapshot) (New-Snapshot $true) $contract}
Check 'wrong ProductVersion rejected' {$s=New-Snapshot $true;$s.admin[0].ProductVersion='other';Reject {Assert-MuAdminProvisioningResult (New-Snapshot) $s $contract} 'ADMIN_HISTORY_MISMATCH'}
Check 'partial admin history rejected' {$s=New-Snapshot $true;$s.admin=@($s.admin[0]);Reject {Assert-MuAdminProvisioningResult (New-Snapshot) $s $contract} 'UNSAFE_CONFIG'}
Check 'game ProductVersion change rejected' {$s=New-Snapshot $true;$s.game[0].ProductVersion='changed';Reject {Assert-MuAdminProvisioningResult (New-Snapshot) $s $contract} 'ADMIN_BASELINE_MISMATCH'}
# Exercise actual orchestration with only policy authorization and external I/O mocked.
function Assert-MuSetupGrantPolicy($Policy) { }
$script:ownerLost=$false;$script:calls=@();$script:failSql=$false;$script:postBad=$false;$script:beforeBad=''
function Assert-MuSetupPgOwner($State) {$script:calls+='owner';if ($script:ownerLost) {throw 'OWNER_LOST'}}
function Invoke-MuSetupSql($State,[string]$Sql,[string]$Database='openmu') {
    Require ($Database -ceq 'openmu')
    if ($Sql.StartsWith('SELECT pg_catalog.json_build_object')) {
        $after=$Sql.Contains('FROM admin."__EFMigrationsHistory"')
        $script:calls+=if ($after) {'after'} else {'before'}
        $s=New-Snapshot $after
        if (!$after -and $script:beforeBad) {
            switch ($script:beforeBad) {
                'admin' {$s.adminAbsent=$false}
                'user' {$s.currentUser='mu_admin'}
                'database' {$s.database='postgres'}
                'game' {$s.game=$s.game[1..62]}
            }
        }
        if ($after -and $script:postBad) {$s.admin[0].ProductVersion='wrong'}
        return $s | ConvertTo-Json -Depth 10
    }
    Require ($Sql -ceq (Read-MuReviewedAdminSql $State $contract))
    $script:calls+='sql';if ($script:failSql) {throw 'MOCK_SQL_FAILED'}
}
Check 'exact reviewed SQL sent once after target checks before postconditions' {
    $script:calls=@();Invoke-MuSetupAdminProvisioning (New-State)
    Require (($script:calls -join ',') -ceq 'owner,before,owner,sql,owner,after')
}
Check 'unknown process ownership prevents any database I/O' {
    $script:calls=@();$script:ownerLost=$true
    try {Reject {Invoke-MuSetupAdminProvisioning (New-State)} 'OWNER_LOST';Require (($script:calls -join ',') -ceq 'owner')} finally {$script:ownerLost=$false}
}
Check 'SQL failure propagates without retries or postcondition queries' {
    $script:calls=@();$script:failSql=$true
    try {Reject {Invoke-MuSetupAdminProvisioning (New-State)} 'MOCK_SQL_FAILED';Require (($script:calls -join ',') -ceq 'owner,before,owner,sql')} finally {$script:failSql=$false}
}
Check 'postcondition failure propagates without repair or grants' {
    $script:calls=@();$script:postBad=$true
    try {Reject {Invoke-MuSetupAdminProvisioning (New-State)} 'ADMIN_HISTORY_MISMATCH';Require (@($script:calls | Where-Object {$_ -ceq 'sql'}).Count -eq 1)} finally {$script:postBad=$false}
}
foreach ($case in @(@('admin','ADMIN_SCHEMA_STATE_MISMATCH'),@('user','ADMIN_TARGET_MISMATCH'),@('database','ADMIN_TARGET_MISMATCH'),@('game','UNSAFE_CONFIG'))) {
    Check ('rejected precondition never submits SQL: '+$case[0]) {
        $script:calls=@();$script:beforeBad=$case[0]
        try {
            Reject {Invoke-MuSetupAdminProvisioning (New-State)} $case[1]
            Require (($script:calls -join ',') -ceq 'owner,before')
        } finally {$script:beforeBad=''}
    }
}
Check 'changed candidate bytes prevent even target queries' {
    $script:calls=@();$script:binaryBad=$true
    try {Reject {Invoke-MuSetupAdminProvisioning (New-State)} 'HASH_MISMATCH';Require ($script:calls.Count -eq 0)} finally {$script:binaryBad=$false}
}
Check 'postcondition history comparison ignores JSON property order' {
    $s=New-Snapshot $true
    $s.game=@($s.game | ForEach-Object {[ordered]@{ProductVersion=$_.ProductVersion;MigrationId=$_.MigrationId}})
    Assert-MuAdminProvisioningResult (New-Snapshot) $s $contract
}
Write-Output ('PASS TOTAL '+$script:passed)
