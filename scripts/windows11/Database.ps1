# Fixed read-only probes; credentials remain in child memory, never reports/logs.
function Invoke-MuProbe([string]$File, [string]$Directory, [string[]]$Arguments, $Environment, [int]$Seconds=15) {
    $info=[Diagnostics.ProcessStartInfo]::new()
    $info.FileName=$File; $info.WorkingDirectory=$Directory; $info.UseShellExecute=$false
    $info.RedirectStandardInput=$true; $info.RedirectStandardOutput=$true; $info.RedirectStandardError=$true
    $info.Environment.Clear()
    foreach ($key in $Environment.Keys) { $info.Environment[$key]=$Environment[$key] }
    foreach ($argument in $Arguments) { $info.ArgumentList.Add($argument) }
    $process=[Diagnostics.Process]::new(); $process.StartInfo=$info; $started=$false
    try {
        if (!$process.Start()) { throw 'PROBE_FAILED' }; $started=$true
        $process.StandardInput.Close()
        $output=$process.StandardOutput.ReadToEndAsync()
        $errorDrain=$process.StandardError.BaseStream.CopyToAsync([IO.Stream]::Null)
        if (!$process.WaitForExit($Seconds * 1000)) { throw 'PROBE_FAILED' }
        if (!$output.Wait(5000) -or !$errorDrain.Wait(5000) -or $process.ExitCode -ne 0) { throw 'PROBE_FAILED' }
        if ($output.Result.Length -gt 1MB) { throw 'PROBE_FAILED' }
        return $output.Result.Trim()
    } catch { throw 'PROBE_FAILED' }
    finally {
        # Only this synchronous read-only/version utility, never its process tree,
        # PostgreSQL or OpenMU. Service processes are never passed to this helper.
        if ($started -and !$process.HasExited) { $process.Kill(); $null=$process.WaitForExit(5000) }
        $process.Dispose()
    }
}

function Assert-MuDependencies($Setup) {
    $envMap=Get-MuEnvironment $Setup
    $envMap.LC_ALL='C'; $envMap.LANG='C'
    foreach ($key in @('postgres','pgCtl','pgControlData','psql')) {
        $version=Invoke-MuProbe (Resolve-MuFile $Setup.root $Setup[$key]) $Setup.root @('--version') $envMap
        if ($version -notmatch 'PostgreSQL\) 17\.11(?:\s|$)') { throw 'UNSAFE_CONFIG' }
    }
    $runtimes=Invoke-MuProbe (Resolve-MuFile $Setup.root $Setup.dotnet) $Setup.root @('--list-runtimes') $envMap
    foreach ($framework in @('Microsoft.NETCore.App','Microsoft.AspNetCore.App')) {
        if ($runtimes -notmatch ('(?m)^' + [regex]::Escape($framework) + ' 10\.0\.11 \[')) { throw 'UNSAFE_CONFIG' }
    }
    $control=Invoke-MuProbe (Resolve-MuFile $Setup.root $Setup.pgControlData) $Setup.root @(
        '-D',(Resolve-MuFile $Setup.root $Setup.pgData)) $envMap
    if ($control -notmatch '(?m)^Database system identifier:\s+([0-9]+)\s*$' -or
        $Matches[1] -cne $Setup.database.systemIdentifier) { throw 'UNSAFE_CONFIG' }
    if ($control -notmatch '(?m)^Database cluster state:\s+shut down\s*$') { throw 'OWNER_LOST' }
}

function Invoke-MuQuery($Setup, [string]$Sql, $Credential=$null, [switch]$PreserveSearchPath) {
    Assert-MuAreaHashes $Setup $Setup.pgDirectory
    Assert-MuFileHash (Resolve-MuFile $Setup.root $Setup.database.pgPassFile) $Setup.hashes[$Setup.database.pgPassFile]
    $child=Get-MuEnvironment $Setup
    $child.PGCONNECT_TIMEOUT='5'
    $child.PGOPTIONS='-c default_transaction_read_only=on -c statement_timeout=5000'
    if (!$PreserveSearchPath) { $child.PGOPTIONS+=' -c search_path=pg_catalog' }
    $user=$Setup.database.queryUser
    $child.PGPASSFILE=Resolve-MuFile $Setup.root $Setup.database.pgPassFile
    if ($null -ne $Credential) { $user=$Credential.user; $child.PGPASSWORD=$Credential.password }
    $text=Invoke-MuProbe (Resolve-MuFile $Setup.root $Setup.psql) $Setup.root @(
        '-X','-q','-t','-A','-w','-h','127.0.0.1','-p','5432','-U',$user,'-d',$Setup.database.name,
        '-v','ON_ERROR_STOP=1','-c',('BEGIN READ ONLY; ' + $Sql + '; COMMIT;')) $child
    try { return $text | ConvertFrom-Json -AsHashtable -Depth 20 } catch { throw 'PROBE_FAILED' }
}

