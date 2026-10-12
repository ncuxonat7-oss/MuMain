# Reconciled Windows launcher lifecycle; separate approved setup is required.
# PowerShell 7.4+. No setup, downloads, database restore or automatic repair.
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$script:AllowedCodes = @('IDLE','PREFLIGHT','RUNNING','STOPPED','SETUP_REQUIRED','HASH_MISMATCH',
    'UNSAFE_CONFIG','PORT_BUSY','ALREADY_RUNNING','START_FAILED','STOP_FAILED','OWNER_LOST','WINDOWS_REQUIRED','MANIFEST_REQUIRED','PROBE_FAILED','PREFLIGHT_OK','STOPPED_WITH_WARNINGS','PACKAGE_INTEGRITY_OK','RUNTIME_GRANTS_UNRESOLVED','WINDOWS_ACCEPTANCE_REQUIRED')

function New-MuSession {
    return @{ Code='IDLE'; Pg=$null; Server=$null; Client=$null; PgStop=$null;
        Lock=$null; Setup=$null; ExitRequested=$false; ServerStopped=$false; ServerErrorsObserved=$false }
}

function Set-MuCode($Session, [string]$Code) {
    if ($Code -notin $script:AllowedCodes) { $Code='START_FAILED' }
    $Session.Code=$Code
}

function Assert-MuPorts([int[]]$Ports) {
    $listeners=@(Get-NetTCPConnection -State Listen -ErrorAction Stop)
    if (@($listeners | Where-Object LocalPort -in $Ports).Count) { throw 'PORT_BUSY' }
}

function Enter-MuLock([string]$Root) {
    # Global session name also prevents a second package copy owning the same stack.
    $mutex=[Threading.Mutex]::new($false, 'Global\MuMain.LocalLauncher')
    $held=$false
    try { $held=$mutex.WaitOne(0) } catch [Threading.AbandonedMutexException] { $held=$true }
    if (!$held) { $mutex.Dispose(); throw 'ALREADY_RUNNING' }
    $marker=Join-Path $Root '.mu-session-active'
    if (Test-Path -LiteralPath $marker) {
        $mutex.ReleaseMutex(); $mutex.Dispose(); throw 'OWNER_LOST'
    }
    try {
        $stream=[IO.File]::Open($marker,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::Read)
        $stream.Dispose()
    }
    catch { $mutex.ReleaseMutex(); $mutex.Dispose(); throw }
    return @{ Mutex=$mutex; Marker=$marker }
}

function Exit-MuLock($Session) {
    if ($null -eq $Session.Lock) { return }
    Remove-Item -LiteralPath $Session.Lock.Marker -Force
    $Session.Lock.Mutex.ReleaseMutex(); $Session.Lock.Mutex.Dispose(); $Session.Lock=$null
}

function Save-MuOwners($Session) {
    $owners=@{}
    foreach ($name in @('Pg','Server','Client','PgStop')) {
        $owned=$Session[$name]
        if ($null -ne $owned) {
            $owners[$name]=@{ pid=$owned.Pid; startUtcTicks=$owned.Ticks; path=$owned.Path }
        }
    }
    # Private recovery evidence only. Never used to adopt processes or in reports.
    Assert-MuLocalPath $Session.Lock.Marker
    [IO.File]::WriteAllText($Session.Lock.Marker, ($owners | ConvertTo-Json -Depth 4))
}

function Get-MuEnvironment($Setup, [switch]$Server) {
    $result=@{}
    foreach ($key in @('SystemRoot','WINDIR','TEMP','TMP')) {
        $value=[Environment]::GetEnvironmentVariable($key)
        if (!$value -or ![IO.Path]::IsPathFullyQualified($value) -or $value.StartsWith('\\')) { throw 'UNSAFE_CONFIG' }
        Assert-MuLocalPath $value
        $result[$key]=$value
    }
    if ($Server) {
        $result.DOTNET_ROOT=Split-Path (Resolve-MuFile $Setup.root $Setup.dotnet)
        $result.OPENMU_LOCAL_ONLY_TCP='1'; $result.RESOLVE_IP='127.0.0.1'
        $result.ASPNETCORE_URLS='http://127.0.0.1:18080'
        $result.ASPNETCORE_ENVIRONMENT='Production'; $result.DOTNET_ENVIRONMENT='Production'
        $result.ASPNETCORE_PREVENTHOSTINGSTARTUP='true'
        $result.DOTNET_CLI_TELEMETRY_OPTOUT='1'; $result.DOTNET_NOLOGO='1'
    }
    return $result
}

