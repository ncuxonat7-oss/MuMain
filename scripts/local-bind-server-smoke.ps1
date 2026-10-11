# One manual Windows smoke. Native input and Read-GameState adapted from
# 52971f34461304a76587cfe3b6c694be239fc54d: .github/workflows/finish-gameplay.yml.
# No baseline repair, actor endpoint, helper rerun, or server force-kill.
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$evidence = Join-Path $PWD evidence
$privateLogs = Join-Path $PWD private-logs
$clientDirectory = Join-Path $PWD client
$serverDirectory = [IO.Path]::GetFullPath((Join-Path $PWD server-source/src/Startup/bin/Release))
$pgBin = if ($env:PGBIN) { $env:PGBIN } else { 'C:\Program Files\PostgreSQL\17\bin' }
$pgData = Join-Path $env:RUNNER_TEMP ("mu-bind-pg-" + $env:GITHUB_RUN_ID)
$server = $null; $client = $null; $pgStarted = $false; $serverIo = $null
$webPort = 18080; $connectPort = 44406; $pgPort = 5432
$startSeconds = 180; $stopMilliseconds = 45000
$expectedPorts = @(); $gamePorts = @(); $chatPorts = @(); $connectPorts = @()
$desktop = $null
$pgOwned = $false; $pgDeadline = $null
$pgStartAttempted = $false; $pgUtilityCleanupIncomplete = $false

function Save-Json([string]$name, $value) {
    $value | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath (Join-Path $evidence $name) -Encoding utf8
}

function Invoke-Pg([string]$sql) {
    $output = & "$pgBin/psql.exe" -X -w -h 127.0.0.1 -p $pgPort -U postgres -d openmu -t -A -v ON_ERROR_STOP=1 -c $sql 2> "$privateLogs/last-query.err"
    if ($LASTEXITCODE) { throw 'Read-only SQL failed; no fixture repair attempted' }
    return ($output -join '')
}

function Write-PgStage([string]$stage, [string]$state, $details = @{}) {
    $entry=@{stage=$stage; state=$state; utc=[DateTime]::UtcNow.ToString('o'); details=$details}
    $entry | ConvertTo-Json -Depth 5 -Compress | Add-Content -LiteralPath "$evidence/pg-stages.jsonl" -Encoding utf8
    Write-Host ("PG stage {0}: {1}" -f $stage,$state)
}

function Invoke-PgTool([string]$stage, [string]$tool, [string[]]$arguments, [int]$seconds) {
    if ($tool -notin @('pg_restore','initdb','pg_ctl','createdb','psql')) { throw 'Unexpected PG utility' }
    if ($null -ne $pgDeadline -and $stage -ne 'stop') {
        $seconds=[Math]::Min($seconds,[int][Math]::Floor(($pgDeadline-[DateTime]::UtcNow).TotalSeconds))
    }
    Write-PgStage $stage 'begin' @{timeoutSeconds=$seconds; tool=$tool}
    if ($seconds -le 0) { throw 'PG preparation exceeded five-minute budget' }
    $info=[Diagnostics.ProcessStartInfo]::new()
    $info.FileName=Join-Path $pgBin "$tool.exe"
    $info.UseShellExecute=$false
    $info.RedirectStandardInput=$true; $info.RedirectStandardOutput=$true; $info.RedirectStandardError=$true
    $info.Environment['PGCONNECT_TIMEOUT']='10'
    foreach ($argument in $arguments) { $info.ArgumentList.Add($argument) }
    $process=[Diagnostics.Process]::new(); $process.StartInfo=$info
    $utilityStarted=$false
    $stdout=$null; $stderr=$null; $clock=[Diagnostics.Stopwatch]::StartNew()
    try {
        if (!$process.Start()) { throw 'PG utility failed to start' }
        $utilityStarted=$true
        Write-PgStage $stage 'started' @{pid=$process.Id}
        $process.StandardInput.Close() # No interactive input for any PG preparation utility.
        $stdout=[IO.File]::Open("$privateLogs/pg-$stage.out",'Create','Write','ReadWrite')
        $stderr=[IO.File]::Open("$privateLogs/pg-$stage.err",'Create','Write','ReadWrite')
        $outTask=$process.StandardOutput.BaseStream.CopyToAsync($stdout)
        $errTask=$process.StandardError.BaseStream.CopyToAsync($stderr)
        if (!$process.WaitForExit($seconds * 1000)) {
            Write-PgStage $stage 'timeout' @{pid=$process.Id; elapsedSeconds=$clock.Elapsed.TotalSeconds}
            # Terminate only this owned utility, never its process tree, postgres or OpenMU.
            $process.Kill()
            if (!$process.WaitForExit(5000)) { throw 'Timed-out PG utility did not terminate' }
            throw 'PG utility deadline exceeded'
        }
        if (![Threading.Tasks.Task]::WhenAll([Threading.Tasks.Task[]]@($outTask,$errTask)).Wait(5000)) {
            Write-PgStage $stage 'pipe_timeout' @{pid=$process.Id; exitCode=$process.ExitCode}
            throw 'PG output pipe did not close after utility exit'
        }
        Write-PgStage $stage 'end' @{pid=$process.Id; exitCode=$process.ExitCode; elapsedSeconds=$clock.Elapsed.TotalSeconds}
        if ($process.ExitCode -ne 0) { throw 'PG utility failed; see bounded stage diagnostics' }
    } catch {
        Write-PgStage $stage 'failed' @{errorType=$_.Exception.GetType().Name; elapsedSeconds=$clock.Elapsed.TotalSeconds}
        throw
    } finally {
        try {
            if ($utilityStarted) {
                $utilityExited=$false
                try {
                    if (!$process.HasExited) {
                        $process.Kill() # Only this owned utility; never the process tree.
                        $utilityExited=$process.WaitForExit(5000)
                    } else { $utilityExited=$true }
                } catch { $utilityExited=$false }
                if (!$utilityExited) { $script:pgUtilityCleanupIncomplete=$true }
                Write-PgStage $stage 'utility-cleanup' @{pid=$process.Id; exitEstablished=$utilityExited}
            }
        } finally {
            if ($null -ne $stdout) { $stdout.Dispose() }
            if ($null -ne $stderr) { $stderr.Dispose() }
            $process.Dispose()
        }
    }
}

