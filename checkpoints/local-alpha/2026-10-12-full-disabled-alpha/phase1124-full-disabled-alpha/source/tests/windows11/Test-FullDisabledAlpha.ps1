# Actual packaged module paths; no payload/server/DB execution. Test-only tripwires.
#requires -Version 7.4
param([Parameter(Mandatory)][string]$PackageRoot,[Parameter(Mandatory)][string]$Cases)
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$script:passed=0
function Require([bool]$Value) { if (!$Value) { throw 'ASSERTION_FAILED' } }
function Check([string]$Name,[scriptblock]$Test) { & $Test; $script:passed++; "PASS $Name" }
$module=Import-Module (Join-Path $PackageRoot 'scripts/windows11/Launcher.psm1') -Force -PassThru
& $module {
    function script:Assert-MuPorts { throw 'TRIPWIRE_PORTS' }
    function script:Enter-MuLock { throw 'TRIPWIRE_LOCK' }
    function script:Start-MuProcess { throw 'TRIPWIRE_PROCESS' }
    function script:Start-MuPostgres { throw 'TRIPWIRE_POSTGRES' }
    function script:Assert-MuDatabase { throw 'TRIPWIRE_DB' }
}
Check 'actual preflight stops at unresolved grants' {
    $s=New-MuSession; Require (!(Test-MuPreflight $s $PackageRoot)); Require ($s.Code -ceq 'RUNTIME_GRANTS_UNRESOLVED'); Require ($null -eq $s.Setup -and $null -eq $s.Lock)
}
Check 'actual start stops before lock ports processes and DB' {
    $s=New-MuSession; Require (!(Start-MuSession $s $PackageRoot)); Require ($s.Code -ceq 'RUNTIME_GRANTS_UNRESOLVED'); Require ($null -eq $s.Pg -and $null -eq $s.Server -and $null -eq $s.Client -and $null -eq $s.Lock)
}
Check 'integrity requires independently supplied pin' {
    $s=New-MuSession; Require (!(Test-MuPreflight $s $PackageRoot -IntegrityOnly)); Require ($s.Code -ceq 'MANIFEST_REQUIRED')
}
Check 'observer was not compiled on module import' { Require ($null -eq ('MuConsoleObserver' -as [type])) }
. (Join-Path $PackageRoot 'scripts/windows11/Guards.ps1')
. (Join-Path $PackageRoot 'scripts/windows11/Database.ps1')
. (Join-Path $PackageRoot 'scripts/windows11/FirstSetup.ps1')
foreach ($name in @('Assert-MuSetupHostAndInputs','Initialize-MuSetupPrivateArea','Read-MuSetupCredentials','Expand-MuSetupDump','Initialize-MuSetupCluster','Start-MuSetupCluster','New-MuSetupRolesAndDatabase','Restore-MuSetupSnapshot','Set-MuSetupReviewedFlags','Prepare-MuSetupAcceptance','Test-MuSetupReadOnlyAcceptance','Seal-MuSetupPrivateOutput','Stop-MuSetupCluster','Invoke-MuSetupUtility','Invoke-MuSetupSql')) {
    Set-Item -LiteralPath ('Function:'+ $name) -Value { throw 'TRIPWIRE_SETUP_STAGE' }
}
$request=@{packageRoot=$PackageRoot;setupRelative='database/setup-test';archive=(Join-Path $PackageRoot 'not-provided.zip');credentialBundle=(Join-Path $PackageRoot 'not-provided.credentials');confirmNewDatabase=$true;confirmCredentialHandling=$true;applyReviewedFlags=$true}
Check 'actual first setup blocked before credentials files or DB' {
    $result=Invoke-MuFirstSetup $request
    Require ($result.status -ceq 'BLOCKED_RUNTIME_GRANTS' -and $result.stage -ceq 'runtime-grants')
    Require (!$result.databaseReady -and !$result.launchEnabled -and $null -eq $result.approvedLaunchManifestSha256 -and $null -eq $result.setupDirectory)
    Require (!(Test-Path -LiteralPath (Join-Path $PackageRoot 'database')))
}
foreach ($case in Get-Content -LiteralPath $Cases -Raw | ConvertFrom-Json -AsHashtable) {
    Check ('negative integrated preflight '+$case.name) {
        $m=Import-Module (Join-Path $case.root 'scripts/windows11/Launcher.psm1') -Force -PassThru
        $s=& $m { New-MuSession }
        $ok=& $m { param($s,$r,$hash) Test-MuPreflight $s $r -IntegrityOnly -ExpectedInventorySha256 $hash } $s $case.root $case.expectedInventorySha256
        Require (!$ok); Require ($s.Code -ceq $case.code)
    }
}
Check 'wrong manifest blocks actual start before grant gate' {
    $case=@(Get-Content -LiteralPath $Cases -Raw | ConvertFrom-Json -AsHashtable | Where-Object name -eq 'wrong-manifest')[0]
    $m=Import-Module (Join-Path $case.root 'scripts/windows11/Launcher.psm1') -Force -PassThru
    $s=& $m { New-MuSession }
    $ok=& $m { param($s,$r) Start-MuSession $s $r } $s $case.root
    Require (!$ok -and $s.Code -ceq 'HASH_MISMATCH' -and $null -eq $s.Lock)
}
"PASSED $script:passed"