function Start-MuProcess([string]$File, [string]$Directory, [string[]]$Arguments, $Environment, [switch]$Observe) {
    $info=[Diagnostics.ProcessStartInfo]::new()
    $info.FileName=$File; $info.WorkingDirectory=$Directory; $info.UseShellExecute=$false
    $info.RedirectStandardInput=$true; $info.RedirectStandardOutput=$true; $info.RedirectStandardError=$true
    $info.Environment.Clear()
    foreach ($key in $Environment.Keys) { $info.Environment[$key]=$Environment[$key] }
    foreach ($argument in $Arguments) { $info.ArgumentList.Add($argument) }
    $process=[Diagnostics.Process]::new(); $process.StartInfo=$info
    try { if (!$process.Start()) { throw 'START_FAILED' } }
    catch { $process.Dispose(); throw }
    $owned=@{ Process=$process; Pid=0; Ticks=0; Path=$File; Output=$null; ErrorOutput=$null; Observer=$null }
    # Drain both pipes without retaining potentially secret or unbounded raw logs.
    try {
        if ($Observe) {
            $owned.Observer=[MuConsoleObserver]::new($process)
            $owned.Output=$owned.Observer.OutputTask; $owned.ErrorOutput=$owned.Observer.ErrorTask
        } else {
            $owned.Output=$process.StandardOutput.BaseStream.CopyToAsync([IO.Stream]::Null)
            $owned.ErrorOutput=$process.StandardError.BaseStream.CopyToAsync([IO.Stream]::Null)
        }
        $owned.Pid=$process.Id; $owned.Ticks=$process.StartTime.ToUniversalTime().Ticks
        $owned.Path=$process.MainModule.FileName
    } catch {
        # Preserve the process handle even if it exits during identity capture.
        # Invalid identity blocks further starts/cleanup and retains the marker.
        $owned.Ticks=0
    }
    return $owned
}

function Assert-MuOwner($Owned) {
    if ($null -eq $Owned -or $Owned.Ticks -le 0 -or $Owned.Pid -le 0 -or $Owned.Process.HasExited) { throw 'OWNER_LOST' }
    $current=Get-Process -Id $Owned.Pid -ErrorAction Stop
    try {
        if ($current.StartTime.ToUniversalTime().Ticks -ne $Owned.Ticks -or
            $current.MainModule.FileName -ine $Owned.Path) { throw 'OWNER_LOST' }
    } finally { $current.Dispose() }
}

function Assert-MuListeners($Owned, [int[]]$Ports) {
    Assert-MuOwner $Owned
    $tcp=@(Get-NetTCPConnection -State Listen -ErrorAction Stop | Where-Object OwningProcess -eq $Owned.Pid)
    if (@($tcp | Where-Object { $_.LocalAddress -ne '127.0.0.1' -or $_.LocalPort -notin $Ports }).Count) { throw 'UNSAFE_CONFIG' }
    $udp=@(Get-NetUDPEndpoint -ErrorAction Stop | Where-Object OwningProcess -eq $Owned.Pid)
    if ($udp.Count) { throw 'UNSAFE_CONFIG' } # No ordinary-session UDP endpoints reviewed.
    $actualPorts=@($tcp | ForEach-Object LocalPort)
    return @($Ports | Where-Object { $_ -notin $actualPorts }).Count -eq 0
}

function Wait-MuListeners($Owned, [int[]]$Ports) {
    $deadline=[DateTime]::UtcNow.AddSeconds(180)
    do {
        if (Assert-MuListeners $Owned $Ports) { return }
        Start-Sleep -Milliseconds 500
    } while ([DateTime]::UtcNow -lt $deadline)
    throw 'START_FAILED'
}

function Wait-MuServer($Session) {
    $owned=$Session.Server
    Assert-MuOwner $owned
    $owned.Process.StandardInput.WriteLine('pid'); $owned.Process.StandardInput.Flush()
    $deadline=[DateTime]::UtcNow.AddSeconds(180)
    do {
        Assert-MuOwner $Session.Pg
        if ($owned.Observer.ErrorSeen) { throw 'START_FAILED' }
        $ready=Assert-MuListeners $owned $Session.Setup.serverPorts
        if ($ready -and $owned.Observer.PidSeen) { return }
        Start-Sleep -Milliseconds 500
    } while ([DateTime]::UtcNow -lt $deadline)
    throw 'START_FAILED'
}

