# Daily launcher only; never installs, initializes or restores a database.
#requires -Version 7.4
[CmdletBinding()]
param(
    [ValidateSet('Menu','Preflight','Start','Stop')][string]$Action='Menu',
    [string]$PackageRoot=(Split-Path (Split-Path $PSScriptRoot))
)
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
Import-Module (Join-Path $PSScriptRoot 'Launcher.psm1') -Force
$session=New-MuSession
if (!$IsWindows -or [Environment]::OSVersion.Version.Build -lt 22000 -or
    [Runtime.InteropServices.RuntimeInformation]::OSArchitecture -ne 'X64') { Write-Host 'WINDOWS_REQUIRED: Windows 11 required. No processes started.'; exit 2 }
if ($Action -eq 'Stop') {
    Write-Host 'NO_OWNED_SESSION: нажмите Остановить в уже открытом окне запуска. Чужие процессы не затронуты.'
    exit 2
}
if ($Action -eq 'Preflight') {
    $ok=Test-MuPreflight $session $PackageRoot
    Write-Host $session.Code
    if (!$ok) { exit 2 }; exit 0
}
function Show-LauncherStatus {
    $messages=@{
        RUNNING='Игра запущена. Оставьте это окно открытым; для завершения выберите Остановить.'
        STOPPED='Сеанс штатно остановлен. База не удалена. Сохранение прогресса отдельно не проверялось.'
        IDLE='В этом окне нет запущенного сеанса.'
        SETUP_REQUIRED='Нужна отдельно согласованная подготовка пакета. База не изменена.'
        MANIFEST_REQUIRED='Нет проверенного описания пакета. Запуск отменён.'
        HASH_MISMATCH='Файлы пакета отличаются от проверенных. Запуск отменён; соберите отчёт.'
        UNSAFE_CONFIG='Настройки не прошли проверку. Соберите отчёт; ничего не исправляйте вручную.'
        PORT_BUSY='Нужный порт занят. Другие программы не остановлены.'
        ALREADY_RUNNING='Сеанс уже открыт. Используйте его окно для остановки.'
        OWNER_LOST='Состояние прежнего сеанса требует проверки. Автоматическое восстановление отключено.'
        STOP_FAILED='Остановка не завершена. Оставьте окно открытым и соберите отчёт.'
    }
    $message=if ($messages.ContainsKey($session.Code)) {$messages[$session.Code]} else {'Операция не завершена. Соберите отчёт.'}
    Write-Host ($message + ' [' + $session.Code + ']')
}

try {
    if ($Action -eq 'Start') { $null=Start-MuSession $session $PackageRoot; Show-LauncherStatus }
    do {
        Write-Host '1 - Запустить   2 - Остановить   3 - Собрать отчёт   0 - Остановить и выйти'
        $choice=Read-Host
        switch ($choice) {
            '1' { $null=Start-MuSession $session $PackageRoot; Show-LauncherStatus }
            '2' { $null=Stop-MuSession $session; Show-LauncherStatus }
            '3' { Write-Host (Write-MuReport $session $PackageRoot) }
            '0' {
                if (!(Stop-MuSession $session)) {
                    Write-Host 'Остановка не завершена. Оставьте окно открытым. PostgreSQL сохранён; принудительной остановки нет.'
                    $choice=''
                }
            }
        }
    } while ($choice -ne '0')
} finally {
    if ($null -ne $session.Lock) { $null=Stop-MuSession $session }
}
