#requires -Version 7.4
param([string]$OutputDirectory=$PSScriptRoot)
$ErrorActionPreference='Stop'
Import-Module (Join-Path $PSScriptRoot 'Launcher.psm1') -Force
# Separate invocation cannot infer a live session's state. No process/log probing.
$session=New-MuSession
Write-Host (Write-MuReport $session $OutputDirectory)