function Test-MuPreflight($Session, [string]$Root, [switch]$IntegrityOnly, [string]$ExpectedInventorySha256) {
    try {
        if ($null -ne $Session.Lock) { throw 'ALREADY_RUNNING' }
        if ($IntegrityOnly) {
            if ($ExpectedInventorySha256 -cnotmatch '^[a-f0-9]{64}$') { throw 'MANIFEST_REQUIRED' }
            $null=Assert-MuPackageContract $Root -VerifyPayload -ExpectedInventorySha256 $ExpectedInventorySha256
            Set-MuCode $Session 'PACKAGE_INTEGRITY_OK';return $true
        }
        $setup=Get-MuApprovedSetup $Root
        Assert-MuPorts (@(5432) + $setup.serverPorts)
        if (Test-Path -LiteralPath (Join-Path $Root '.mu-session-active')) { throw 'OWNER_LOST' }
        $Session.Setup=$setup; Set-MuCode $Session 'PREFLIGHT_OK'
        return $true
    } catch { Set-MuCode $Session $_.Exception.Message; return $false }
}

function Start-MuPostgres($Setup) {
    # Direct child ownership avoids adopting a pg_ctl-spawned process by PID file alone.
    $data=Resolve-MuFile $Setup.root $Setup.pgData
    if (Test-Path -LiteralPath (Join-Path $data 'postmaster.pid')) { throw 'OWNER_LOST' }
    return Start-MuProcess (Resolve-MuFile $Setup.root $Setup.postgres) $data @('-D',$data,'-h','127.0.0.1','-p','5432') (Get-MuEnvironment $Setup)
}

function Start-MuServer($Setup) {
    if (!('MuConsoleObserver' -as [type])) { Add-Type -Path (Join-Path $PSScriptRoot 'ConsoleObserver.cs') }
    Assert-MuHashes $Setup
    return Start-MuProcess (Resolve-MuFile $Setup.root $Setup.dotnet) (Resolve-MuFile $Setup.root $Setup.server) @(
        'MUnique.OpenMU.Startup.dll','-autostart','-adminpanel:disabled','-resolveIP:127.0.0.1') (Get-MuEnvironment $Setup -Server) -Observe
}

function Start-MuClient($Setup) {
    Assert-MuHashes $Setup
    $file=Resolve-MuFile $Setup.root $Setup.client
    return Start-MuProcess $file (Split-Path $file) @('connect','/u127.0.0.1','/p44406') (Get-MuEnvironment $Setup)
}

function Start-MuSession($Session, [string]$Root) {
    if ($null -ne $Session.Lock) { Set-MuCode $Session 'ALREADY_RUNNING'; return $false }
    try {
        Set-MuCode $Session 'PREFLIGHT'
        $Session.Setup=Get-MuApprovedSetup $Root
        Assert-MuHashes $Session.Setup
        Assert-MuPorts (@(5432) + $Session.Setup.serverPorts)
        $Session.Lock=Enter-MuLock $Root
        # Recheck after lock; never share/adopt an occupied listener.
        Assert-MuPorts (@(5432) + $Session.Setup.serverPorts)
        $Session.Pg=Start-MuPostgres $Session.Setup
        Save-MuOwners $Session
        Wait-MuListeners $Session.Pg @(5432)
        Assert-MuDatabase $Session.Setup
        $Session.Server=Start-MuServer $Session.Setup
        Save-MuOwners $Session
        Wait-MuServer $Session
        if (!(Assert-MuListeners $Session.Pg @(5432))) { throw 'START_FAILED' }
        $Session.Client=Start-MuClient $Session.Setup
        Save-MuOwners $Session
        Assert-MuOwner $Session.Client
        Set-MuCode $Session 'RUNNING'
        return $true
    } catch {
        $failure=$_.Exception.Message
        # No second launch is possible while failed cleanup retains the lock.
        if ($null -ne $Session.Lock) { $null=Stop-MuSession $Session }
        if ($Session.Code -ne 'STOP_FAILED') { Set-MuCode $Session $failure }
        return $false
    }
}

function Stop-MuClient($Owned) {
    if ($null -eq $Owned -or $Owned.Process.HasExited) { return }
    Assert-MuOwner $Owned
    if (!$Owned.Process.CloseMainWindow() -or !$Owned.Process.WaitForExit(15000)) { throw 'STOP_FAILED' }
}

function Stop-MuServer($Session) {
    if ($null -eq $Session.Server -or $Session.ServerStopped) { return }
    $owned=$Session.Server
    $Session.ServerErrorsObserved=$Session.ServerErrorsObserved -or ($null -ne $owned.Observer -and $owned.Observer.ErrorSeen)
    if (!$Session.ExitRequested) {
        Assert-MuOwner $Session.Pg
        if ((Invoke-MuQuery $Session.Setup 'SELECT to_json(1)') -ne 1) { throw 'STOP_FAILED' }
        Assert-MuOwner $owned
        $owned.Process.StandardInput.WriteLine('exit'); $owned.Process.StandardInput.Flush()
        $Session.ExitRequested=$true
    }
    if (!$owned.Process.WaitForExit(45000)) { throw 'STOP_FAILED' }
    if (!$owned.Output.Wait(5000) -or !$owned.ErrorOutput.Wait(5000)) { throw 'STOP_FAILED' }
    $Session.ServerErrorsObserved=$Session.ServerErrorsObserved -or $owned.Observer.ErrorSeen
    if ($owned.Process.ExitCode -ne 0) { throw 'STOP_FAILED' }
    Assert-MuOwner $Session.Pg
    $Session.ServerStopped=$true
}