function Start-DisposablePostgres {
    $script:pgDeadline=[DateTime]::UtcNow.AddMinutes(5)
    Write-PgStage 'fresh-path' 'begin'
    if (Test-Path -LiteralPath $pgData) { throw 'Disposable cluster path already exists; refusing reuse' }
    Write-PgStage 'fresh-path' 'end'
    Write-PgStage 'port-check' 'begin'
    $query=Get-NetTCPConnection -State Listen -LocalPort $pgPort -AsJob -ErrorAction SilentlyContinue
    if (!(Wait-Job -Job $query -Timeout 10)) {
        Write-PgStage 'port-check' 'timeout'
        throw 'PG port inventory timed out; no PG initialization attempted'
    }
    $ports=@(Receive-Job -Job $query -ErrorAction SilentlyContinue)
    $queryFailed=$query.State -ne 'Completed'
    Remove-Job -Job $query
    if ($queryFailed) { throw 'PG port inventory failed; refusing startup' }
    if ($ports.Count) { throw 'PG port occupied; existing service untouched' }
    Write-PgStage 'port-check' 'end'
    Invoke-PgTool 'version' 'pg_restore' @('--version') 15
    $version=Get-Content -LiteralPath "$privateLogs/pg-version.out" -Raw
    if ($version -notmatch 'PostgreSQL\) 17\.') { throw 'Expected existing PostgreSQL 17 tools' }
    $script:pgOwned=$true
    Invoke-PgTool 'init' 'initdb' @('-D',$pgData,'-U','postgres','-A','trust','--no-locale') 90
    $script:pgStartAttempted=$true
    Invoke-PgTool 'start' 'pg_ctl' @('-D',$pgData,'-l',"$privateLogs/postgres.txt",'-o','-h 127.0.0.1 -p 5432','-t','60','-w','start') 75
    $script:pgStarted=$true
    Invoke-PgTool 'createdb' 'createdb' @('-w','-h','127.0.0.1','-p',"$pgPort",'-U','postgres','openmu') 30
    Invoke-PgTool 'roles' 'psql' @('-X','-w','-h','127.0.0.1','-p',"$pgPort",'-U','postgres','-d','openmu','-v','ON_ERROR_STOP=1','-c',
        'CREATE ROLE account LOGIN; CREATE ROLE config LOGIN; CREATE ROLE guild LOGIN; CREATE ROLE friend LOGIN;') 30
    Invoke-PgTool 'restore' 'pg_restore' @('--exit-on-error','-w','-h','127.0.0.1','-p',"$pgPort",'-U','postgres','-d','openmu','saved-gameplay/gameplay-test-db.dump') 120
    Write-PgStage 'identity-write' 'begin'
    Save-Json 'database-identity.json' @{artifact=11651520969; cluster=$pgData; version=$version.Trim(); temporary=$true}
    Write-PgStage 'identity-write' 'end'
}

