# Actual PowerShell: integrity/admission only; no external utilities are allowed.
param([string]$Root,[string]$InventorySha)
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$code=Join-Path $Root 'scripts/windows11'
. (Join-Path $code 'Guards.ps1')
. (Join-Path $code 'FirstSetup.ps1')
. (Join-Path $code 'AdminProvisioning.ps1')
$script:utilityCalls=0
function Invoke-MuSetupUtility { $script:utilityCalls++;throw 'EXTERNAL_UTILITY_FORBIDDEN' }
function Invoke-MuSetupSql { $script:utilityCalls++;throw 'SQL_FORBIDDEN' }
function Must($b){if(!$b){throw 'ASSERTION_FAILED'}}
$results=@()
$null=Assert-MuPackageContract $Root
$results+='PASS coherent complete-package metadata and executing-script integrity'
try { $null=Get-MuApprovedSetup $Root;throw 'EXPECTED_REJECTION_MISSING' } catch {Must ($_.Exception.Message -ceq 'SETUP_REQUIRED')}
$results+='PASS launch admission rejects disabled contract'
$request=@{packageRoot=$Root;setupRelative='database/setup-unit-blocked';archive=(Join-Path $PSScriptRoot 'never-open-archive');credentialBundle=(Join-Path $PSScriptRoot 'never-open-credentials');confirmNewDatabase=$true;confirmCredentialHandling=$true;applyReviewedFlags=$true}
$result=Invoke-MuFirstSetup $request
Must ($result.stage -ceq 'application-approval' -and !$result.databaseReady -and $null -eq $result.setupDirectory)
Must (!(Test-Path (Join-Path $Root 'database')))
$results+='PASS real setup orchestration stops at application approval before credentials or DB'
$state=@{policy=(Get-MuFirstSetupPolicy);request=$request}
try {Invoke-MuSetupAdminProvisioning $state;throw 'EXPECTED_REJECTION_MISSING'} catch {Must ($_.Exception.Message -ceq 'SETUP_APPLICATION_APPROVAL_REQUIRED')}
$results+='PASS direct admin provisioning stops at application approval'
try {$null=Assert-MuPackageContract $Root -VerifyPayload -ExpectedInventorySha256 ('0'*64);throw 'EXPECTED_REJECTION_MISSING'} catch {Must ($_.Exception.Message -ceq 'HASH_MISMATCH')}
$results+='PASS wrong independent manifest pin rejected before payload hashing'
foreach($kind in @('missing','corrupt')) {
 $fixture=Join-Path $PSScriptRoot ('fixture-'+$kind+'-'+[Guid]::NewGuid().ToString('N'))
 $null=New-Item -ItemType Directory (Join-Path $fixture 'scripts/windows11')
 $null=New-Item -ItemType Directory (Join-Path $fixture 'server')
 foreach($n in @('package-admission.json','package-inventory.json','windows11-launch-manifest.draft.json','packaging-status.json')) {Copy-Item -LiteralPath (Join-Path $Root $n) -Destination $fixture}
 Copy-Item -LiteralPath (Join-Path $Root 'server/ConnectionSettings.xml') -Destination (Join-Path $fixture 'server/ConnectionSettings.xml')
 foreach($f in Get-ChildItem -LiteralPath $code -File) {
  if($f.Name -ceq 'admin-provisioning.sql') {
   if($kind -ceq 'corrupt'){[IO.File]::WriteAllText((Join-Path $fixture 'scripts/windows11/admin-provisioning.sql'),'inert-corruption-fixture')}
  }else{Copy-Item -LiteralPath $f.FullName -Destination (Join-Path $fixture 'scripts/windows11')}
 }
 . (Join-Path $fixture 'scripts/windows11/Guards.ps1')
 $blocked=$false
 try {$null=Assert-MuPackageContract $fixture} catch {$blocked=$true;if($kind -ceq 'missing'){Must ($_.CategoryInfo.Category -eq 'ObjectNotFound')}else{Must ($_.Exception.Message -ceq 'HASH_MISMATCH')}}
 Must $blocked
 $results+="PASS $kind admin SQL rejected by integrated package contract"
}
Must ($script:utilityCalls -eq 0)
$results+='PASS zero external utility or SQL invocations'
$results