function Stop-MuPostgres($Session) {
    if ($null -eq $Session.Pg) { return }
    $setup=$Session.Setup
    if ($null -eq $Session.PgStop) {
        Assert-MuOwner $Session.Pg
        Assert-MuAreaHashes $setup $setup.pgDirectory
        $pidFile=Join-Path (Resolve-MuFile $setup.root $setup.pgData) 'postmaster.pid'
        if ([int](Get-Content -LiteralPath $pidFile -TotalCount 1) -ne $Session.Pg.Pid) { throw 'OWNER_LOST' }
        $Session.PgStop=Start-MuProcess (Resolve-MuFile $setup.root $setup.pgCtl) $setup.root @(
            '-D',(Resolve-MuFile $setup.root $setup.pgData),'-m','fast','-t','60','-w','stop') (Get-MuEnvironment $setup)
        Save-MuOwners $Session
    }
    # A timed-out utility remains owned. Retrying Stop must not spawn a duplicate.
    if (!$Session.PgStop.Process.WaitForExit(75000) -or $Session.PgStop.Process.ExitCode -ne 0 -or
        !$Session.Pg.Process.WaitForExit(5000) -or $Session.Pg.Process.ExitCode -ne 0) { throw 'STOP_FAILED' }
}

function Close-MuHandles($Session) {
    foreach ($name in @('Client','Server','Pg','PgStop')) {
        if ($null -ne $Session[$name]) {
            $Session[$name].Process.Dispose(); $Session[$name]=$null
        }
    }
    $Session.ExitRequested=$false
    $Session.ServerStopped=$false
}

function Stop-MuSession($Session) {
    if ($null -eq $Session.Lock) {
        Set-MuCode $Session $(if ($Session.ServerErrorsObserved) {'STOPPED_WITH_WARNINGS'} else {'IDLE'})
        return $true
    }
    try {
        Stop-MuClient $Session.Client
        Stop-MuServer $Session
        Stop-MuPostgres $Session
        Close-MuHandles $Session
        Exit-MuLock $Session
        Set-MuCode $Session $(if ($Session.ServerErrorsObserved) {'STOPPED_WITH_WARNINGS'} else {'STOPPED'})
        return $true
    } catch {
        Set-MuCode $Session 'STOP_FAILED'
        return $false
    }
}

function Write-MuReport($Session, [string]$Directory) {
    # Construct an allowlist from constants, never serialize session/setup/errors.
    $code=if ($Session.Code -in $script:AllowedCodes) { $Session.Code } else { 'START_FAILED' }
    $report=[ordered]@{ schema=1; utc=[DateTime]::UtcNow.ToString('o'); status=$code;
        launcher='bounded-windows11-v2'; runtimeArtifact='LOCAL_PUBLISHED_SERVER'; build='PUBLISH_ONLY_NO_BUILD';
        source='7f1f061f9201f460cd13a3dc8cd9a455870bdc36'; sdk='10.0.401';
        openmu='d067b3c11c23c3145de6e2c76201ab9a93b267c8'; setup=$(if ($null -ne $Session.Setup) {'VALIDATED'} else {'NOT_VALIDATED'});
        serverErrorMarkersObserved=($Session.ServerErrorsObserved -eq $true -or
            ($null -ne $Session.Server -and $null -ne $Session.Server.Observer -and $Session.Server.Observer.ErrorSeen));
        persistence='UNKNOWN';
        windowsLifecycle='NOT_RUN'; uploads=$false; rawLogsIncluded=$false }
    Assert-MuLocalPath $Directory
    $path=Join-Path $Directory ('mu-report-' + [Guid]::NewGuid().ToString('N') + '.json')
    [IO.File]::WriteAllText($path, ($report | ConvertTo-Json))
    return $path
}

. (Join-Path $PSScriptRoot 'Guards.ps1')
. (Join-Path $PSScriptRoot 'Database.ps1')
# Observer compilation is deferred to the process path, unreachable while gates are closed.
Export-ModuleMember -Function New-MuSession,Test-MuPreflight,Start-MuSession,Stop-MuSession,Write-MuReport
