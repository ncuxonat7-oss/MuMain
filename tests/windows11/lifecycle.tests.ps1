# Run with PowerShell 7.4+, on Linux or Windows. No game, DB, network or Pester.
$ErrorActionPreference='Stop'
$modulePath=Join-Path $PSScriptRoot '../../scripts/windows11/Launcher.psm1'
$script:passed=0
function Check([string]$Name, [scriptblock]$Body) {
    & $Body
    $script:passed++
    Write-Host "PASS $Name"
}
function Assert($Condition) { if (!$Condition) { throw 'Assertion failed' } }
function Fresh {
    Remove-Module Launcher -ErrorAction SilentlyContinue
    return Import-Module $modulePath -PassThru -Force
}
function MockLifecycle($Module, [string]$Failure='') {
    & $Module {
        param($Failure)
        $script:events=[Collections.Generic.List[string]]::new(); $script:failure=$Failure
        function script:Event([string]$Name) {
            $script:events.Add($Name)
            if ($script:failure -eq $Name) { throw 'START_FAILED' }
        }
        function script:Get-MuApprovedSetup { Event 'setup'; return @{serverPorts=@(44406,55902,18080)} }
        function script:Assert-MuHashes { Event 'hashes' }
        function script:Assert-MuPorts { Event 'ports' }
        function script:Enter-MuLock { Event 'lock'; return @{} }
        function script:Save-MuOwners { }
        function script:Start-MuPostgres { Event 'pg-start'; return @{name='pg'} }
        function script:Wait-MuListeners($Owned) { Event "$($Owned.name)-ready" }
        function script:Wait-MuServer { Event 'server-ready' }
        function script:Assert-MuDatabase { Event 'db-check' }
        function script:Start-MuServer { Event 'server-start'; return @{name='server'} }
        function script:Assert-MuListeners { Event 'pg-recheck'; return $true }
        function script:Start-MuClient { Event 'client-start'; return @{name='client'} }
        function script:Stop-MuClient { Event 'client-stop' }
        function script:Stop-MuServer { Event 'server-stop' }
        function script:Stop-MuPostgres { Event 'pg-stop' }
        function script:Close-MuHandles($Session) {
            Event 'dispose'; $Session.Pg=$null; $Session.Server=$null; $Session.Client=$null
        }
        function script:Exit-MuLock($Session) { Event 'unlock'; $Session.Lock=$null }
    } $Failure
}
function Events($Module) { return & $Module { $script:events.ToArray() } }