function Read-GameState {
    $sql = @'
select json_build_object(
'experience', c."Experience", 'points', c."LevelUpPoints",
'level', (select "Value" from data."StatAttribute" where "CharacterId"=c."Id" and "DefinitionId"='560931ad-0901-4342-b7f4-fd2e2fcc0563'),
'strength', (select "Value" from data."StatAttribute" where "CharacterId"=c."Id" and "DefinitionId"='123282fe-fead-448e-ad2c-baece939b4b1'),
'shieldSlot', (select "ItemSlot" from data."Item" where "Id"='801da101-0000-760d-a605-a410efe9185d' and "ItemStorageId"=c."InventoryId"),
'items', (select json_agg(i order by i."Id") from data."Item" i where i."ItemStorageId"=c."InventoryId"))
from data."Character" c where "Name"='test0Dk';
'@
    $states = @(Invoke-Pg $sql | ConvertFrom-Json)
    if ($states.Count -ne 1 -or $null -eq $states[0]) { throw 'Expected exactly one test0Dk' }
    return $states[0]
}

function Assert-State($state, [int]$strength, [int]$points, $baseline) {
    if ($state.level -ne 2 -or $state.experience -ne 115 -or $state.points -ne $points -or
        $state.strength -ne $strength -or $state.shieldSlot -ne 1 -or @($state.items).Count -ne 44) {
        throw 'Baseline/state mismatch; no SQL repair and no additional allocation allowed'
    }
    if ($null -ne $baseline -and ((@($state.items.Id) -join ',') -cne (@($baseline.items.Id) -join ','))) {
        throw 'Inventory UUID set changed'
    }
}

function Read-EndpointContract {
    $system = @(Invoke-Pg 'select json_agg(json_build_object(''readConsoleInput'',"ReadConsoleInput")) from config."SystemConfiguration";' | ConvertFrom-Json)
    if ($system.Count -ne 1 -or $system[0].readConsoleInput -ne $true) { throw 'ReadConsoleInput is not confirmed true; no server start or SQL repair' }
    # Exact configured endpoint tables: unknown schema or empty category fails closed.
    $game = @(Invoke-Pg 'select json_agg(json_build_object(''port'',"NetworkPort",''published'',"AlternativePublishedPort")) from config."GameServerEndpoint";' | ConvertFrom-Json)
    $chat = @(Invoke-Pg 'select json_agg(json_build_object(''port'',"NetworkPort")) from config."ChatServerEndpoint";' | ConvertFrom-Json)
    $connect = @(Invoke-Pg 'select json_agg(json_build_object(''port'',"ClientListenerPort")) from config."ConnectServerDefinition";' | ConvertFrom-Json)
    foreach ($category in @($game, $chat, $connect)) {
        if (!$category.Count -or $null -eq $category[0]) { throw 'Configured listener category absent; no coverage claim' }
        foreach ($entry in $category) { if ($entry.port -lt 1 -or $entry.port -gt 65535) { throw 'Invalid configured port' } }
    }
    foreach ($entry in $game) {
        if ($entry.published -ne 0 -and $entry.published -ne $entry.port) { throw 'Alternative published game port needs separate routing; no rewrite' }
    }
    $script:gamePorts = @($game.port | Sort-Object -Unique)
    $script:chatPorts = @($chat.port | Sort-Object -Unique)
    $script:connectPorts = @($connect.port | Sort-Object -Unique)
    if ($connectPort -notin $connectPorts) { throw 'Known native connect port absent' }
    $script:expectedPorts = @(@($gamePorts) + @($chatPorts) + @($connectPorts) + @($webPort) | Sort-Object -Unique)
    foreach ($port in $expectedPorts) {
        if (Get-NetTCPConnection -State Listen -LocalPort $port -ErrorAction SilentlyContinue) { throw "Server port occupied: $port" }
    }
    Save-Json 'endpoint-contract.json' @{game=$game; chat=$chat; connect=$connect; web=$webPort; postgres=$pgPort; advertisedAddress='127.0.0.1'; readConsoleInput=$true; actor='disabled'}
}