function Get-MuRoleSql {
    # Reject effective DDL access, ownership, memberships and elevated roles. No
    # credentials or account records are selected. No SQL input comes from logs.
    return @'
SELECT json_build_object('user',current_user,'safe',
 NOT r.rolsuper AND NOT r.rolcreatedb AND NOT r.rolcreaterole AND NOT r.rolreplication AND NOT r.rolbypassrls
 AND NOT EXISTS(SELECT 1 FROM pg_auth_members WHERE member=r.oid)
 AND NOT has_database_privilege(current_database(),'CREATE')
 AND NOT EXISTS(SELECT 1 FROM pg_namespace n WHERE has_schema_privilege(n.oid,'CREATE'))
 AND NOT EXISTS(SELECT 1 FROM pg_class c WHERE c.relowner=r.oid)
 AND NOT EXISTS(SELECT 1 FROM pg_database d WHERE d.datdba=r.oid))
 FROM pg_roles r WHERE r.rolname=current_user
'@
}

function Get-MuSnapshotSql($Setup) {
    return @"
SELECT json_build_object(
 'database',current_database(), 'port',inet_server_port(), 'address',inet_server_addr()::text,
 'version',current_setting('server_version'),
 'systems',(SELECT json_agg(json_build_object('id',"Id"::text,'readConsoleInput',"ReadConsoleInput",'autoUpdateSchema',"AutoUpdateSchema")) FROM config."SystemConfiguration"),
 'configurationIds',(SELECT json_agg("Id"::text ORDER BY "Id") FROM config."GameConfiguration"),
 'game',(SELECT json_agg(json_build_object('port',"NetworkPort",'published',"AlternativePublishedPort") ORDER BY "NetworkPort") FROM config."GameServerEndpoint"),
 'chat',(SELECT json_agg(json_build_object('port',"NetworkPort") ORDER BY "NetworkPort") FROM config."ChatServerEndpoint"),
 'connect',(SELECT json_agg(json_build_object('port',"ClientListenerPort") ORDER BY "ClientListenerPort") FROM config."ConnectServerDefinition")
)
"@
}

function Assert-MuSnapshot($Setup, $Snapshot) {
    if ($Snapshot.database -cne $Setup.database.name -or $Snapshot.port -ne 5432 -or
        $Snapshot.address -cne '127.0.0.1' -or $Snapshot.version -notmatch '^17\.11(?:\s|$)') { throw 'UNSAFE_CONFIG' }
    $systems=@($Snapshot.systems)
    if ($systems.Count -ne 1 -or $systems[0].id -cne (Get-MuDatabaseSourceContract).systemConfigurationId -or
        $systems[0].readConsoleInput -isnot [bool] -or $systems[0].readConsoleInput -cne $true -or
        $systems[0].autoUpdateSchema -isnot [bool] -or $systems[0].autoUpdateSchema -cne $false) { throw 'UNSAFE_CONFIG' }
    Assert-MuExactStrings $Snapshot.configurationIds $Setup.database.configurationIds '^[a-f0-9]{8}(-[a-f0-9]{4}){3}-[a-f0-9]{12}$'
    $actual=@{game=$Snapshot.game;chat=$Snapshot.chat;connect=$Snapshot.connect}
    Assert-MuEndpointShape $actual
    foreach ($category in @('game','chat','connect')) {
        $expected=@($Setup.endpoints[$category] | ForEach-Object { if ($category -eq 'game') { '{0}:{1}' -f $_.port,$_.published } else { [string]$_.port } } | Sort-Object)
        $observed=@($actual[$category] | ForEach-Object { if ($category -eq 'game') { '{0}:{1}' -f $_.port,$_.published } else { [string]$_.port } } | Sort-Object)
        if (@(Compare-Object $expected $observed -CaseSensitive).Count) { throw 'UNSAFE_CONFIG' }
    }
}

