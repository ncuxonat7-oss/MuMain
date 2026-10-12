# One-time DB preparation only. Imported by SetupMU.ps1 and mock-only tests.
# No action happens on import. Preparation is not setup-application or launch approval.
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'

function Get-MuFirstSetupPolicy {
    $path=Join-Path $PSScriptRoot 'first-setup-policy.json'
    Assert-MuLocalPath $path
    Assert-MuFileHash $path '15023e44c5997321245fd6e1851ec16671b6934b3eb6e8292c53025c90ac79cf'
    return Read-MuJson $path
}

function Assert-MuSetupRequest($Request) {
    Assert-MuKeys $Request @('packageRoot','setupRelative','archive','credentialBundle','confirmNewDatabase','confirmCredentialHandling','applyReviewedFlags')
    foreach ($key in @('confirmNewDatabase','confirmCredentialHandling','applyReviewedFlags')) {
        if ($Request[$key] -isnot [bool] -or !$Request[$key]) { throw 'SETUP_APPROVAL_REQUIRED' }
    }
    foreach ($key in @('packageRoot','archive','credentialBundle')) {
        if ($Request[$key] -isnot [string] -or ![IO.Path]::IsPathFullyQualified($Request[$key])) { throw 'UNSAFE_CONFIG' }
    }
    if ($Request.setupRelative -isnot [string] -or $Request.setupRelative -cnotmatch '^database/setup-[a-z0-9][a-z0-9-]{0,47}$') { throw 'UNSAFE_CONFIG' }
}

function Get-MuDisposableProfile {
    $path=Resolve-MuFile $PSScriptRoot 'disposable-role-profile.json'
    Assert-MuFileHash $path '5e186c3e242b677c5d2ce37032bd3316a0bf0e30312ca252ba23b1770c57c7a6'
    return Read-MuJson $path
}

function Assert-MuSetupGrantPolicy($Policy) {
    if ($Policy -isnot [Collections.IDictionary] -or $Policy.runtimeGrantStatus -cne 'DISPOSABLE_PROFILE_PREPARED' -or
        $Policy.profileSha256 -cne '5e186c3e242b677c5d2ce37032bd3316a0bf0e30312ca252ba23b1770c57c7a6') { throw 'RUNTIME_GRANTS_UNRESOLVED' }
    if ($Policy.runtimeSourceStatus -cne 'REVIEWED' -or $Policy.runtimeBinaryAlignment -isnot [bool] -or !$Policy.runtimeBinaryAlignment -or
        $Policy.liveValidationStatus -cne 'NOT_RUN') { throw 'SOURCE_BINARY_VALIDATION_REQUIRED' }
    if ($Policy.launchEnabled -isnot [bool] -or $Policy.launchEnabled -or $null -ne $Policy.approvedLaunchManifestSha256 -or
        $Policy.database -cne 'openmu' -or $Policy.listenAddress -cne '127.0.0.1' -or $Policy.port -ne 5432) { throw 'UNSAFE_CONFIG' }
    $null=Get-MuDisposableProfile
}

function Assert-MuSetupApplication($State) {
    Assert-MuSetupGrantPolicy $State.policy
    # This null pin is deliberately NOT filled by implementation/test approval.
    if ($State.policy.setupApplicationApprovalSha256 -cnotmatch '^[a-f0-9]{64}$') { throw 'SETUP_APPLICATION_APPROVAL_REQUIRED' }
    $path=Resolve-MuFile $State.request.packageRoot 'setup-application-approval.json'
    Assert-MuFileHash $path $State.policy.setupApplicationApprovalSha256
    $approval=Read-MuJson $path
    Assert-MuKeys $approval @('schema','scope','packageRoot','setupRelative','profileSha256','credentialBundleSha256','adminSchemaMode','launchEnabled','approvedLaunchManifestSha256')
    if ($approval.schema -ne 1 -or $approval.scope -cne 'NEW_DISPOSABLE_LOCAL_ALPHA_SETUP' -or
        $approval.packageRoot -cne [IO.Path]::GetFullPath($State.request.packageRoot) -or
        $approval.setupRelative -cne $State.request.setupRelative -or $approval.profileSha256 -cne $State.policy.profileSha256 -or
        $approval.adminSchemaMode -cne 'ExternallyProvisioned' -or $approval.launchEnabled -isnot [bool] -or
        $approval.launchEnabled -or $null -ne $approval.approvedLaunchManifestSha256) { throw 'SETUP_APPLICATION_APPROVAL_REQUIRED' }
    Assert-MuLocalPath $State.request.credentialBundle
    Assert-MuFileHash $State.request.credentialBundle $approval.credentialBundleSha256
}