function Start-OwnedServer([string]$label) {
    $childEnvironment = Get-CheckedChildEnvironment
    $info = [Diagnostics.ProcessStartInfo]::new()
    $info.FileName = (Get-Command dotnet).Source
    $info.WorkingDirectory = $serverDirectory
    $info.UseShellExecute = $false
    $info.RedirectStandardInput = $true; $info.RedirectStandardOutput = $true; $info.RedirectStandardError = $true
    foreach ($arg in @('MUnique.OpenMU.Startup.dll','-autostart','-adminpanel:disabled','-resolveIP:127.0.0.1')) { $info.ArgumentList.Add($arg) }
    # Clear inherited hosting, endpoint, DB, profiler, startup-hook and actor overrides.
    $info.Environment.Clear()
    foreach ($key in $childEnvironment.Keys) { $info.Environment[$key]=$childEnvironment[$key] }
    $script:server = [Diagnostics.Process]::new(); $server.StartInfo=$info
    if (!$server.Start()) { throw 'Server process start failed' }
    $outPath=Join-Path $privateLogs "$label-server.out"; $errPath=Join-Path $privateLogs "$label-server.err"
    $out=[IO.File]::Open($outPath, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write, [IO.FileShare]::ReadWrite)
    $err=[IO.File]::Open($errPath, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write, [IO.FileShare]::ReadWrite)
    $script:serverIo=@{out=$out; err=$err; outPath=$outPath; errPath=$errPath;
        outTask=$server.StandardOutput.BaseStream.CopyToAsync($out); errTask=$server.StandardError.BaseStream.CopyToAsync($err)}
    $server.StandardInput.AutoFlush=$true
    $server.StandardInput.WriteLine('pid')
    $deadline=[DateTime]::UtcNow.AddSeconds($startSeconds)
    do {
        if ($server.HasExited) { throw 'Server exited before readiness' }
        $out.Flush(); $err.Flush()
        $pidReply = (Get-Content -LiteralPath $outPath -Raw) -match ("PID: " + $server.Id + '\b')
        $ports=@(Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue | Where-Object OwningProcess -eq $server.Id)
        if ($pidReply -and @($expectedPorts | Where-Object { $_ -notin @($ports | ForEach-Object { $_.LocalPort }) }).Count -eq 0) { break }
        Start-Sleep -Seconds 1
    } while ([DateTime]::UtcNow -lt $deadline)
    if (!$pidReply) { throw 'Owned stdin pid round-trip failed' }
    Assert-Listeners $label
}

function Assert-Listeners([string]$label) {
    $all=@(Get-NetTCPConnection -State Listen -ErrorAction Stop)
    $owned=@($all | Where-Object OwningProcess -eq $server.Id)
    $pgOwner=[int](Get-Content -LiteralPath (Join-Path $pgData postmaster.pid) -TotalCount 1)
    $pg=@($all | Where-Object { $_.LocalPort -eq $pgPort })
    Save-Json "$label-listeners.json" @{serverPid=$server.Id; postgresPid=$pgOwner;
        server=@($owned | Select-Object LocalAddress,LocalPort,OwningProcess);
        postgres=@($pg | Select-Object LocalAddress,LocalPort,OwningProcess)}
    if (!$pg.Count -or @($pg | Where-Object { $_.OwningProcess -ne $pgOwner -or $_.LocalAddress -ne '127.0.0.1' }).Count) { throw 'PostgreSQL ownership/bind mismatch' }
    if (@($owned | Where-Object { $_.LocalAddress -ne '127.0.0.1' -or $_.LocalPort -notin $expectedPorts }).Count) { throw 'Unexpected server listener/address (including optional endpoint)' }
    if (@($expectedPorts | Where-Object { $_ -notin @($owned | ForEach-Object { $_.LocalPort }) }).Count) { throw 'Configured listener missing' }
    $actorLog=(Get-Content -LiteralPath $serverIo.outPath -Raw) + (Get-Content -LiteralPath $serverIo.errPath -Raw)
    if ($actorLog -match 'Actor control endpoint enabled') { throw 'Actor endpoint unexpectedly enabled' }
    $udp=@(Get-NetUDPEndpoint -ErrorAction Stop | Where-Object OwningProcess -eq $server.Id)
    Save-Json "$label-udp.json" @($udp | Select-Object LocalAddress,LocalPort,OwningProcess)
    if (@($udp | Where-Object { ![Net.IPAddress]::IsLoopback([Net.IPAddress]::Parse($_.LocalAddress)) }).Count) { throw 'Non-loopback server UDP endpoint' }
}

