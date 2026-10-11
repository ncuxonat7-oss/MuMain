# Manually invoked metadata-only local report. No logs, environment, DB or uploads.
#requires -Version 7.4
[CmdletBinding()]
param()
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
Import-Module (Join-Path $PSScriptRoot 'Launcher.psm1') -Force
# A separate invocation cannot infer a live controller's status. The menu report
# includes its current status. Keep the default destination beside this script.
$session=New-MuSession
Write-Host (Write-MuReport $session $PSScriptRoot)