function Assert-MuSetupCredentialValues($Values) {
    if ($null -eq $Values) { throw 'CREDENTIALS_REQUIRED' }
    Assert-MuKeys $Values @('mu_setup','mu_entity','mu_typed','mu_admin','mu_account','mu_config','mu_friend','mu_guild','mu_probe')
    foreach ($name in $Values.Keys) {
        if ($Values[$name] -isnot [string] -or $Values[$name] -cnotmatch '^[A-Za-z0-9_-]{32,128}$') { throw 'INVALID_PRIVATE_INPUT' }
    }
}

function Assert-MuSetupCredentialInput($State) {
    if (!(Test-Path -LiteralPath $State.request.credentialBundle -PathType Leaf)) { throw 'CREDENTIALS_REQUIRED' }
    Assert-MuLocalPath $State.request.credentialBundle
    Assert-MuPrivateFile $State.request.credentialBundle
    Assert-MuSetupCredentialValues (Read-MuJson $State.request.credentialBundle)
}

function Write-MuNewPrivateText([string]$Path,[string]$Text) {
    Assert-MuLocalPath (Split-Path $Path)
    $stream=[IO.File]::Open($Path,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None)
    try { $bytes=[Text.UTF8Encoding]::new($false).GetBytes($Text);$stream.Write($bytes,0,$bytes.Length) }
    finally { $stream.Dispose() }
}

function Write-MuSetupEvent($State,[string]$Stage,[string]$Result) {
    if ($Stage -cnotmatch '^[a-z-]{1,40}$' -or $Result -cnotin @('begin','ok','failed','retained')) { throw 'UNSAFE_CONFIG' }
    $State.events+=@{stage=$Stage;result=$Result;utc=[DateTime]::UtcNow.ToString('o')}
    if ($State.events.Count -gt 64) { throw 'SETUP_JOURNAL_LIMIT' }
    if ($State.journalReady) {
        # Only a fixed vocabulary, never exception text, SQL, process output or secrets.
        $State.events | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $State.directory 'setup-journal.json') -Encoding utf8
    }
}

function Assert-MuSetupHostAndInputs($State) {
    $r=$State.request; $p=$State.policy
    if (!$IsWindows -or [Environment]::OSVersion.Version.Build -lt 22000 -or
        [Runtime.InteropServices.RuntimeInformation]::OSArchitecture -ne 'X64') { throw 'WINDOWS_REQUIRED' }
    Assert-MuLocalPath $r.packageRoot
    $State.directory=Join-Path $r.packageRoot $r.setupRelative
    if (Test-Path -LiteralPath $State.directory) { throw 'SETUP_DESTINATION_EXISTS' }
    $parent=Split-Path $State.directory
    if (Test-Path -LiteralPath $parent) { Assert-MuLocalPath $parent }
    $inventoryPath=Resolve-MuFile $r.packageRoot 'package-inventory.json'
    $State.inventory=(Assert-MuPackageContract $r.packageRoot).inventory
    foreach ($relative in $State.inventory.Keys) {
        Assert-MuFileHash (Resolve-MuFile $r.packageRoot $relative) $State.inventory[$relative].sha256
    }
    $contract=Read-MuJson (Resolve-MuFile $r.packageRoot 'scripts/windows11/local-session-contract.json')
    if ($contract.launchEnabled -isnot [bool] -or $contract.launchEnabled -ne $false -or $null -ne $contract.approvedLaunchManifestSha256) { throw 'UNSAFE_CONFIG' }
    Assert-MuLocalPath $r.archive
    Assert-MuFileHash $r.archive $p.archiveSha256
    if ((Get-Item -LiteralPath $r.archive).Length -ne $p.archiveBytes) { throw 'HASH_MISMATCH' }
    Assert-MuLocalPath $r.credentialBundle
    Assert-MuPrivateFile $r.credentialBundle
    $listeners=@(Get-NetTCPConnection -State Listen -ErrorAction Stop)
    if (@($listeners | Where-Object LocalPort -eq 5432).Count) { throw 'PORT_BUSY' }
    $State.pgData=Join-Path $State.directory 'cluster'
    $State.pgBin=Resolve-MuFile $r.packageRoot 'postgres/bin'
}

function Set-MuSetupPrivateDirectory([string]$Path) {
    # Real use requires the owner's separate Windows ACL/credential handoff approval.
    $acl=[Security.AccessControl.DirectorySecurity]::new()
    $sid=[Security.Principal.WindowsIdentity]::GetCurrent().User
    $acl.SetOwner($sid); $acl.SetAccessRuleProtection($true,$false)
    foreach ($id in @($sid.Value,'S-1-5-18','S-1-5-32-544')) {
        $rule=[Security.AccessControl.FileSystemAccessRule]::new([Security.Principal.SecurityIdentifier]::new($id),
            'FullControl','ContainerInherit, ObjectInherit','None','Allow')
        $acl.AddAccessRule($rule)
    }
    Set-Acl -LiteralPath $Path -AclObject $acl
    Assert-MuPrivateFile $Path
}