function Stop-OwnedServer([string]$label) {
    if ($null -eq $server -or $server.HasExited) { throw 'Server exited without owned graceful request' }
    if ((Invoke-Pg 'select 1;') -ne '1') { throw 'PostgreSQL unavailable before shutdown' }
    $server.StandardInput.WriteLine('exit'); $server.StandardInput.Flush()
    if (!$server.WaitForExit($stopMilliseconds)) { throw 'Graceful exit timeout; no server force-kill, PG retained' }
    $serverIo.outTask.GetAwaiter().GetResult(); $serverIo.errTask.GetAwaiter().GetResult()
    $serverIo.out.Dispose(); $serverIo.err.Dispose()
    $logs=(Get-Content -LiteralPath $serverIo.outPath -Raw) + (Get-Content -LiteralPath $serverIo.errPath -Raw)
    $errors=[regex]::Matches($logs, '(?im)\b(ERR|FTL|Error|Fatal)\b|Unhandled exception|Exception:').Count
    Save-Json "$label-shutdown.json" @{exitCode=$server.ExitCode; errorMarkers=$errors; stdinExit=$true; postgresAlive=((Invoke-Pg 'select 1;') -eq '1')}
    if ($server.ExitCode -ne 0 -or $errors) { throw 'Unclean server exit/log errors; no persistence PASS' }
    if (@(Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue | Where-Object OwningProcess -eq $server.Id).Count) { throw 'Server listeners remained after exit' }
}

# Existing native UI helpers; same coordinates and physical key timings.
Add-Type @'
using System;
using System.Runtime.InteropServices;
public static class PrototypeInput {
  [StructLayout(LayoutKind.Sequential)] public struct Rect { public int Left, Top, Right, Bottom; }
  [DllImport("user32.dll")] public static extern bool GetClientRect(IntPtr window, ref Rect rectangle);
  [StructLayout(LayoutKind.Sequential)] public struct Point { public int X; public int Y; }
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr window);
  [DllImport("user32.dll")] public static extern bool ClientToScreen(IntPtr window, ref Point point);
  [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
  [DllImport("user32.dll")] public static extern void keybd_event(byte key,byte scan,uint flags,UIntPtr extra);
  [DllImport("user32.dll")] public static extern void mouse_event(uint flags,uint x,uint y,uint data,UIntPtr extra);
}
'@

function Click-Client([int]$x,[int]$y) {
  $client.Refresh()
  if ($client.HasExited) { throw 'Client exited before input' }
  [PrototypeInput]::SetForegroundWindow($client.MainWindowHandle) | Out-Null
  $point = [PrototypeInput+Point]::new()
  $point.X = $x
  $point.Y = $y
  [PrototypeInput]::ClientToScreen($client.MainWindowHandle,[ref]$point) | Out-Null
  [PrototypeInput]::SetCursorPos($point.X,$point.Y) | Out-Null
  Start-Sleep -Milliseconds 250
  [PrototypeInput]::mouse_event(2,0,0,0,[UIntPtr]::Zero)
  Start-Sleep -Milliseconds 180
  [PrototypeInput]::mouse_event(4,0,0,0,[UIntPtr]::Zero)
  Start-Sleep -Seconds 2
}


function Wait-ClientReady {
  $deadline = [DateTime]::UtcNow.AddSeconds(60)
  while ([DateTime]::UtcNow -lt $deadline) {
    $client.Refresh()
    if ($client.HasExited) { throw 'Client exited before ready' }
    if ((Test-Path "$clientDirectory/MuError.log") -and (Select-String -Path "$clientDirectory/MuError.log" -Pattern 'Success Receive Server List' -Quiet)) { return }
    Start-Sleep -Seconds 2
  }
  throw 'Client did not receive server list before timeout'
}
function Press-PhysicalKey([byte]$key) {
  Focus-Client
  [PrototypeInput]::keybd_event($key,0,0,[UIntPtr]::Zero)
  Start-Sleep -Milliseconds 250
  [PrototypeInput]::keybd_event($key,0,2,[UIntPtr]::Zero)
  Start-Sleep -Milliseconds 400
}
function Type-AccountName([string]$name) {
  foreach ($letter in $name.ToCharArray()) { [Windows.Forms.SendKeys]::SendWait([string]$letter); Start-Sleep -Milliseconds 80 }
}
function Login-TestAccount([string]$account) {
  if ($account -ne 'test0') { throw 'Only named disposable seeded accounts permitted' }
  Wait-ClientReady
  Click-Client 334 301
  Click-Client 512 301
  Start-Sleep -Seconds 5
  Click-Client 530 465
  Type-AccountName $account
  Click-Client 530 490
  Type-AccountName $account
  Click-Client 525 563
  Start-Sleep -Seconds 10
  Click-Client 110 550
  Click-Client 891 694
  Start-Sleep -Seconds 10
}
function Focus-Client {
  $client.Refresh()
  if ($client.HasExited) { throw 'Client exited' }
  [PrototypeInput]::SetForegroundWindow($client.MainWindowHandle) | Out-Null
  Start-Sleep -Milliseconds 200
}

