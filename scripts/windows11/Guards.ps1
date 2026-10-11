# Read-only package/configuration guards. No setup generation or repair.
function Assert-MuKeys($Object, [string[]]$Keys) {
    if ($Object -isnot [Collections.IDictionary] -or
        @(Compare-Object @($Object.Keys | Sort-Object) @($Keys | Sort-Object) -CaseSensitive).Count) { throw 'UNSAFE_CONFIG' }
}

function Assert-MuLocalPath([string]$Path) {
    if (![IO.Path]::IsPathFullyQualified($Path) -or $Path.StartsWith('\\')) { throw 'UNSAFE_CONFIG' }
    if ($IsWindows -and [IO.DriveInfo]::new([IO.Path]::GetPathRoot($Path)).DriveType -ne 'Fixed') { throw 'UNSAFE_CONFIG' }
    $cursor=Get-Item -LiteralPath $Path -Force
    while ($null -ne $cursor) {
        if ($cursor.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'UNSAFE_CONFIG' }
        $parent=Split-Path $cursor.FullName
        if (!$parent -or $parent -eq $cursor.FullName) { break }
        $cursor=Get-Item -LiteralPath $parent -Force
    }
}

function Assert-MuRelative([string]$Relative) {
    if (!$Relative -or $Relative -match '[\\:]|^/|//|(^|/)(\.|\.\.)(/|$)|[ .](/|$)' -or
        $Relative -match '[\x00-\x1f*?<>|"]' -or $Relative -match '(?i)(^|/)(CON|PRN|AUX|NUL|COM[0-9]|LPT[0-9])(\.|/|$)') {
        throw 'UNSAFE_CONFIG'
    }
}

function Resolve-MuFile([string]$Root, [string]$Relative) {
    Assert-MuRelative $Relative
    $base=[IO.Path]::GetFullPath($Root).TrimEnd([IO.Path]::DirectorySeparatorChar)
    $path=[IO.Path]::GetFullPath((Join-Path $base $Relative))
    if (!$path.StartsWith($base + [IO.Path]::DirectorySeparatorChar,[StringComparison]::OrdinalIgnoreCase)) { throw 'UNSAFE_CONFIG' }
    Assert-MuLocalPath $path
    return $path
}