function Initialize-MuSetupPrivateArea($State) {
    # Atomic directory claim via a sibling lock file: never adopt an existing setup.
    $parent=Split-Path $State.directory
    if (!(Test-Path -LiteralPath $parent)) { $null=New-Item -ItemType Directory -Path $parent }
    Assert-MuLocalPath $parent
    $claim=$State.directory + '.claim'
    $State.claim=[IO.File]::Open($claim,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None)
    if (Test-Path -LiteralPath $State.directory) { throw 'SETUP_DESTINATION_EXISTS' }
    $null=New-Item -ItemType Directory -Path $State.directory
    Set-MuSetupPrivateDirectory $State.directory
    $State.journalReady=$true
}

function Read-MuSetupCredentials($State) {
    # Owner-provided private input only. Never generate, request through chat or log it.
    $values=Read-MuJson $State.request.credentialBundle
    Assert-MuSetupCredentialInput $State
    Assert-MuSetupCredentialValues $values
    $State.credentials=$values
    $State.bootstrapPassword=Join-Path $State.directory 'bootstrap.pw'
    $State.bootstrapPass=Join-Path $State.directory 'bootstrap.pgpass'
    Write-MuNewPrivateText $State.bootstrapPassword ($values.mu_setup + "`n")
    Write-MuNewPrivateText $State.bootstrapPass ('127.0.0.1:5432:*:mu_setup:' + $values.mu_setup + "`n")
    foreach ($path in @($State.bootstrapPassword,$State.bootstrapPass)) { Assert-MuPrivateFile $path }
}

function Expand-MuSetupDump($State) {
    $archive=[IO.Compression.ZipFile]::OpenRead($State.request.archive)
    try {
        $entries=@($archive.Entries | Where-Object FullName -ceq 'gameplay-test-db.dump')
        if ($entries.Count -ne 1 -or $entries[0].Length -ne $State.policy.dumpBytes) { throw 'HASH_MISMATCH' }
        $State.dump=Join-Path $State.directory 'baseline.dump'
        $input=$entries[0].Open(); $output=[IO.File]::Open($State.dump,[IO.FileMode]::CreateNew)
        try { $input.CopyTo($output) } finally { $input.Dispose(); $output.Dispose() }
        Assert-MuFileHash $State.dump $State.policy.dumpSha256
    } finally { $archive.Dispose() }
}

function Invoke-MuSetupUtility($State,[ValidateSet('initdb','pg_ctl','pg_controldata','psql','pg_restore')][string]$Tool,
    [string[]]$Arguments,[string]$InputSql='',[int]$Seconds=30,[switch]$DaemonStart) {
    if ($Seconds -lt 1 -or $Seconds -gt 180) { throw 'UNSAFE_CONFIG' }
    $info=[Diagnostics.ProcessStartInfo]::new()
    $info.FileName=Join-Path $State.pgBin ($Tool + '.exe'); $info.WorkingDirectory=$State.directory
    $info.UseShellExecute=$false; $info.Environment.Clear()
    foreach ($key in @('SystemRoot','WINDIR','TEMP','TMP')) { $info.Environment[$key]=[Environment]::GetEnvironmentVariable($key) }
    $info.Environment['LC_ALL']='C';$info.Environment['LANG']='C';$info.Environment['PGCONNECT_TIMEOUT']='5'
    $info.Environment['PGPASSFILE']=$State.bootstrapPass
    $info.RedirectStandardInput=$true
    $info.RedirectStandardOutput=!$DaemonStart; $info.RedirectStandardError=!$DaemonStart
    foreach ($argument in $Arguments) { $info.ArgumentList.Add($argument) }
    $process=[Diagnostics.Process]::new();$process.StartInfo=$info;$started=$false
    try {
        if (!$process.Start()) { throw 'SETUP_UTILITY_FAILED' };$started=$true
        if ($InputSql) { $process.StandardInput.Write($InputSql) }
        $process.StandardInput.Close()
        if (!$DaemonStart) { $out=$process.StandardOutput.ReadToEndAsync();$err=$process.StandardError.BaseStream.CopyToAsync([IO.Stream]::Null) }
        if (!$process.WaitForExit($Seconds*1000)) { throw 'SETUP_UTILITY_TIMEOUT' }
        if ($process.ExitCode -ne 0) { throw 'SETUP_UTILITY_FAILED' }
        if (!$DaemonStart) {
            if (!$out.Wait(5000) -or !$err.Wait(5000) -or $out.Result.Length -gt 1MB) { throw 'SETUP_UTILITY_FAILED' }
            return $out.Result.Trim()
        }
    } finally {
        # A utility only; never a PostgreSQL/server process tree. Unknown postmaster
        # state is retained if ownership cannot be established.
        if ($started -and !$process.HasExited) { $process.Kill();$null=$process.WaitForExit(5000) }
        $process.Dispose()
    }
}