function Start-NativeClient([string]$label) {
    # Fresh logs prevent a prior session's server-list marker satisfying readiness.
    Get-ChildItem -LiteralPath $clientDirectory -File -Filter '*.log' | Remove-Item
    $env:SDL_GPU_DRIVER='direct3d12'
    $script:client=Start-Process "$clientDirectory/Main.exe" -WorkingDirectory $clientDirectory -ArgumentList 'connect','/u127.0.0.1','/p44406' -PassThru
    Login-TestAccount 'test0'
    $connections=@(Get-NetTCPConnection -State Established -ErrorAction Stop | Where-Object {
        $_.OwningProcess -eq $client.Id -and $_.RemotePort -in $gamePorts
    })
    Save-Json "$label-native-connections.json" @($connections | Select-Object LocalAddress,LocalPort,RemoteAddress,RemotePort,OwningProcess)
    if (!$connections.Count -or @($connections | Where-Object RemoteAddress -ne '127.0.0.1').Count) { throw 'Native advertised game endpoint did not connect to expected loopback' }
    $nativeLog=Get-Content -LiteralPath "$clientDirectory/MuError.log" -Raw
    if ($nativeLog -notmatch '\[ReceiveServerConnect\]' -or $nativeLog -notmatch '\[ReceiveList Count') { throw 'Native connect/character list not observed' }
    Save-Json "$label-native-markers.json" @{receivedServerConnect=$true; receivedCharacterList=$true; selectedAccount='test0'; requestedCharacter='test0Dk'; enteredWorld='PENDING_VISUAL_REVIEW'}
}

function Capture-Stage([string]$name) {
    Focus-Client
    $rect=[PrototypeInput+Rect]::new()
    if (![PrototypeInput]::GetClientRect($client.MainWindowHandle, [ref]$rect) -or $rect.Right -ne 1024 -or $rect.Bottom -ne 768) { throw 'Native fixture requires exact 1024x768 client area' }
    $point=[PrototypeInput+Point]::new()
    if (![PrototypeInput]::ClientToScreen($client.MainWindowHandle,[ref]$point)) { throw 'Client coordinates unavailable' }
    $bitmap=[Drawing.Bitmap]::new(1024,768); $graphics=[Drawing.Graphics]::FromImage($bitmap)
    try {
        $graphics.CopyFromScreen($point.X,$point.Y,0,0,$bitmap.Size)
        $bitmap.Save((Join-Path $evidence "$name.png"),[Drawing.Imaging.ImageFormat]::Png)
    } finally { $graphics.Dispose(); $bitmap.Dispose() }
}

function Close-NativeClient {
    if ($null -ne $client -and !$client.HasExited) {
        [void]$client.CloseMainWindow()
        if (!$client.WaitForExit(5000)) { $client.Kill(); $client.WaitForExit() }
    }
}