function Get-MuHistorySql($Setup, [string]$Context) {
    Assert-MuDatabaseShape $Setup.database
    if ($Context -cnotin @('EntityDataContext','AdminAuth.AdminPanelContext')) { throw 'UNSAFE_CONFIG' }
    $schema=$Setup.database.migrationHistories[$Context].schema
    # Fixed table and independently pinned schema. Every function/catalog is qualified
    # because this probe preserves the runtime role/database's default search_path.
    $resolution=if ($Context -ceq 'EntityDataContext') {
        '(SELECT n.nspname FROM pg_catalog.pg_class c JOIN pg_catalog.pg_namespace n ON n.oid OPERATOR(pg_catalog.=) c.relnamespace WHERE c.oid OPERATOR(pg_catalog.=) pg_catalog.to_regclass(''"__EFMigrationsHistory"''))'
    } else { "'admin'" }
    return @"
SELECT pg_catalog.json_build_object(
 'context','$Context', 'schema','$schema', 'table','__EFMigrationsHistory',
 'resolvedSchema',$resolution,
 'migrations',(SELECT pg_catalog.json_agg(pg_catalog.json_build_object('id',"MigrationId",'productVersion',"ProductVersion") ORDER BY "MigrationId") FROM "$schema"."__EFMigrationsHistory")
)
"@
}

function Assert-MuHistory($Setup, [string]$Context, $History) {
    Assert-MuDatabaseShape $Setup.database
    if ($Context -cnotin @('EntityDataContext','AdminAuth.AdminPanelContext')) { throw 'UNSAFE_CONFIG' }
    Assert-MuKeys $History @('context','schema','table','resolvedSchema','migrations')
    $expected=$Setup.database.migrationHistories[$Context]
    if ($History.context -cne $Context -or $History.schema -cne $expected.schema -or
        $History.table -cne $expected.table -or $History.resolvedSchema -cne $expected.schema) { throw 'UNSAFE_CONFIG' }
    # EF reads both columns with GetString. Reading only MigrationId would miss
    # null/missing/incompatible ProductVersion or column-specific SELECT denial.
    if ($History.migrations -isnot [array] -or $History.migrations.Count -ne $expected.ids.Count) { throw 'UNSAFE_CONFIG' }
    foreach ($row in $History.migrations) {
        Assert-MuKeys $row @('id','productVersion')
        if ($row.id -isnot [string] -or $row.id -cnotmatch '^[0-9]{14}_[A-Za-z0-9_]+$' -or
            $row.productVersion -isnot [string] -or
            $row.productVersion -cnotmatch '^[0-9]+\.[0-9]+\.[0-9]+(?:[-+][A-Za-z0-9.+-]+)?$') { throw 'UNSAFE_CONFIG' }
    }
    Assert-MuExactStrings @($History.migrations | ForEach-Object { $_.id }) $expected.ids '^[0-9]{14}_[A-Za-z0-9_]+$'
}

function Assert-MuDatabase($Setup) {
    Assert-MuDatabaseShape $Setup.database
    $credentials=Get-MuConnections $Setup
    $snapshot=Invoke-MuQuery $Setup (Get-MuSnapshotSql $Setup)
    Assert-MuSnapshot $Setup $snapshot
    $probeRole=Invoke-MuQuery $Setup (Get-MuRoleSql)
    if ($probeRole.user -cne $Setup.database.queryUser -or $probeRole.safe -cne $true) { throw 'UNSAFE_CONFIG' }
    foreach ($credential in $credentials.Values) {
        $role=Invoke-MuQuery $Setup (Get-MuRoleSql) $credential
        if ($role.user -cne $credential.user -or $role.safe -cne $true) { throw 'UNSAFE_CONFIG' }
    }
    foreach ($context in @('EntityDataContext','AdminAuth.AdminPanelContext')) {
        $sql=Get-MuHistorySql $Setup $context
        Assert-MuHistory $Setup $context (Invoke-MuQuery $Setup $sql -PreserveSearchPath)
        # Verify each actual context credential independently. Never use only the
        # probe or EntityDataContext credential as proof for AdminPanelContext.
        Assert-MuHistory $Setup $context (Invoke-MuQuery $Setup $sql $credentials[$context] -PreserveSearchPath)
    }
    Assert-MuSnapshot $Setup (Invoke-MuQuery $Setup (Get-MuSnapshotSql $Setup) $credentials.EntityDataContext)
}