Check 'all candidate scripts parse' {
    foreach ($file in Get-ChildItem (Join-Path $PSScriptRoot '../../scripts/windows11') -Include *.ps1,*.psm1 -Recurse) {
        $tokens=$null; $errors=$null
        $null=[Management.Automation.Language.Parser]::ParseFile($file.FullName,[ref]$tokens,[ref]$errors)
        Assert ($errors.Count -eq 0)
    }
}
Check 'missing/unapproved setup refuses before process or filesystem changes' {
    $m=Fresh; $s=New-MuSession
    Assert (!(Start-MuSession $s ([IO.Path]::GetTempPath())))
    Assert ($s.Code -eq 'SETUP_REQUIRED' -and $null -eq $s.Lock -and $null -eq $s.Pg)
}
Check 'start readiness order, duplicate refusal, explicit stop ordering' {
    $m=Fresh; MockLifecycle $m; $s=New-MuSession
    Assert (Start-MuSession $s '.')
    Assert ($s.Code -eq 'RUNNING')
    Assert (!(Start-MuSession $s '.'))
    Assert (Stop-MuSession $s)
    Assert ((Events $m) -join ',' -eq 'setup,hashes,ports,lock,ports,pg-start,pg-ready,db-check,server-start,server-ready,pg-recheck,client-start,client-stop,server-stop,pg-stop,dispose,unlock')
}
foreach ($stage in @('setup','hashes','ports')) {
    Check "preflight failure $stage never starts PostgreSQL" {
        $m=Fresh; MockLifecycle $m $stage; $s=New-MuSession
        Assert (!(Start-MuSession $s '.'))
        Assert ('pg-start' -notin (Events $m))
        Assert ($null -eq $s.Lock)
    }
}
foreach ($stage in @('pg-ready','db-check','server-ready','pg-recheck')) {
    Check "failure $stage never launches client and cleans in order" {
        $m=Fresh; MockLifecycle $m $stage; $s=New-MuSession
        Assert (!(Start-MuSession $s '.'))
        $events=@(Events $m)
        Assert ('client-start' -notin $events)
        Assert ([array]::IndexOf($events,'server-stop') -lt [array]::IndexOf($events,'pg-stop'))
        Assert ($null -eq $s.Lock)
    }
}
foreach ($stage in @('client-stop','server-stop','pg-stop')) {
    Check "failed $stage retains session for retry without further shutdown" {
        $m=Fresh; MockLifecycle $m; $s=New-MuSession; Assert (Start-MuSession $s '.')
        & $m { param($Stage) $script:failure=$Stage; $script:events.Clear() } $stage
        Assert (!(Stop-MuSession $s))
        Assert ($s.Code -eq 'STOP_FAILED' -and $null -ne $s.Lock)
        Assert ('unlock' -notin (Events $m))
        if ($stage -ne 'pg-stop') { Assert ('pg-stop' -notin (Events $m)) }
        & $m { $script:failure='' }
        Assert (Stop-MuSession $s)
    }
}
Check 'sanitized report excludes unknown fields, paths, credentials and raw status' {
    $m=Fresh; $s=New-MuSession
    $s.Code='Password=canary-secret'; $s.Setup=@{password='canary-secret'; root='private-owner-name'}
    $dir=Join-Path ([IO.Path]::GetTempPath()) ([guid]::NewGuid())
    $null=New-Item -ItemType Directory $dir
    try {
        $path=Write-MuReport $s $dir; $text=Get-Content -Raw $path; $report=$text | ConvertFrom-Json
        Assert ($text -notmatch 'canary-secret|private-owner-name')
        Assert ($report.status -eq 'START_FAILED' -and !$report.uploads -and !$report.rawLogsIncluded)
        Assert (@(Get-ChildItem $dir).Count -eq 1)
    } finally { Remove-Item -Recurse $dir }
}
Check 'path traversal and changed file hash rejected' {
    $m=Fresh; $dir=Join-Path ([IO.Path]::GetTempPath()) ([guid]::NewGuid())
    $null=New-Item -ItemType Directory $dir
    try {
        Set-Content (Join-Path $dir 'file') 'changed'
        $rejected=& $m { param($Root) try { Resolve-MuFile $Root '../escape'; $false } catch { $true } } $dir
        Assert $rejected
        $rejected=& $m {
            param($Root)
            try { Assert-MuHashes @{ root=$Root; hashes=@{file=('0'*64)} }; $false }
            catch { $_.Exception.Message -eq 'HASH_MISMATCH' }
        } $dir
        Assert $rejected
    } finally { Remove-Item -Recurse $dir }
}
Check 'listener guard rejects wildcard, extra TCP, UDP and missing ports' {
    $m=Fresh
    & $m {
        function script:Assert-MuOwner { }
        function script:Get-NetTCPConnection { return $script:tcp }
        function script:Get-NetUDPEndpoint { return $script:udp }
        $script:udp=@(); $script:tcp=@()
        if (Assert-MuListeners @{Pid=42} @(44406)) { throw 'Missing accepted' }
        $script:tcp=@([pscustomobject]@{OwningProcess=42;LocalAddress='127.0.0.1';LocalPort=44406})
        if (!(Assert-MuListeners @{Pid=42} @(44406))) { throw 'Safe rejected' }
        foreach ($mode in @('wildcard','extra','udp')) {
            $script:tcp[0].LocalAddress=if ($mode -eq 'wildcard') {'0.0.0.0'} else {'127.0.0.1'}
            $script:tcp[0].LocalPort=if ($mode -eq 'extra') {1234} else {44406}
            $script:udp=if ($mode -eq 'udp') {@([pscustomobject]@{OwningProcess=42})} else {@()}
            $rejected=$false
            try { $null=Assert-MuListeners @{Pid=42} @(44406) } catch { $rejected=$true }
            if (!$rejected) { throw "Accepted $mode" }
        }
    }
}
Check 'server timeout retains stdin ownership; retry sends exit only once' {
    $m=Fresh
    & $m {
        function script:Assert-MuOwner { }
        $writer=[IO.StringWriter]::new()
        $complete=[Threading.Tasks.Task]::CompletedTask
        $process=[pscustomobject]@{ StandardInput=$writer; ExitCode=0; WaitResult=$false }
        $process | Add-Member ScriptMethod WaitForExit { param($Timeout) return $this.WaitResult }
        function script:Invoke-MuQuery { return 1 }
        $s=New-MuSession; $s.Pg=@{}; $s.Server=@{Process=$process;Output=$complete;ErrorOutput=$complete;Observer=@{ErrorSeen=$false}}
        $failed=$false
        try { Stop-MuServer $s } catch { $failed=$true }
        if (!$failed -or !$s.ExitRequested -or $s.ServerStopped) { throw 'Timeout state wrong' }
        $process.WaitResult=$true
        Stop-MuServer $s
        if (!$s.ServerStopped -or $writer.ToString() -ne ('exit' + [Environment]::NewLine)) { throw 'Retry sent duplicate exit' }
        $writer.Dispose()
    }
}
Check 'occupied port rejects without adopting process' {
    $m=Fresh
    $blocked=& $m {
        function script:Get-NetTCPConnection { [pscustomobject]@{LocalPort=5432;OwningProcess=999} }
        try { Assert-MuPorts @(5432,44406); $false } catch { $_.Exception.Message -eq 'PORT_BUSY' }
    }
    Assert $blocked
}
Check 'durable marker refuses orphan adoption and remains intact' {
    $m=Fresh; $dir=Join-Path ([IO.Path]::GetTempPath()) ([guid]::NewGuid())
    $null=New-Item -ItemType Directory $dir
    try {
        $marker=Join-Path $dir '.mu-session-active'; Set-Content $marker 'orphan-canary'
        $blocked=& $m { param($Root) try { $null=Enter-MuLock $Root; $false } catch { $_.Exception.Message -eq 'OWNER_LOST' } } $dir
        Assert $blocked
        Assert ((Get-Content -Raw $marker).Trim() -eq 'orphan-canary')
    } finally { Remove-Item -Recurse -Force $dir }
}
Check 'real owned child drains output and honors stdin exit without force kill' {
    $m=Fresh
    & $m {
        $exe=(Get-Process -Id $PID).Path
        $child=Start-MuProcess $exe ([IO.Path]::GetTempPath()) @('-NoLogo','-NoProfile','-Command',
            '[Console]::Out.WriteLine("secret-not-retained"); while ([Console]::ReadLine() -ne "exit") {}') @{
                XDG_CACHE_HOME=$env:XDG_CACHE_HOME; XDG_CONFIG_HOME=$env:XDG_CONFIG_HOME; XDG_DATA_HOME=$env:XDG_DATA_HOME
            }
        try {
            Assert-MuOwner $child
            $correctTicks=$child.Ticks; $child.Ticks++
            $rejected=$false
            try { Assert-MuOwner $child } catch { $rejected=$true }
            if (!$rejected) { throw 'Reused identity accepted' }
            $child.Ticks=$correctTicks
            $child.Process.StandardInput.WriteLine('exit'); $child.Process.StandardInput.Flush()
            if (!$child.Process.WaitForExit(10000) -or $child.Process.ExitCode -ne 0) { throw 'Child failed' }
            if (!$child.Output.Wait(5000) -or !$child.ErrorOutput.Wait(5000)) { throw 'Pipe drain failed' }
        } finally { $child.Process.Dispose() }
    }
}
Write-Host "$script:passed tests passed. Fake lifecycle + harmless child only; Windows/game/database NOT RUN."
