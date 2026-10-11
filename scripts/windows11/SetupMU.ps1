# One-time setup entry, deliberately blocked by unresolved no-DDL runtime grants.
#requires -Version 7.4
[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$PackageRoot,
    [Parameter(Mandatory)][string]$SetupRelative,
    [Parameter(Mandatory)][string]$BaselineArchive,
    [Parameter(Mandatory)][string]$CredentialBundle,
    [switch]$ConfirmNewDatabase,
    [switch]$ConfirmCredentialHandling,
    [switch]$ApplyReviewedFlags
)
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
. (Join-Path $PSScriptRoot 'Guards.ps1')
. (Join-Path $PSScriptRoot 'Database.ps1')
. (Join-Path $PSScriptRoot 'FirstSetup.ps1')
$result=Invoke-MuFirstSetup @{packageRoot=$PackageRoot;setupRelative=$SetupRelative;archive=$BaselineArchive;
    credentialBundle=$CredentialBundle;confirmNewDatabase=[bool]$ConfirmNewDatabase;
    confirmCredentialHandling=[bool]$ConfirmCredentialHandling;applyReviewedFlags=[bool]$ApplyReviewedFlags}
$result | ConvertTo-Json -Depth 6
if (!$result.databaseReady) { exit 2 }