function Get-CheckedChildEnvironment {
    # Recheck before EACH Process.Start, including restart; do not mutate the runtime.
    $manifest=Get-Content -LiteralPath "$evidence/runtime-manifest.json" -Raw | ConvertFrom-Json -AsHashtable
    $configs=@(Get-ChildItem -LiteralPath $serverDirectory -Recurse -File | Where-Object {
        $_.Name -like 'appsettings*' -or $_.Extension -eq '.config' -or
        $_.Name -eq 'ConnectionSettings.xml' -or $_.Name -like '*.runtimeconfig*.json'
    })
    foreach ($file in $configs) {
        $relative=[IO.Path]::GetRelativePath($serverDirectory,$file.FullName).Replace('\','/')
        if (!$manifest.ContainsKey($relative) -or (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash -ne $manifest[$relative]) {
            throw 'Runtime configuration changed since verified build'
        }
        if ($file.Extension -eq '.config') { throw 'Unreviewed executable/web configuration; refusing launch' }
        if ($file.Name -like 'appsettings*') {
            if ($file.DirectoryName -ne $serverDirectory -or $file.Name -notin @('appsettings.json','appsettings.Production.json')) {
                throw 'Unreviewed appsettings provider/file; refusing launch'
            }
            $settings=Get-Content -LiteralPath $file.FullName -Raw | ConvertFrom-Json -AsHashtable
            foreach ($key in $settings.Keys) {
                # Kestrel, hosting startup, ConnectionStrings and unknown sections are rejected.
                if ($key -notin @('Logging','AllowedHosts','Urls')) { throw 'Unreviewed appsettings section; refusing launch' }
                if ($key -eq 'Urls' -and $settings[$key] -cne "http://127.0.0.1:$webPort") { throw 'Non-approved web URL configuration' }
                if ($key -eq 'Logging') {
                    foreach ($loggingKey in $settings[$key].Keys) {
                        if ($loggingKey -ne 'LogLevel') { throw 'Unreviewed logging provider configuration' }
                    }
                }
            }
        }
        if ($file.Name -like '*.runtimeconfig*.json') {
            if ($file.Name -ne 'MUnique.OpenMU.Startup.runtimeconfig.json' -or $file.DirectoryName -ne $serverDirectory) {
                throw 'Unreviewed runtime configuration file; refusing launch'
            }
            $runtime=Get-Content -LiteralPath $file.FullName -Raw | ConvertFrom-Json -AsHashtable
            if ($runtime.Count -ne 1 -or !$runtime.ContainsKey('runtimeOptions')) { throw 'Unknown runtime configuration shape' }
            foreach ($key in $runtime.runtimeOptions.Keys) {
                if ($key -notin @('tfm','framework','frameworks','configProperties','rollForward')) { throw 'Unreviewed runtime option' }
            }
            if ($runtime.runtimeOptions.ContainsKey('configProperties')) {
                foreach ($key in $runtime.runtimeOptions.configProperties.Keys) {
                    if ($key -notin @('System.GC.Server','System.Reflection.Metadata.MetadataUpdater.IsSupported',
                        'System.Runtime.Serialization.EnableUnsafeBinaryFormatterSerialization','System.Globalization.Invariant')) {
                        throw 'Unreviewed runtime property; refusing launch'
                    }
                }
            }
        }
    }
    [xml]$xml=Get-Content -LiteralPath "$serverDirectory/ConnectionSettings.xml" -Raw
    $entries=@($xml.SelectNodes('//*[local-name()="ConnectionString"]'))
    if (!$entries.Count) { throw 'Cannot verify runtime DB connection settings' }
    foreach ($entry in $entries) {
        $cs=[System.Data.Common.DbConnectionStringBuilder]::new(); $cs.ConnectionString=$entry.InnerText
        foreach ($key in $cs.Keys) {
            if ($key -notin @('Server','Port','Database','User Id','Username','Password','Pooling',
                'Minimum Pool Size','Maximum Pool Size','Timeout','Command Timeout','Include Error Detail')) {
                throw 'Unreviewed DB connection option; refusing launch'
            }
        }
        if (!$cs.ContainsKey('Server') -or !$cs.ContainsKey('Database')) { throw 'Unknown DB connection shape' }
        # Pinned default may use localhost; effective DB_HOST below is numeric loopback.
        if ($cs['Server'] -notin @('localhost','127.0.0.1','::1')) { throw 'Non-loopback configured DB host' }
        if ($cs['Database'] -notin @('openmu','postgres')) { throw 'Unexpected runtime database target' }
        if ($cs.ContainsKey('Port') -and [int]$cs['Port'] -ne $pgPort) { throw 'Unexpected runtime database port' }
    }
    $child=@{}
    foreach ($key in @('SystemRoot','WINDIR','TEMP','TMP')) {
        $value=[Environment]::GetEnvironmentVariable($key)
        if (!$value -or ![IO.Path]::IsPathFullyQualified($value) -or $value.StartsWith('\\') -or !(Test-Path -LiteralPath $value -PathType Container)) {
            throw 'Required local Windows environment directory unavailable'
        }
        $child[$key]=$value
    }
    $child['DOTNET_ROOT']=Split-Path (Get-Command dotnet).Source
    $child['OPENMU_LOCAL_ONLY_TCP']='1'
    $child['ASPNETCORE_URLS']="http://127.0.0.1:$webPort"
    $child['ASPNETCORE_ENVIRONMENT']='Production'; $child['DOTNET_ENVIRONMENT']='Production'
    $child['ASPNETCORE_PREVENTHOSTINGSTARTUP']='true'
    $child['DB_HOST']='127.0.0.1'; $child['DB_ADMIN_USER']='postgres'
    $child['DOTNET_CLI_TELEMETRY_OPTOUT']='1'; $child['DOTNET_NOLOGO']='1'
    Save-Json 'prelaunch-containment.json' @{verified=$true; environmentKeys=@($child.Keys | Sort-Object);
        databaseHost='127.0.0.1'; webUrl=$child['ASPNETCORE_URLS']; inheritedOverrides=$false;
        configFiles=@($configs.Name); unknownConfiguration='refuse before Process.Start'}
    return $child
}

try {
    Save-Json 'smoke-result.json' @{status='NOT_RUN'; scenario='test0Dk STR31 to32, points2 to1; graceful server restart and native relog'}
    Start-DisposablePostgres
    $null=Get-CheckedChildEnvironment
    $before=Read-GameState
    Assert-State $before 31 2 $null
    Save-Json 'before-state.json' $before
    Read-EndpointContract
    Add-Type -AssemblyName System.Windows.Forms
    Add-Type -AssemblyName System.Drawing
    Start-OwnedServer 'first'
    Start-NativeClient 'first'
    Press-PhysicalKey 67
    Capture-Stage '01-before-one-str-allocation'
    # Repeat guards immediately before the only state-changing UI click.
    Assert-State (Read-GameState) 31 2 $before
    Click-Client 989 202
    Capture-Stage '02-after-one-str-allocation'
    Assert-Listeners 'first-after-allocation'
    # Keep native client connected: server's graceful disconnect must save state.
    Stop-OwnedServer 'first'
    $saved=Read-GameState
    Save-Json 'after-graceful-exit-state.json' $saved
    Assert-State $saved 32 1 $before
    Close-NativeClient
    Start-OwnedServer 'second'
    Start-NativeClient 'second'
    Press-PhysicalKey 67
    Capture-Stage '03-native-relog-strength32-point1'
    $relogged=Read-GameState
    Save-Json 'after-native-relog-state.json' $relogged
    Assert-State $relogged 32 1 $before
    Stop-OwnedServer 'second'
    $final=Read-GameState
    Save-Json 'after-second-exit-state.json' $final
    Assert-State $final 32 1 $before
    Save-Json 'smoke-result.json' @{status='PENDING_VISUAL_REVIEW'; persistedState='PASS'; nativeRelog='PENDING_VISUAL_REVIEW'; allocationClicks=1; beforeSTR=31; afterSTR=32; beforePoints=2; afterPoints=1;
        nativeEndpointConnected=$true; gracefulRestarts=1; serverExits=2; postgresAliveDuringShutdown=$true;
        integrity='level2 EXP115 shield-slot1 and same 44 item UUIDs';
        limit='Persisted STR state verified. Native world entry/relog requires review of authentic captures; no aggregate PASS. Not full game, crash safety, or owner Windows package proof.'}
} catch {
    # Preserve only our fixed diagnostic or error type; never arbitrary SQL/connection text.
    Save-Json 'smoke-result.json' @{status='FAIL'; noAutomaticRetry=$true}
    Save-Json 'smoke-failure.json' @{status='FAIL'; errorType=$_.Exception.GetType().FullName; scriptLine=$_.InvocationInfo.ScriptLineNumber}
    throw 'Bounded server smoke failed; see stage evidence and failure line. No automatic retry.'
} finally {
    $cleanupOk=!$pgUtilityCleanupIncomplete
    if ($null -ne $server -and !$server.HasExited) {
        try { Stop-OwnedServer 'failure-cleanup' } catch { $cleanupOk=$false }
    }
    Close-NativeClient
    $pgStopAction='not_attempted'; $pgStopped=$false
    $pgPidFilePresent=Test-Path -LiteralPath (Join-Path $pgData postmaster.pid)
    if ($pgOwned -and $pgPidFilePresent -and ($null -eq $server -or $server.HasExited)) {
        # pg_ctl may have spawned PostgreSQL before returning or timing out.
        $pgStopAction='owned_cluster_fast_stop'
        try {
            Invoke-PgTool 'stop' 'pg_ctl' @('-D',$pgData,'-m','fast','-t','60','-w','stop') 75
            $pgStopped=!(Test-Path -LiteralPath (Join-Path $pgData postmaster.pid))
            if (!$pgStopped) { $cleanupOk=$false }
        } catch { $cleanupOk=$false }
    } elseif ($pgOwned -and $pgPidFilePresent) {
        $pgStopAction='retained_while_server_alive'; $cleanupOk=$false
    } else {
        $pgStopAction='no_owned_pid_file_stop_not_proven'
    }
    if ($pgStartAttempted -and !$pgStopped) {
        $cleanupOk=$false
        if (!$pgPidFilePresent) { $pgStopAction='UNKNOWN_start_attempted_without_shutdown_proof' }
    }
    if ($pgUtilityCleanupIncomplete) { $cleanupOk=$false }
    Save-Json 'cleanup.json' @{completed=$cleanupOk; serverForceKill=$false; clusterDeleted=$false;
        postgresStartAttempted=$pgStartAttempted; utilityCleanupIncomplete=$pgUtilityCleanupIncomplete;
        postgresStartedFlag=$pgStarted; clusterPreparationOwned=$pgOwned; postgresPidFileBeforeCleanup=$pgPidFilePresent;
        postgresStopAction=$pgStopAction; postgresStopped=$pgStopped}
    if (!$cleanupOk) {
        Save-Json 'smoke-result.json' @{status='FAIL_CLEANUP'; serverForceKill=$false}
        throw 'Cleanup incomplete; run must fail, no force-kill substituted'
    }
}
