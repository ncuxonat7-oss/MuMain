param([string]$Root,[string]$Hash)
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
. (Join-Path $Root 'scripts/windows11/Guards.ps1')
$null=Assert-MuPackageContract $Root -ExpectedInventorySha256 $Hash
'FINAL_METADATA_OK'
