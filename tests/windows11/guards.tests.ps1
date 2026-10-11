# Synthetic package/configuration tests. No actual DB, credentials, service or game.
$ErrorActionPreference='Stop'
$modulePath=Join-Path $PSScriptRoot '../../scripts/windows11/Launcher.psm1'
$script:passed=0
function Check([string]$Name,[scriptblock]$Body) { & $Body; $script:passed++; Write-Host "PASS $Name" }
function Assert($Condition) { if (!$Condition) { throw 'Assertion failed' } }
function Fresh {
    Remove-Module Launcher -ErrorAction SilentlyContinue
    return Import-Module $modulePath -Force -PassThru
}
function Clone($Value) { return $Value | ConvertTo-Json -Depth 30 | ConvertFrom-Json -AsHashtable }
function Reject($Module,[scriptblock]$Body,$Argument) {
    return & $Module { param($Body,$Argument) try { $null=& $Body $Argument; $false } catch { $true } } $Body $Argument
}
function New-Fixture {
    $root=Join-Path ([IO.Path]::GetTempPath()) ([guid]::NewGuid())
    foreach ($dir in @('server','client','pg/bin','dotnet','data')) { $null=New-Item -ItemType Directory (Join-Path $root $dir) -Force }
    $db=@{name='openmu';queryUser='mu_probe';pgPassFile='probe.pgpass';systemIdentifier='1234567890123456789';
        migrationSchema='public';migrationIds=@('20261010120000_Initial');runtimeRoles=@('mu_game');configurationIds=@('12345678-1234-1234-1234-123456789abc')}
    $setup=@{schema=1;runtimeArchive='runtime.zip';server='server';clientDirectory='client';pgDirectory='pg';dotnetDirectory='dotnet';pgData='data';
        dotnet='dotnet/dotnet.exe';postgres='pg/bin/postgres.exe';pgCtl='pg/bin/pg_ctl.exe';pgControlData='pg/bin/pg_controldata.exe';psql='pg/bin/psql.exe';client='client/Main.exe';
        hashes=@{};database=$db;versions=@{dotnet='10.0.11';postgres='17.11'};
        endpoints=@{game=@(@{port=55902;published=0});chat=@(@{port=55980});connect=@(@{port=44406})}}
    foreach ($file in @('runtime.zip','probe.pgpass',$setup.dotnet,$setup.postgres,$setup.pgCtl,$setup.pgControlData,$setup.psql,$setup.client,'server/MUnique.OpenMU.Startup.dll')) {
        Set-Content (Join-Path $root $file) 'synthetic-not-executable'
    }
    Set-Content (Join-Path $root 'data/PG_VERSION') '17'
    Set-Content (Join-Path $root 'data/postgresql.conf') "listen_addresses = '127.0.0.1'`nport = 5432`npassword_encryption = 'scram-sha-256'"
    Set-Content (Join-Path $root 'data/postgresql.auto.conf') '# no overrides'
    Set-Content (Join-Path $root 'data/pg_ident.conf') '# no mappings'
    Set-Content (Join-Path $root 'data/pg_hba.conf') "host openmu mu_probe 127.0.0.1/32 scram-sha-256`nhost openmu mu_game 127.0.0.1/32 scram-sha-256"
    $xml='<ConnectionSettings xmlns="http://www.munique.net/ConnectionSettings"><Connections>'
    foreach ($context in @('EntityDataContext','AdminAuth.AdminPanelContext','TypedContext','ConfigurationContext','AccountContext','TradeContext','FriendContext','GuildContext')) {
        $xml+="<Connection><ContextTypeName>MUnique.OpenMU.Persistence.EntityFramework.$context</ContextTypeName><ConnectionString>Server=127.0.0.1;Port=5432;Database=openmu;User Id=mu_game;Password=synthetic-only;</ConnectionString><DatabaseEngine>Npgsql</DatabaseEngine></Connection>"
    }
    Set-Content (Join-Path $root 'server/ConnectionSettings.xml') ($xml+'</Connections></ConnectionSettings>')
    @{DetailedErrors=$true;AllowedHosts='*';Database=@{AssumeExternallyProvisioned=$false};Serilog=@{WriteTo=@(@{Name='Console'},@{Name='File';Args=@{path='logs/log.txt'}})}} |
        ConvertTo-Json -Depth 10 | Set-Content (Join-Path $root 'server/appsettings.json')
    1..183 | ForEach-Object { Set-Content (Join-Path $root "server/payload-$_.dll") 'synthetic-payload' }
    foreach ($file in Get-ChildItem $root -Recurse -File) {
        $path=[IO.Path]::GetRelativePath($root,$file.FullName).Replace('\','/')
        $setup.hashes[$path]=(Get-FileHash $file.FullName).Hash.ToLowerInvariant()
    }
    return @{root=$root;setup=$setup}
}
$fixture=New-Fixture
$script:passed=0
try {
    $m=Fresh
    & $m {
        param($Fixture)
        $script:s=$Fixture.setup | ConvertTo-Json -Depth 30 | ConvertFrom-Json -AsHashtable
        Assert-MuSetupShape $script:s; $script:s.root=$Fixture.root
        $script:inventory=@{}
        foreach ($key in $s.hashes.Keys | Where-Object { $_.StartsWith('server/') }) { $script:inventory[$key.Substring(7)]=$s.hashes[$key] }
        function script:Read-MuRuntimeInventory { return $script:inventory }
        function script:Assert-MuPrivateFile { }
        function script:Assert-MuClientPin { }
    } $fixture
    Check 'valid shape, complete synthetic inventory and safe configuration' {
        & $m { Assert-MuHashes $s; Assert-MuConfiguration $s }
    }
    Check 'unknown schema field and path overlap rejected' {
        $bad=Clone $fixture.setup; $bad.extra=$true
        Assert (Reject $m {param($x) Assert-MuSetupShape $x} $bad)
        $bad=Clone $fixture.setup; $bad.pgData='server/data'
        Assert (Reject $m {param($x) Assert-MuSetupShape $x} $bad)
    }
    Check 'wrong hashes and incomplete runtime inventory rejected' {
        & $m {
            $key='server/payload-1.dll'; $hash=$s.hashes[$key]; $s.hashes[$key]='0'*64
            try { Assert-MuHashes $s; throw 'unexpected acceptance' } catch { if ($_.Exception.Message -ne 'HASH_MISMATCH') { throw } }
            finally { $s.hashes[$key]=$hash }
            $s.hashes.Remove($key)
            try { Assert-MuHashes $s; throw 'unexpected acceptance' } catch { if ($_.Exception.Message -ne 'HASH_MISMATCH') { throw } }
            finally { $s.hashes[$key]=$hash }
        }
    }
    Check 'extra DLL/config refused but expected runtime log tolerated' {
        $extra=Join-Path $fixture.root 'server/evil.dll'; Set-Content $extra 'unknown'
        try { Assert (Reject $m { Assert-MuHashes $s } $null) } finally { Remove-Item $extra }
        $logs=Join-Path $fixture.root 'server/logs'; $null=New-Item -ItemType Directory $logs
        Set-Content (Join-Path $logs 'log.txt') 'secret-log-canary'
        & $m { Assert-MuHashes $s }
    }
    foreach ($unsafe in @("include = 'elsewhere.conf'","shared_preload_libraries = 'evil'","listen_addresses = '*'")) {
        Check "PostgreSQL unsafe option rejected: $unsafe" {
            $path=Join-Path $fixture.root 'data/postgresql.conf'; $safe=Get-Content -Raw $path
            try { Add-Content $path $unsafe; Assert (Reject $m { Assert-MuPostgresConfig $s } $null) }
            finally { [IO.File]::WriteAllText($path,$safe) }
        }
    }
    Check 'CI trust and broad HBA rejected' {
        foreach ($line in @('host openmu mu_game 127.0.0.1/32 trust','host all all 0.0.0.0/0 scram-sha-256')) {
            Assert (Reject $m {param($x) Assert-MuHba $s @($x)} $line)
        }
    }
    Check 'nonempty auto config rejected' {
        $path=Join-Path $fixture.root 'data/postgresql.auto.conf'; $safe=Get-Content -Raw $path
        try { Add-Content $path "port = 5433"; Assert (Reject $m { Assert-MuPostgresConfig $s } $null) }
        finally { [IO.File]::WriteAllText($path,$safe) }
    }
    foreach ($unsafe in @('Server=0.0.0.0','Database=postgres','Options=-c bad=1;Server=127.0.0.1','Password=admin')) {
        Check "unsafe connection config rejected: $unsafe" {
            $path=Join-Path $fixture.root 'server/ConnectionSettings.xml'; $safe=Get-Content -Raw $path
            $changed=if ($unsafe.StartsWith('Password')) {$safe.Replace('Password=synthetic-only',$unsafe)}
                elseif ($unsafe.StartsWith('Database')) {$safe.Replace('Database=openmu',$unsafe)} else {$safe.Replace('Server=127.0.0.1',$unsafe)}
            try { [IO.File]::WriteAllText($path,$changed); Assert (Reject $m { Get-MuConnections $s } $null) }
            finally { [IO.File]::WriteAllText($path,$safe) }
        }
    }
    Check 'SQL snapshot accepts exact state and semantic endpoint key ordering' {
        & $m {
            $script:snapshot=@{database='openmu';address='127.0.0.1';port=5432;version='17.11';
                systems=@(@{readConsoleInput=$true;autoUpdateSchema=$false});configurationIds=$s.database.configurationIds;
                migrations=$s.database.migrationIds;game=@(@{published=0;port=55902});chat=$s.endpoints.chat;connect=$s.endpoints.connect}
            Assert-MuSnapshot $s $snapshot
        }
    }
    foreach ($failure in @('console','multi-system','auto-update','migrations','endpoint','database')) {
        Check "read-only state rejects $failure without repair" {
            $ok=& $m {
                param($Failure)
                $bad=$snapshot | ConvertTo-Json -Depth 20 | ConvertFrom-Json -AsHashtable
                switch ($Failure) {
                    'console' {$bad.systems[0].readConsoleInput=$false}
                    'multi-system' {$bad.systems+=@{readConsoleInput=$true;autoUpdateSchema=$false}}
                    'auto-update' {$bad.systems[0].autoUpdateSchema=$true}
                    'migrations' {$bad.migrations=@('20261010120001_Unknown')}
                    'endpoint' {$bad.game[0].port=60000}
                    'database' {$bad.database='other'}
                }
                try { Assert-MuSnapshot $s $bad; $false } catch { $true }
            } $failure
            Assert $ok
        }
    }
    Check 'read-only adapter uses isolated environment, no password argv and fixed read-only transaction' {
        & $m {
            function script:Assert-MuAreaHashes { }
            function script:Get-MuEnvironment { return @{} }
            function script:Invoke-MuProbe {
                param($File,$Directory,$Arguments,$Environment)
                if (($Arguments -join ' ') -match 'synthetic-secret' -or $Environment.PGOPTIONS -notmatch 'default_transaction_read_only=on' -or
                    $Arguments[-1] -cne 'BEGIN READ ONLY; SELECT to_json(1); COMMIT;' -or $Environment.PGPASSWORD -cne 'synthetic-secret') { throw 'Unsafe query adapter' }
                return '1'
            }
            if ((Invoke-MuQuery $s 'SELECT to_json(1)' @{user='mu_game';password='synthetic-secret'}) -ne 1) { throw 'Wrong query result' }
        }
    }
    Check 'approved manifest loader works in isolated fixture and rejects receipt tampering' {
        $scripts=Join-Path $fixture.root 'isolated-launcher'
        Copy-Item (Split-Path $modulePath) $scripts -Recurse
        $manifest=Join-Path $fixture.root 'windows11-launch-manifest.json'
        $fixture.setup | ConvertTo-Json -Depth 30 | Set-Content $manifest
        @{launchEnabled=$true;approvedLaunchManifestSha256=(Get-FileHash $manifest).Hash.ToLowerInvariant()} |
            ConvertTo-Json | Set-Content (Join-Path $scripts 'local-session-contract.json')
        Remove-Module Launcher -ErrorAction SilentlyContinue
        $loader=Import-Module (Join-Path $scripts 'Launcher.psm1') -PassThru -Force
        & $loader {
            param($Fixture)
            $script:inventory=@{}
            foreach ($key in $Fixture.setup.hashes.Keys | Where-Object { $_.StartsWith('server/') }) {
                $script:inventory[$key.Substring(7)]=$Fixture.setup.hashes[$key]
            }
            function script:Read-MuRuntimeInventory { return $script:inventory }
            function script:Assert-MuPrivateFile { }
        function script:Assert-MuClientPin { }
            function script:Assert-MuDependencies { }
        } $fixture
        $loaded=& $loader {param($Root) Get-MuApprovedSetup $Root} $fixture.root
        Assert ($loaded.database.name -eq 'openmu' -and 55902 -in $loaded.serverPorts)
        Add-Content $manifest ' '
        Assert (Reject $loader {param($Root) Get-MuApprovedSetup $Root} $fixture.root)
        Remove-Item $manifest
        Assert (Reject $loader {param($Root) Get-MuApprovedSetup $Root} $fixture.root)
    }
    Check 'database guard checks every runtime credential and rejects elevated role' {
        $dbModule=Fresh
        & $dbModule {
            param($Fixture)
            $script:s=$Fixture.setup | ConvertTo-Json -Depth 30 | ConvertFrom-Json -AsHashtable
            Assert-MuSetupShape $s; $s.root=$Fixture.root
            $script:calls=0; $script:unsafeRole=$false
            function script:Assert-MuPrivateFile { }
        function script:Assert-MuClientPin { }
            function script:Assert-MuSnapshot { }
            function script:Invoke-MuQuery {
                param($Setup,$Sql,$Credential)
                if ($Sql -match 'pg_roles') {
                    $script:calls++
                    return @{user=$(if ($null -eq $Credential) {$Setup.database.queryUser} else {$Credential.user});safe=(!$script:unsafeRole)}
                }
                return @{}
            }
            Assert-MuDatabase $s
            if ($script:calls -ne 9) { throw 'Credential coverage missing' }
            $script:unsafeRole=$true
            $failed=$false
            try { Assert-MuDatabase $s } catch { $failed=$true }
            if (!$failed) { throw 'Elevated role accepted' }
        } $fixture
    }
    Check 'PostgreSQL stop retry reuses timed-out utility and accepts its later completion' {
        $stopModule=Fresh
        Set-Content (Join-Path $fixture.root 'data/postmaster.pid') '42'
        & $stopModule {
            param($Fixture)
            $s=New-MuSession; $s.Setup=$Fixture.setup; $s.Setup.root=$Fixture.root
            $pg=[pscustomobject]@{HasExited=$false;ExitCode=0}
            $pg | Add-Member ScriptMethod WaitForExit { param($Timeout) return $this.HasExited }
            $s.Pg=@{Pid=42;Process=$pg}
            $script:utility=[pscustomobject]@{Ready=$false;ExitCode=0}
            $script:utility | Add-Member ScriptMethod WaitForExit { param($Timeout) return $this.Ready }
            $script:starts=0
            function script:Assert-MuOwner($Owned) { if ($Owned.Process.HasExited) { throw 'Unexpected owner check after exit' } }
            function script:Assert-MuAreaHashes { }
            function script:Get-MuEnvironment { return @{} }
            function script:Save-MuOwners { }
            function script:Start-MuProcess { $script:starts++; return @{Process=$script:utility} }
            $failed=$false
            try { Stop-MuPostgres $s } catch { $failed=$true }
            if (!$failed -or $null -eq $s.PgStop) { throw 'Timeout lost utility' }
            $script:utility.Ready=$true; $pg.HasExited=$true
            Stop-MuPostgres $s
            if ($script:starts -ne 1) { throw 'Duplicate shutdown utility' }
        } $fixture
        Remove-Item (Join-Path $fixture.root 'data/postmaster.pid')
    }
    Check 'client baseline pin rejects synthetic or missing client and overlay bytes' {
        $clean=Fresh
        Assert (Reject $clean {param($x) Assert-MuClientPin $x} $fixture.setup)
    }
    Check 'real artifact reader rejects unpinned archive bytes' {
        $clean=Fresh
        Assert (Reject $clean {param($x) $x.setup.root=$x.root; Read-MuRuntimeInventory $x.setup} (Clone $fixture))
    }
    Check 'reports reject network destination rather than write there' {
        $clean=Fresh
        Assert (Reject $clean { Write-MuReport (New-MuSession) '\\server\share' } $null)
    }
    Check 'actual bounded observer sees PID and error marker without retaining raw lines' {
        $clean=Fresh
        & $clean {
            $exe=(Get-Process -Id $PID).Path
            $envMap=@{}
            foreach ($key in @('XDG_CACHE_HOME','XDG_CONFIG_HOME','XDG_DATA_HOME','SystemRoot','WINDIR','TEMP','TMP')) {
                $value=[Environment]::GetEnvironmentVariable($key); if ($value) { $envMap[$key]=$value }
            }
            $p=Start-MuProcess $exe ([IO.Path]::GetTempPath()) @('-NoLogo','-NoProfile','-Command',
                '[Console]::WriteLine("PID: " + $PID); [Console]::WriteLine("Error synthetic-secret"); while ([Console]::ReadLine() -ne "exit") {}') $envMap -Observe
            try {
                $p.Process.StandardInput.WriteLine('exit'); $p.Process.StandardInput.Flush()
                if (!$p.Process.WaitForExit(10000) -or !$p.Output.Wait(5000) -or !$p.Observer.PidSeen -or !$p.Observer.ErrorSeen) { throw 'Observation failed' }
            } finally { $p.Process.Dispose() }
        }
    }
    Write-Host "$script:passed guard tests passed. Synthetic only; Windows/runtime/DB NOT RUN."
} finally { Remove-Item -Recurse -Force $fixture.root }