function Assert-MuFileHash([string]$Path, [string]$Hash) {
    if ($Hash -cnotmatch '^[a-f0-9]{64}$' -or
        (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash -ine $Hash) { throw 'HASH_MISMATCH' }
}

function Read-MuJson([string]$Path) {
    if ((Get-Item -LiteralPath $Path).Length -gt 4MB) { throw 'UNSAFE_CONFIG' }
    return Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json -AsHashtable -Depth 40
}

function Get-MuApprovedSetup([string]$Root) {
    Assert-MuLocalPath $Root
    $contract=Read-MuJson (Join-Path $PSScriptRoot 'local-session-contract.json')
    # The release reviewer pins the actual setup manifest, not an editable "ready"
    # assertion. This repository contains no approved owner setup or invented pin.
    if ($contract.launchEnabled -isnot [bool] -or $contract.launchEnabled -ne $true -or $contract.approvedLaunchManifestSha256 -cnotmatch '^[a-f0-9]{64}$') { throw 'SETUP_REQUIRED' }
    $path=Join-Path $Root 'windows11-launch-manifest.json'
    if (!(Test-Path -LiteralPath $path -PathType Leaf)) { throw 'MANIFEST_REQUIRED' }
    Assert-MuLocalPath $path
    Assert-MuFileHash $path $contract.approvedLaunchManifestSha256
    $setup=Read-MuJson $path
    Assert-MuSetupShape $setup
    $setup.root=[IO.Path]::GetFullPath($Root)
    Assert-MuHashes $setup
    Assert-MuConfiguration $setup
    Assert-MuDependencies $setup
    return $setup
}

function Assert-MuSetupShape($Setup) {
    Assert-MuKeys $Setup @('schema','runtimeArchive','server','clientDirectory','pgDirectory','dotnetDirectory',
        'pgData','dotnet','postgres','pgCtl','pgControlData','psql','client','hashes','database','endpoints','versions')
    if ($Setup.schema -ne 2) { throw 'UNSAFE_CONFIG' }
    foreach ($key in @('runtimeArchive','server','clientDirectory','pgDirectory','dotnetDirectory','pgData',
        'dotnet','postgres','pgCtl','pgControlData','psql','client')) { Assert-MuRelative $Setup[$key] }
    Assert-MuKeys $Setup.versions @('dotnet','postgres')
    if ($Setup.versions.dotnet -cne '10.0.11' -or $Setup.versions.postgres -cne '17.11') { throw 'UNSAFE_CONFIG' }
    $areas=@($Setup.server,$Setup.clientDirectory,$Setup.pgDirectory,$Setup.dotnetDirectory,$Setup.pgData)
    foreach ($a in $areas) { foreach ($b in $areas) {
        if ($a -ne $b -and $a.StartsWith($b + '/', [StringComparison]::OrdinalIgnoreCase)) { throw 'UNSAFE_CONFIG' }
    } }
    if (@($areas | Sort-Object -Unique).Count -ne 5) { throw 'UNSAFE_CONFIG' }
    $executables=@{dotnet=($Setup.dotnetDirectory + '/dotnet.exe'); client=($Setup.clientDirectory + '/Main.exe');
        postgres=($Setup.pgDirectory + '/bin/postgres.exe'); pgCtl=($Setup.pgDirectory + '/bin/pg_ctl.exe');
        pgControlData=($Setup.pgDirectory + '/bin/pg_controldata.exe'); psql=($Setup.pgDirectory + '/bin/psql.exe')}
    foreach ($key in $executables.Keys) { if ($Setup[$key] -cne $executables[$key]) { throw 'UNSAFE_CONFIG' } }
    Assert-MuDatabaseShape $Setup.database
    $databaseSource=Get-MuDatabaseSourceContract
    $migrationAssembly=$Setup.server + '/' + $databaseSource.migrationAssembly
    if (!$Setup.hashes.ContainsKey($migrationAssembly) -or
        $Setup.hashes[$migrationAssembly] -cne $databaseSource.migrationAssemblySha256) { throw 'HASH_MISMATCH' }
    Assert-MuEndpointShape $Setup.endpoints
    $expectedEndpoints=(Get-MuDatabaseSourceContract).endpoints
    foreach ($kind in @('game','chat','connect')) {
        $expected=@($expectedEndpoints[$kind] | ForEach-Object { if ($kind -eq 'game') { '{0}:{1}' -f $_.port,$_.published } else { [string]$_.port } })
        $actual=@($Setup.endpoints[$kind] | ForEach-Object { if ($kind -eq 'game') { '{0}:{1}' -f $_.port,$_.published } else { [string]$_.port } })
        Assert-MuExactStrings $actual $expected '^[0-9]+(:[0-9]+)?$'
    }
    $Setup.serverPorts=@(@($Setup.endpoints.game.port) + @($Setup.endpoints.chat.port) +
        @($Setup.endpoints.connect.port) + @(18080) | Sort-Object -Unique)
    if (5432 -in $Setup.serverPorts -or 44406 -notin $Setup.serverPorts -or 55902 -notin $Setup.serverPorts) { throw 'UNSAFE_CONFIG' }
}

function Get-MuDatabaseSourceContract {
    # Independent pinned-source/export expectations, never populated by a DB probe.
    $path=Join-Path $PSScriptRoot 'database-source-contract.json'
    Assert-MuLocalPath $path
    Assert-MuFileHash $path '0718c51ba1367d476a5d3fff7a46e55b16f334688ecbb650af7148b836c2cac6'
    return Read-MuJson $path
}

function Assert-MuExactStrings($Actual, $Expected, [string]$Pattern) {
    # Do not let Compare-Object hide duplicate, scalar, null or malformed identities.
    if ($Actual -isnot [array] -or $Expected -isnot [array] -or !$Actual.Count -or
        $Actual.Count -ne $Expected.Count) { throw 'UNSAFE_CONFIG' }
    foreach ($value in $Actual) {
        if ($value -isnot [string] -or $value -cnotmatch $Pattern) { throw 'UNSAFE_CONFIG' }
    }
    if (@($Actual | Sort-Object -Unique).Count -ne $Actual.Count -or
        @(Compare-Object @($Expected | Sort-Object) @($Actual | Sort-Object) -CaseSensitive).Count) { throw 'UNSAFE_CONFIG' }
}

function Assert-MuDatabaseShape($Db) {
    Assert-MuKeys $Db @('name','queryUser','pgPassFile','systemIdentifier','migrationHistories','runtimeRoles','configurationIds')
    foreach ($value in @($Db.name,$Db.queryUser) + @($Db.runtimeRoles)) {
        if ($value -isnot [string] -or $value -cnotmatch '^[a-z_][a-z0-9_]{0,62}$') { throw 'UNSAFE_CONFIG' }
    }
    Assert-MuRelative $Db.pgPassFile
    if ($Db.name -cne 'openmu' -or $Db.systemIdentifier -cnotmatch '^[0-9]{10,20}$' -or
        $Db.runtimeRoles -isnot [array] -or !$Db.runtimeRoles.Count -or $Db.queryUser -in $Db.runtimeRoles -or
        @($Db.runtimeRoles | Sort-Object -Unique).Count -ne $Db.runtimeRoles.Count) { throw 'UNSAFE_CONFIG' }
    $contract=Get-MuDatabaseSourceContract
    Assert-MuExactStrings $Db.configurationIds $contract.configurationIds '^[a-f0-9]{8}(-[a-f0-9]{4}){3}-[a-f0-9]{12}$'
    Assert-MuKeys $Db.migrationHistories @('EntityDataContext','AdminAuth.AdminPanelContext')
    foreach ($context in @('EntityDataContext','AdminAuth.AdminPanelContext')) {
        $history=$Db.migrationHistories[$context]; $expected=$contract.migrationHistories[$context]
        Assert-MuKeys $history @('schema','table','ids')
        if ($history.schema -cne $expected.schema -or $history.table -cne $expected.table) { throw 'UNSAFE_CONFIG' }
        Assert-MuExactStrings $history.ids $expected.ids '^[0-9]{14}_[A-Za-z0-9_]+$'
    }
}

function Assert-MuEndpointShape($Endpoints) {
    Assert-MuKeys $Endpoints @('game','chat','connect')
    foreach ($kind in @('game','chat','connect')) {
        if (!$Endpoints[$kind].Count) { throw 'UNSAFE_CONFIG' }
        foreach ($entry in $Endpoints[$kind]) {
            $keys=if ($kind -eq 'game') { @('port','published') } else { @('port') }
            Assert-MuKeys $entry $keys
            if ($entry.port -isnot [long] -and $entry.port -isnot [int]) { throw 'UNSAFE_CONFIG' }
            if ($entry.port -lt 1 -or $entry.port -gt 65535 -or $entry.port -in @(5432,18080)) { throw 'UNSAFE_CONFIG' }
            if ($kind -eq 'game' -and $entry.published -ne 0 -and $entry.published -ne $entry.port) { throw 'UNSAFE_CONFIG' }
        }
    }
}

function Read-MuRuntimeInventory($Setup) {
    $path=Resolve-MuFile $Setup.root $Setup.runtimeArchive
    Assert-MuFileHash $path '505d1053d235417876c59f31e2dbb0338bad955dee31c193ccf167da28355f8c'
    $zip=[IO.Compression.ZipFile]::OpenRead($path)
    try {
        $entries=@($zip.Entries | Where-Object Name -eq 'runtime-manifest.json')
        if ($entries.Count -ne 1 -or $entries[0].Length -gt 1MB) { throw 'HASH_MISMATCH' }
        $reader=[IO.StreamReader]::new($entries[0].Open())
        try { $inventory=$reader.ReadToEnd() | ConvertFrom-Json -AsHashtable } finally { $reader.Dispose() }
        $inner=@($zip.Entries | Where-Object Name -eq 'openmu-money-local-bind-runtime.zip')
        if ($inner.Count -ne 1) { throw 'HASH_MISMATCH' }
        $stream=$inner[0].Open(); $sha=[Security.Cryptography.SHA256]::Create()
        try { $digest=[Convert]::ToHexString($sha.ComputeHash($stream)).ToLowerInvariant() }
        finally { $stream.Dispose(); $sha.Dispose() }
        if ($digest -cne '4b1b1d71a0aa992fb3f2dbac7e447a5704cccc7ed38ebacfdebe97eabebf1eec' -or $inventory.Count -ne 186) { throw 'HASH_MISMATCH' }
        return $inventory
    } finally { $zip.Dispose() }
}

function Assert-MuTree($Setup, [string]$Area) {
    $root=Resolve-MuFile $Setup.root $Area
    foreach ($item in Get-ChildItem -LiteralPath $root -Recurse -Force) {
        if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'UNSAFE_CONFIG' }
        if ($item.PSIsContainer) { continue }
        $relative=[IO.Path]::GetRelativePath($Setup.root,$item.FullName).Replace('\','/')
        # The pinned logger and native client may write logs. Nothing under these
        # exclusions is consumed as code/config or copied to CollectReport.
        $serverLog=$relative.StartsWith($Setup.server + '/logs/') -and $item.Extension -eq '.txt'
        $clientLog=$item.DirectoryName -eq (Join-Path $Setup.root $Setup.clientDirectory) -and $item.Extension -eq '.log'
        if (!$Setup.hashes.ContainsKey($relative) -and !$serverLog -and !$clientLog) { throw 'HASH_MISMATCH' }
    }
}

function Assert-MuHashes($Setup) {
    if ($Setup.hashes.Count -eq 0) { throw 'MANIFEST_REQUIRED' }
    $unique=[Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
    foreach ($relative in $Setup.hashes.Keys) { if (!$unique.Add($relative)) { throw 'UNSAFE_CONFIG' } }
    foreach ($relative in $Setup.hashes.Keys) { Assert-MuFileHash (Resolve-MuFile $Setup.root $relative) $Setup.hashes[$relative] }
    $required=@($Setup.dotnet,$Setup.postgres,$Setup.pgCtl,$Setup.pgControlData,$Setup.psql,$Setup.client,$Setup.database.pgPassFile)
    foreach ($name in @('PG_VERSION','postgresql.conf','postgresql.auto.conf','pg_hba.conf','pg_ident.conf')) { $required+=($Setup.pgData + '/' + $name) }
    foreach ($path in $required) { if (!$Setup.hashes.ContainsKey($path)) { throw 'HASH_MISMATCH' } }
    foreach ($area in @($Setup.server,$Setup.clientDirectory,$Setup.pgDirectory,$Setup.dotnetDirectory)) { Assert-MuTree $Setup $area }
    Assert-MuClientPin $Setup
    $inventory=Read-MuRuntimeInventory $Setup
    foreach ($relative in $inventory.Keys) {
        Assert-MuRelative $relative
        $key=$Setup.server + '/' + $relative
        if (!$Setup.hashes.ContainsKey($key)) { throw 'HASH_MISMATCH' }
        # Only an explicitly reviewed authentication config may differ from build bytes.
        if ($relative -cne 'ConnectionSettings.xml' -and $Setup.hashes[$key] -cne $inventory[$relative]) { throw 'HASH_MISMATCH' }
    }
    $serverEntries=@($Setup.hashes.Keys | Where-Object { $_.StartsWith($Setup.server + '/') })
    if ($serverEntries.Count -ne 186) { throw 'HASH_MISMATCH' }
}

function Read-MuConfigLines([string]$Path) {
    return @(Get-Content -LiteralPath $Path | ForEach-Object { ($_ -split '#',2)[0].Trim() } | Where-Object { $_ })
}

function Assert-MuPostgresConfig($Setup) {
    $data=Resolve-MuFile $Setup.root $Setup.pgData
    if ((Get-Content -Raw (Join-Path $data 'PG_VERSION')).Trim() -cne '17') { throw 'UNSAFE_CONFIG' }
    $config=@{}
    foreach ($line in Read-MuConfigLines (Join-Path $data 'postgresql.conf')) {
        if ($line -cnotmatch "^([a-z_]+)\s*=\s*('[^']*'|[0-9]+[A-Za-z]*|on|off)$") { throw 'UNSAFE_CONFIG' }
        $key=$Matches[1]; $value=$Matches[2].Trim("'")
        if ($config.ContainsKey($key) -or $key -notin @('listen_addresses','port','password_encryption',
            'shared_preload_libraries','session_preload_libraries','local_preload_libraries','max_connections',
            'shared_buffers','logging_collector','log_destination','timezone','datestyle','log_statement','log_min_error_statement')) { throw 'UNSAFE_CONFIG' }
        $config[$key]=$value
    }
    if ($config.listen_addresses -cne '127.0.0.1' -or $config.port -cne '5432' -or
        $config.password_encryption -cne 'scram-sha-256') { throw 'UNSAFE_CONFIG' }
    foreach ($key in @('shared_preload_libraries','session_preload_libraries','local_preload_libraries')) {
        if ($config.ContainsKey($key) -and $config[$key] -ne '') { throw 'UNSAFE_CONFIG' }
    }
    if ($config.ContainsKey('log_destination') -and $config.log_destination -cne 'stderr') { throw 'UNSAFE_CONFIG' }
    if ($config.ContainsKey('log_statement') -and $config.log_statement -cne 'none') { throw 'UNSAFE_CONFIG' }
    if ($config.ContainsKey('log_min_error_statement') -and $config.log_min_error_statement -cne 'panic') { throw 'UNSAFE_CONFIG' }
    if (@(Read-MuConfigLines (Join-Path $data 'postgresql.auto.conf')).Count -or
        @(Read-MuConfigLines (Join-Path $data 'pg_ident.conf')).Count) { throw 'UNSAFE_CONFIG' }
    Assert-MuHba $Setup (Read-MuConfigLines (Join-Path $data 'pg_hba.conf'))
    foreach ($item in Get-ChildItem -LiteralPath $data -Recurse -Force) {
        if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'UNSAFE_CONFIG' }
        if ($item.Extension -eq '.conf' -and !$Setup.hashes.ContainsKey($Setup.pgData + '/' + [IO.Path]::GetRelativePath($data,$item.FullName).Replace('\','/'))) { throw 'UNSAFE_CONFIG' }
    }
}

function Assert-MuHba($Setup, [string[]]$Lines) {
    $roles=@($Setup.database.runtimeRoles) + @($Setup.database.queryUser) | Sort-Object -Unique
    $seen=@()
    foreach ($line in $Lines) {
        $parts=$line -split '\s+'
        if ($parts.Count -ne 5 -or $parts[0] -cne 'host' -or $parts[1] -cne $Setup.database.name -or
            $parts[2] -notin $roles -or $parts[3] -cne '127.0.0.1/32' -or $parts[4] -cne 'scram-sha-256') { throw 'UNSAFE_CONFIG' }
        $seen+=$parts[2]
    }
    if (@(Compare-Object @($roles) @($seen | Sort-Object -Unique)).Count) { throw 'UNSAFE_CONFIG' }
}

function Assert-MuPrivateFile([string]$Path) {
    if (!$IsWindows) { throw 'WINDOWS_REQUIRED' }
    $allowed=@([Security.Principal.WindowsIdentity]::GetCurrent().User.Value,'S-1-5-18','S-1-5-32-544')
    $acl=Get-Acl -LiteralPath $Path
    if ($acl.GetOwner([Security.Principal.SecurityIdentifier]).Value -notin $allowed) { throw 'UNSAFE_CONFIG' }
    foreach ($rule in $acl.GetAccessRules($true,$true,[Security.Principal.SecurityIdentifier])) {
        if ($rule.AccessControlType -eq 'Allow' -and $rule.IdentityReference.Value -notin $allowed) { throw 'UNSAFE_CONFIG' }
    }
}

function Assert-MuConnectionSchemaMode($Entry,[string]$Name) {
    $children=@($Entry.ChildNodes | Where-Object NodeType -eq 'Element')
    $expected=@('ConnectionString','ContextTypeName','DatabaseEngine')
    if ($Name -ceq 'AdminAuth.AdminPanelContext') { $expected+=@('AdminSchemaManagement') }
    if ($children.Count -ne $expected.Count -or
        @($children | Where-Object NamespaceURI -cne 'http://www.munique.net/ConnectionSettings').Count -or
        @(Compare-Object @($children.LocalName | Sort-Object) @($expected | Sort-Object) -CaseSensitive).Count) { throw 'UNSAFE_CONFIG' }
    if ($Name -ceq 'AdminAuth.AdminPanelContext' -and [string]$Entry.AdminSchemaManagement -cne 'ExternallyProvisioned') { throw 'UNSAFE_CONFIG' }
}

function Get-MuConnections($Setup) {
    $path=Resolve-MuFile $Setup.root ($Setup.server + '/ConnectionSettings.xml')
    Assert-MuPrivateFile $path
    $settings=[Xml.XmlReaderSettings]::new(); $settings.DtdProcessing='Prohibit'; $settings.XmlResolver=$null
    $reader=[Xml.XmlReader]::Create($path,$settings); $xml=[Xml.XmlDocument]::new(); $xml.XmlResolver=$null
    try { $xml.Load($reader) } finally { $reader.Dispose() }
    if ($xml.DocumentElement.LocalName -cne 'ConnectionSettings' -or $xml.DocumentElement.NamespaceURI -cne 'http://www.munique.net/ConnectionSettings') { throw 'UNSAFE_CONFIG' }
    $entries=@($xml.SelectNodes('//*[local-name()="Connection"]'))
    $contexts=@('EntityDataContext','AdminAuth.AdminPanelContext','TypedContext','ConfigurationContext','AccountContext','TradeContext','FriendContext','GuildContext')
    if ($entries.Count -ne $contexts.Count) { throw 'UNSAFE_CONFIG' }
    $result=@{}
    foreach ($entry in $entries) {
        $context=[string]$entry.ContextTypeName
        $name=$context -creplace '^MUnique.OpenMU.Persistence.EntityFramework\.',''
        Assert-MuConnectionSchemaMode $entry $name
        if ($context -cne ('MUnique.OpenMU.Persistence.EntityFramework.' + $name) -or $name -notin $contexts -or $result.ContainsKey($name) -or $entry.DatabaseEngine -cne 'Npgsql') { throw 'UNSAFE_CONFIG' }
        $cs=[Data.Common.DbConnectionStringBuilder]::new(); $cs.set_ConnectionString([string]$entry.ConnectionString)
        foreach ($key in $cs.get_Keys()) { if ($key -notin @('Server','Port','Database','User Id','Password','Command Timeout','Pooling','Minimum Pool Size','Maximum Pool Size','Timeout')) { throw 'UNSAFE_CONFIG' } }
        if ($cs['Server'] -cne '127.0.0.1' -or [int]$cs['Port'] -ne 5432 -or $cs['Database'] -cne $Setup.database.name -or
            $cs['User Id'] -notin $Setup.database.runtimeRoles -or ![string]$cs['Password'] -or
            $cs['Password'] -in @([string]$cs['User Id'],'admin','password')) { throw 'UNSAFE_CONFIG' }
        $result[$name]=@{user=[string]$cs['User Id']; password=[string]$cs['Password']}
    }
    if (@(Compare-Object @($result.Values.user | Sort-Object -Unique) @($Setup.database.runtimeRoles | Sort-Object) -CaseSensitive).Count) { throw 'UNSAFE_CONFIG' }
    return $result
}

function Assert-MuConfiguration($Setup) {
    Assert-MuPostgresConfig $Setup
    Assert-MuPrivateFile (Resolve-MuFile $Setup.root $Setup.database.pgPassFile)
    $null=Get-MuConnections $Setup
    $server=Resolve-MuFile $Setup.root $Setup.server
    $known=@('appsettings.json','MUnique.OpenMU.Startup.runtimeconfig.json',
        'MUnique.OpenMU.Web.AdminPanel.runtimeconfig.json','MUnique.OpenMU.Web.Map.runtimeconfig.json')
    foreach ($file in Get-ChildItem -LiteralPath $server -Recurse -File) {
        if ($file.Extension -eq '.config' -or (($file.Name -like 'appsettings*' -or $file.Name -like '*.runtimeconfig*.json') -and
            ($file.DirectoryName -ne $server -or $file.Name -notin $known))) { throw 'UNSAFE_CONFIG' }
    }
    # These bytes must also equal the inventory from the exact approved build.
    $app=Read-MuJson (Join-Path $server 'appsettings.json')
    Assert-MuKeys $app @('DetailedErrors','AllowedHosts','Database','Serilog')
    Assert-MuKeys $app.Database @('AssumeExternallyProvisioned')
    if ($app.Database.AssumeExternallyProvisioned -ne $false) { throw 'UNSAFE_CONFIG' }
    $sinks=@($app.Serilog.WriteTo)
    if ($sinks.Count -ne 2 -or $sinks[0].Name -cne 'Console' -or $sinks[1].Name -cne 'File' -or
        $sinks[1].Args.path -cne 'logs/log.txt') { throw 'UNSAFE_CONFIG' }
}

function Assert-MuAreaHashes($Setup, [string]$Area) {
    Assert-MuTree $Setup $Area
    foreach ($path in $Setup.hashes.Keys | Where-Object { $_.StartsWith($Area + '/') }) {
        Assert-MuFileHash (Resolve-MuFile $Setup.root $path) $Setup.hashes[$path]
    }
}

function Assert-MuClientPin($Setup) {
    $pins=@{
        'Main.exe'='9d895c638eb256b98d728dfc511f4c57d4a9e88cdba703e639426712b0b57cd5'
        'MUnique.Client.Library.dll'='9292041494d9226f105fc07a94c2451f6303b906123b2932ea05a3469c378cb7'
        'Data/Items/Group12_Wing.json'='1441360f93d80291659f63912022e0816125863acd0212ab4ec02fca33ebbb73'
    }
    foreach ($relative in $pins.Keys) {
        $key=$Setup.clientDirectory + '/' + $relative
        if (!$Setup.hashes.ContainsKey($key) -or $Setup.hashes[$key] -cne $pins[$relative]) { throw 'HASH_MISMATCH' }
    }
    foreach ($area in @('Data','fonts','shaders')) {
        $prefix=$Setup.clientDirectory + '/' + $area + '/'
        if (!@($Setup.hashes.Keys | Where-Object { $_.StartsWith($prefix) }).Count) { throw 'HASH_MISMATCH' }
    }
}