function Invoke-MuSetupSql($State,[string]$Sql,[string]$Database='openmu') {
    if ($Database -cnotin @('postgres','openmu')) { throw 'UNSAFE_CONFIG' }
    return Invoke-MuSetupUtility $State 'psql' @('-X','-q','-t','-A','-w','-h','127.0.0.1','-p','5432','-U','mu_setup','-d',$Database,'-v','ON_ERROR_STOP=1','-f','-') $Sql 60
}

function Initialize-MuSetupCluster($State) {
    # Baseline custom-dump metadata explicitly says SQL_ASCII, libc locale C.
    # Preserve it; UTF8 conversion would be a separate migration decision.
    $null=Invoke-MuSetupUtility $State 'initdb' @('-D',$State.pgData,'-U','mu_setup','--auth-local=scram-sha-256',
        '--auth-host=scram-sha-256','--encoding=SQL_ASCII','--locale=C','--pwfile',$State.bootstrapPassword) '' 120
    @("listen_addresses = '127.0.0.1'","port = 5432","password_encryption = 'scram-sha-256'",
      "log_statement = 'none'","log_min_error_statement = 'panic'") | Set-Content -LiteralPath (Join-Path $State.pgData 'postgresql.conf') -Encoding utf8
    'host all mu_setup 127.0.0.1/32 scram-sha-256' | Set-Content -LiteralPath (Join-Path $State.pgData 'pg_hba.conf') -Encoding utf8
    '' | Set-Content -LiteralPath (Join-Path $State.pgData 'pg_ident.conf') -Encoding utf8
}

function Assert-MuSetupPgOwner($State) {
    $lines=@(Get-Content -LiteralPath (Join-Path $State.pgData 'postmaster.pid'))
    if ($lines.Count -lt 2 -or [IO.Path]::GetFullPath($lines[1]) -ine [IO.Path]::GetFullPath($State.pgData)) { throw 'OWNER_LOST' }
    $process=Get-Process -Id ([int]$lines[0]) -ErrorAction Stop
    try {
        $path=Join-Path $State.pgBin 'postgres.exe'
        if ($process.MainModule.FileName -ine $path) { throw 'OWNER_LOST' }
        $identity=@{pid=$process.Id;ticks=$process.StartTime.ToUniversalTime().Ticks;path=$path}
        if ($null -ne $State.pgOwner -and ($identity.pid -ne $State.pgOwner.pid -or $identity.ticks -ne $State.pgOwner.ticks)) { throw 'OWNER_LOST' }
        $listeners=@(Get-NetTCPConnection -State Listen -ErrorAction Stop | Where-Object LocalPort -eq 5432)
        if (!$listeners.Count -or @($listeners | Where-Object { $_.OwningProcess -ne $identity.pid -or $_.LocalAddress -cne '127.0.0.1' }).Count) { throw 'OWNER_LOST' }
        $State.pgOwner=$identity
    } finally { $process.Dispose() }
}

function Start-MuSetupCluster($State) {
    # Repeat conflict check immediately before start; never stop another listener.
    if (@(Get-NetTCPConnection -State Listen -ErrorAction Stop | Where-Object LocalPort -eq 5432).Count) { throw 'PORT_BUSY' }
    $State.pgStartAttempted=$true
    $null=Invoke-MuSetupUtility $State 'pg_ctl' @('-D',$State.pgData,'-l',(Join-Path $State.directory 'postgres-private.log'),'-w','-t','45','start') '' 60 -DaemonStart
    Assert-MuSetupPgOwner $State
    $control=Invoke-MuSetupUtility $State 'pg_controldata' @('-D',$State.pgData) '' 15
    if ($control -notmatch '(?m)^Database system identifier:\s+([0-9]+)\s*$') { throw 'PROBE_FAILED' }
    $State.systemIdentifier=$Matches[1]
}

function New-MuSetupRolesAndDatabase($State) {
    $sql="CREATE ROLE mu_owner NOLOGIN NOINHERIT NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS;`n"
    foreach ($name in @('mu_entity','mu_typed','mu_admin','mu_account','mu_config','mu_friend','mu_guild','mu_probe')) {
        $sql+="CREATE ROLE $name LOGIN NOINHERIT NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS PASSWORD '$($State.credentials[$name])';`n"
    }
    $sql+="CREATE DATABASE openmu OWNER mu_owner TEMPLATE template0 ENCODING 'SQL_ASCII' LC_COLLATE 'C' LC_CTYPE 'C';`n"
    # Only the newly created private cluster; remove inherited cross-DB access.
    $sql+="REVOKE CONNECT,TEMPORARY ON DATABASE postgres,template1 FROM PUBLIC;`n"
    $null=Invoke-MuSetupSql $State $sql 'postgres'
}

function Restore-MuSetupSnapshot($State) {
    Assert-MuSetupPgOwner $State
    $null=Invoke-MuSetupUtility $State 'pg_restore' @('--exit-on-error','--single-transaction','--no-owner','--no-acl',
        '--role=mu_owner','-w','-h','127.0.0.1','-p','5432','-U','mu_setup','-d','openmu',$State.dump) '' 180
}

