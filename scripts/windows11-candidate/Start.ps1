# Review candidate. No laptop setup or policy changes are performed.
#requires -Version 7.4
param([string]$PackageRoot=$PSScriptRoot)
$ErrorActionPreference='Stop'
Import-Module (Join-Path $PSScriptRoot 'Launcher.psm1') -Force
$session=New-MuSession
if (!$IsWindows) { Write-Host 'Windows 11 required. No processes started.'; exit 1 }
try {
    do {
        Write-Host '1 - Запустить / Start   2 - Остановить / Stop   3 - Собрать отчёт / CollectReport   0 - Выход / Exit'
        $choice=Read-Host
        switch ($choice) {
            '1' { $null=Start-MuSession $session $PackageRoot; Write-Host $session.Code }
            '2' { $null=Stop-MuSession $session; Write-Host $session.Code }
            '3' { Write-Host (Write-MuReport $session $PackageRoot) }
            '0' {
                if (!(Stop-MuSession $session)) {
                    Write-Host 'Stop failed. Keep this window open; PostgreSQL retained. No forced shutdown.'
                    $choice=''
                }
            }
        }
        if ($session.Code -eq 'SETUP_REQUIRED') {
            Write-Host 'Нужна отдельно согласованная подготовка пакета. База не изменена.'
        }
    } while ($choice -ne '0')
} finally {
    # If console teardown interrupts this attempt, the durable marker is retained.
    # A later launcher refuses recovery/adoption; it cannot recover the stdin pipe.
    if ($null -ne $session.Lock) { $null=Stop-MuSession $session }
}