function Get-MuSetupKnownGrantsSql {
    $profile=Get-MuDisposableProfile
    $lines=[Collections.Generic.List[string]]::new()
    $lines.Add('REVOKE ALL ON DATABASE openmu FROM PUBLIC;')
    $lines.Add('REVOKE CREATE ON SCHEMA public FROM PUBLIC;')
    foreach ($role in @($profile.roles.Keys | Sort-Object)) {
        $lines.Add("GRANT CONNECT ON DATABASE openmu TO $role;")
        foreach ($schema in $profile.roles[$role].schemaUsage) { $lines.Add("GRANT USAGE ON SCHEMA $schema TO $role;") }
        foreach ($entry in $profile.roles[$role].tables) {
            $schema,$table=$entry.table.Split('.')
            $operations=$entry.operations -join ','
            $lines.Add(('GRANT {0} ON {1}."{2}" TO {3};' -f $operations,$schema,$table,$role))
        }
    }
    # Keep the existing non-runtime, column-limited acceptance probe separate.
    $lines.Add(@'
GRANT CONNECT ON DATABASE openmu TO mu_probe;
GRANT USAGE ON SCHEMA public,admin,config TO mu_probe;
GRANT SELECT ON public."__EFMigrationsHistory",admin."__EFMigrationsHistory" TO mu_probe;
GRANT SELECT ("Id","ReadConsoleInput","AutoUpdateSchema") ON config."SystemConfiguration" TO mu_probe;
GRANT SELECT ("Id") ON config."GameConfiguration" TO mu_probe;
GRANT SELECT ("NetworkPort","AlternativePublishedPort") ON config."GameServerEndpoint" TO mu_probe;
GRANT SELECT ("NetworkPort") ON config."ChatServerEndpoint" TO mu_probe;
GRANT SELECT ("ClientListenerPort") ON config."ConnectServerDefinition" TO mu_probe;
'@)
    return $lines -join "`n"
}

function Assert-MuPreparedGrantIdentity($State,$Identity) {
    Assert-MuKeys $Identity @('user','database','dataDirectory','listenAddress','port','systemIdentifier','histories')
    if ($null -eq $State.pgOwner -or $State.systemIdentifier -cnotmatch '^[0-9]{10,20}$' -or
        $Identity.user -cne 'mu_setup' -or $Identity.database -cne 'openmu' -or
        [IO.Path]::GetFullPath($Identity.dataDirectory) -cne [IO.Path]::GetFullPath($State.pgData) -or
        $Identity.listenAddress -cne '127.0.0.1' -or $Identity.port -cne '5432' -or
        $Identity.systemIdentifier -cne $State.systemIdentifier) { throw 'PREPARED_DATABASE_IDENTITY_REQUIRED' }
    $contract=Get-MuDatabaseSourceContract
    Assert-MuKeys $Identity.histories @('EntityDataContext','AdminAuth.AdminPanelContext')
    foreach ($context in $contract.migrationHistories.Keys) {
        Assert-MuExactStrings $Identity.histories[$context] $contract.migrationHistories[$context].ids '^[0-9]{14}_[A-Za-z0-9_]+$'
    }
}

function Set-MuSetupRuntimeGrants($State) {
    Assert-MuSetupApplication $State
    Assert-MuSetupCredentialValues $State.credentials
    Assert-MuSetupPgOwner $State
    # Read identities/history only. Missing admin storage must be provisioned by
    # the separate approved admin setup mechanism, never Migrate/fallback here.
    $query=@'
BEGIN READ ONLY;
SELECT json_build_object('user',current_user,'database',current_database(),'dataDirectory',current_setting('data_directory'),
 'listenAddress',current_setting('listen_addresses'),'port',current_setting('port'),
 'systemIdentifier',(SELECT system_identifier::text FROM pg_control_system()),
 'histories',json_build_object('EntityDataContext',(SELECT json_agg("MigrationId" ORDER BY "MigrationId") FROM public."__EFMigrationsHistory"),
 'AdminAuth.AdminPanelContext',(SELECT json_agg("MigrationId" ORDER BY "MigrationId") FROM admin."__EFMigrationsHistory")));
ROLLBACK;
'@
    $identity=(Invoke-MuSetupSql $State $query) | ConvertFrom-Json -AsHashtable
    Assert-MuPreparedGrantIdentity $State $identity
    $directory=$State.pgData.Replace("'","''")
    $system=$State.systemIdentifier
    $guard=@"
DO `$mu`$ BEGIN
 IF current_user <> 'mu_setup' OR current_database() <> 'openmu' OR current_setting('data_directory') <> '$directory'
 OR current_setting('listen_addresses') <> '127.0.0.1' OR current_setting('port') <> '5432'
 OR (SELECT system_identifier::text FROM pg_control_system()) <> '$system' THEN RAISE EXCEPTION 'PREPARED_DATABASE_IDENTITY_REQUIRED'; END IF;
 IF EXISTS(SELECT FROM pg_roles WHERE rolname IN ('mu_entity','mu_typed','mu_admin','mu_account','mu_config','mu_friend','mu_guild','mu_probe')
 AND (rolsuper OR rolcreatedb OR rolcreaterole OR rolreplication OR rolbypassrls OR rolinherit)) THEN RAISE EXCEPTION 'UNSAFE_RUNTIME_ROLE'; END IF;
 IF EXISTS(SELECT FROM pg_auth_members m JOIN pg_roles r ON r.oid=m.member OR r.oid=m.roleid WHERE r.rolname LIKE 'mu_%') THEN RAISE EXCEPTION 'UNSAFE_ROLE_MEMBERSHIP'; END IF;
 IF EXISTS(SELECT FROM pg_class c JOIN pg_roles r ON r.oid=c.relowner WHERE r.rolname IN ('mu_entity','mu_typed','mu_admin','mu_account','mu_config','mu_friend','mu_guild','mu_probe'))
 OR EXISTS(SELECT FROM pg_namespace n JOIN pg_roles r ON r.oid=n.nspowner WHERE r.rolname IN ('mu_entity','mu_typed','mu_admin','mu_account','mu_config','mu_friend','mu_guild','mu_probe'))
 OR EXISTS(SELECT FROM pg_database d JOIN pg_roles r ON r.oid=d.datdba WHERE r.rolname IN ('mu_entity','mu_typed','mu_admin','mu_account','mu_config','mu_friend','mu_guild','mu_probe')) THEN RAISE EXCEPTION 'UNSAFE_RUNTIME_OWNERSHIP'; END IF;
END `$mu`$;
"@
    $null=Invoke-MuSetupSql $State ("BEGIN;`n"+$guard+(Get-MuSetupKnownGrantsSql)+"`nCOMMIT;")
}

function Get-MuSetupFlagsSql {
    return @'
BEGIN;
SET LOCAL statement_timeout='5s';
SET LOCAL lock_timeout='5s';
LOCK TABLE config."SystemConfiguration" IN EXCLUSIVE MODE;
DO $mu$
DECLARE before_other jsonb; after_other jsonb; changed integer;
BEGIN
 IF (SELECT count(*) FROM config."SystemConfiguration") <> 1 THEN RAISE EXCEPTION 'SETUP_FLAG_SHAPE'; END IF;
 SELECT to_jsonb(s)-'ReadConsoleInput'-'AutoUpdateSchema' INTO before_other FROM config."SystemConfiguration" s
 WHERE s."Id"='00000010-0000-0000-0000-000000000000' AND s."ReadConsoleInput"=false AND s."AutoUpdateSchema"=true;
 IF before_other IS NULL THEN RAISE EXCEPTION 'SETUP_FLAG_BEFORE'; END IF;
 UPDATE config."SystemConfiguration" SET "ReadConsoleInput"=true,"AutoUpdateSchema"=false
 WHERE "Id"='00000010-0000-0000-0000-000000000000' AND "ReadConsoleInput"=false AND "AutoUpdateSchema"=true;
 GET DIAGNOSTICS changed=ROW_COUNT;
 SELECT to_jsonb(s)-'ReadConsoleInput'-'AutoUpdateSchema' INTO after_other FROM config."SystemConfiguration" s;
 IF changed<>1 OR before_other IS DISTINCT FROM after_other THEN RAISE EXCEPTION 'SETUP_FLAG_UNEXPECTED_CHANGE'; END IF;
 IF (SELECT count(*) FROM config."SystemConfiguration") <> 1 OR NOT EXISTS(
   SELECT 1 FROM config."SystemConfiguration" WHERE "Id"='00000010-0000-0000-0000-000000000000'
     AND "ReadConsoleInput"=true AND "AutoUpdateSchema"=false) THEN RAISE EXCEPTION 'SETUP_FLAG_AFTER'; END IF;
END $mu$;
COMMIT;
'@
}

function Set-MuSetupReviewedFlags($State) {
    if (!$State.request.applyReviewedFlags) { throw 'SETUP_APPROVAL_REQUIRED' }
    $null=Invoke-MuSetupSql $State (Get-MuSetupFlagsSql)
}

function Prepare-MuSetupAcceptance($State) {
    Assert-MuSetupGrantPolicy $State.policy
    $contract=Get-MuDatabaseSourceContract
    $mapping=@{EntityDataContext='mu_entity';'AdminAuth.AdminPanelContext'='mu_admin';TypedContext='mu_typed';
        ConfigurationContext='mu_config';AccountContext='mu_account';TradeContext='mu_account';FriendContext='mu_friend';GuildContext='mu_guild'}
    $relative=$State.request.setupRelative + '/prepared-server'
    $directory=Join-Path $State.request.packageRoot $relative
    if (Test-Path -LiteralPath $directory) { throw 'SETUP_DESTINATION_EXISTS' }
    $null=New-Item -ItemType Directory -Path $directory
    $xml=[Xml.XmlDocument]::new();$ns='http://www.munique.net/ConnectionSettings'
    $root=$xml.CreateElement('ConnectionSettings',$ns);$null=$xml.AppendChild($root)
    $connections=$xml.CreateElement('Connections',$ns);$null=$root.AppendChild($connections)
    foreach ($context in @('EntityDataContext','AdminAuth.AdminPanelContext','TypedContext','ConfigurationContext','AccountContext','TradeContext','FriendContext','GuildContext')) {
        $connection=$xml.CreateElement('Connection',$ns);$null=$connections.AppendChild($connection)
        $role=$mapping[$context]
        $values=@{ContextTypeName=('MUnique.OpenMU.Persistence.EntityFramework.'+$context);DatabaseEngine='Npgsql';
            ConnectionString=("Server=127.0.0.1;Port=5432;Database=openmu;User Id=$role;Password=$($State.credentials[$role]);Command Timeout=120;")}
        $names=@('ContextTypeName','ConnectionString','DatabaseEngine')
        if ($context -ceq 'AdminAuth.AdminPanelContext') { $values.AdminSchemaManagement='ExternallyProvisioned';$names+=@('AdminSchemaManagement') }
        foreach ($name in $names) {
            $element=$xml.CreateElement($name,$ns);$element.InnerText=$values[$name];$null=$connection.AppendChild($element)
        }
    }
    $config=Join-Path $directory 'ConnectionSettings.xml';Write-MuNewPrivateText $config $xml.OuterXml;Assert-MuPrivateFile $config
    $passRelative=$State.request.setupRelative + '/probe.pgpass'
    $pass=Join-Path $State.request.packageRoot $passRelative
    Write-MuNewPrivateText $pass ('127.0.0.1:5432:openmu:mu_probe:' + $State.credentials.mu_probe + "`n")
    Assert-MuPrivateFile $pass
    $roles=@($mapping.Values | Sort-Object -Unique)
    $hba=@('host all mu_setup 127.0.0.1/32 scram-sha-256') + @(@($roles)+@('mu_probe') | ForEach-Object { "host openmu $_ 127.0.0.1/32 scram-sha-256" })
    $hba | Set-Content -LiteralPath (Join-Path $State.pgData 'pg_hba.conf') -Encoding utf8
    $null=Invoke-MuSetupSql $State 'SELECT pg_catalog.pg_reload_conf();'
    $control=Invoke-MuSetupUtility $State 'pg_controldata' @('-D',$State.pgData) '' 15
    if ($control -notmatch '(?m)^Database system identifier:\s+([0-9]+)\s*$') { throw 'PROBE_FAILED' }
    $systemIdentifier=$Matches[1]
    $hashes=@{};foreach ($key in $State.inventory.Keys) { $hashes[$key]=$State.inventory[$key].sha256 }
    $hashes[$relative + '/ConnectionSettings.xml']=(Get-FileHash -LiteralPath $config -Algorithm SHA256).Hash.ToLowerInvariant()
    $hashes[$passRelative]=(Get-FileHash -LiteralPath $pass -Algorithm SHA256).Hash.ToLowerInvariant()
    $State.acceptanceSetup=@{root=$State.request.packageRoot;server=$relative;pgDirectory='postgres';psql='postgres/bin/psql.exe';
        hashes=$hashes;endpoints=$contract.endpoints;database=@{name='openmu';queryUser='mu_probe';pgPassFile=$passRelative;
        systemIdentifier=$systemIdentifier;runtimeRoles=$roles;migrationHistories=$contract.migrationHistories;configurationIds=$contract.configurationIds}}
}

function Seal-MuSetupPrivateOutput($State) {
    # Preserve packaged ConnectionSettings.xml. Staged private config must be
    # separately reviewed/promoted; this procedure never writes an approved manifest.
    $roles=@($State.acceptanceSetup.database.runtimeRoles)+@('mu_probe')
    @($roles | ForEach-Object { "host openmu $_ 127.0.0.1/32 scram-sha-256" }) |
        Set-Content -LiteralPath (Join-Path $State.pgData 'pg_hba.conf') -Encoding utf8
    @("listen_addresses = '127.0.0.1'","port = 5432","password_encryption = 'scram-sha-256'",
      "log_statement = 'none'","log_min_error_statement = 'panic'") |
        Set-Content -LiteralPath (Join-Path $State.pgData 'postgresql.conf') -Encoding utf8
    # This file contains no credentials. Private config itself stays ACL-restricted.
    @{schema=2;status='DB_PREPARED_CONFIG_STAGED_REVIEW_REQUIRED';launchEnabled=$false;approvedLaunchManifestSha256=$null;
        pgData=($State.request.setupRelative+'/cluster');database=$State.acceptanceSetup.database;
        endpoints=$State.acceptanceSetup.endpoints;runtimeConfigPromotion='NOT_PERFORMED'} |
        ConvertTo-Json -Depth 20 | Set-Content -LiteralPath (Join-Path $State.directory 'setup-result.draft.json') -Encoding utf8
}

function Test-MuSetupReadOnlyAcceptance($State) {
    if ($null -eq $State.acceptanceSetup) { throw 'SETUP_NOT_PREPARED' }
    Assert-MuSetupPgOwner $State
    Assert-MuDatabase $State.acceptanceSetup
}

function Stop-MuSetupCluster($State) {
    if ($null -eq $State.pgOwner) { throw 'OWNER_LOST' }
    Assert-MuSetupPgOwner $State
    $null=Invoke-MuSetupUtility $State 'pg_ctl' @('-D',$State.pgData,'-m','fast','-w','-t','30','stop') '' 45
    if (Test-Path -LiteralPath (Join-Path $State.pgData 'postmaster.pid')) { throw 'STOP_FAILED' }
    $State.pgOwner=$null;$State.pgStopped=$true
}

function Invoke-MuFirstSetup($Request) {
    $state=@{request=$Request;policy=$null;directory=$null;events=@();journalReady=$false;claim=$null;credentials=$null;
        inventory=$null;systemIdentifier=$null;pgOwner=$null;pgStartAttempted=$false;pgStopped=$false;acceptanceSetup=$null;status='NOT_STARTED';stage='request'}
    try {
        Assert-MuSetupRequest $Request
        $state.stage='package-integrity';$null=Assert-MuPackageContract $Request.packageRoot
        $state.policy=Get-MuFirstSetupPolicy
        $state.stage='application-approval';Assert-MuSetupApplication $state
        $state.stage='credentials-required';Assert-MuSetupCredentialInput $state
        # Must stop before filesystem claims, credentials or cluster creation.
        $state.stage='runtime-grants';Assert-MuSetupGrantPolicy $state.policy
        foreach ($stage in @('preflight','private-area','credentials','dump','initialize','start','roles','restore','admin-provision','grants','flags','prepare-acceptance','acceptance','seal','stop')) {
            $state.stage=$stage;Write-MuSetupEvent $state $stage 'begin'
            switch ($stage) {
                'preflight' { Assert-MuSetupHostAndInputs $state }
                'private-area' { Initialize-MuSetupPrivateArea $state }
                'credentials' { Read-MuSetupCredentials $state }
                'dump' { Expand-MuSetupDump $state }
                'initialize' { Initialize-MuSetupCluster $state }
                'start' { Start-MuSetupCluster $state }
                'roles' { New-MuSetupRolesAndDatabase $state }
                'restore' { Restore-MuSetupSnapshot $state }
                'admin-provision' { Invoke-MuSetupAdminProvisioning $state }
                'grants' { Set-MuSetupRuntimeGrants $state }
                'flags' { Set-MuSetupReviewedFlags $state }
                'prepare-acceptance' { Prepare-MuSetupAcceptance $state }
                'acceptance' { Test-MuSetupReadOnlyAcceptance $state }
                'seal' { Seal-MuSetupPrivateOutput $state }
                'stop' { Stop-MuSetupCluster $state }
            }
            Write-MuSetupEvent $state $stage 'ok'
        }
        $state.status='DB_PREPARED_LAUNCH_DISABLED'
    } catch {
        $state.status=if ($state.stage -ceq 'credentials-required') {'BLOCKED_CREDENTIALS_REQUIRED'} elseif ($state.stage -ceq 'runtime-grants') {'BLOCKED_RUNTIME_GRANTS'} else {'FAILED_RETAINED'}
        try { Write-MuSetupEvent $state $state.stage 'failed' } catch { $state.status='FAILED_JOURNAL_RETAINED' }
        if ($null -ne $state.pgOwner) {
            try { Stop-MuSetupCluster $state;Write-MuSetupEvent $state 'cleanup-stop' 'ok' }
            catch { $state.status='FAILED_OWNER_REVIEW_REQUIRED' }
        } elseif ($state.pgStartAttempted -and !$state.pgStopped) { $state.status='FAILED_OWNER_REVIEW_REQUIRED' }
    } finally {
        $state.credentials=$null
        if ($null -ne $state.claim) { $state.claim.Dispose() }
        # No automatic deletion of cluster, claim, credentials, backup or evidence.
    }
    return @{status=$state.status;stage=$state.stage;setupDirectory=$state.directory;events=$state.events;
        launchEnabled=$false;approvedLaunchManifestSha256=$null;databaseReady=($state.status -ceq 'DB_PREPARED_LAUNCH_DISABLED')}
}
