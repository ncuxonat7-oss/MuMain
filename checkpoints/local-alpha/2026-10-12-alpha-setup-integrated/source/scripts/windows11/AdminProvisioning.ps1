# Setup-only, disabled by the existing first-setup policy. Import defines functions only.
# Pins come from the completed admin diagnostic; they do not approve a package or launch.
function Get-MuAdminProvisioningContract {
    $path=Join-Path $PSScriptRoot 'admin-provisioning-contract.json'
    Assert-MuLocalPath $path
    Assert-MuFileHash $path '3243bc44f592e7fe7b41bb5be329ab1d9021811aaf7dc1300052d6799a0c4377'
    return Read-MuJson $path
}

function Read-MuReviewedAdminSql($State,$Contract) {
    $root=$State.request.packageRoot
    $original=Resolve-MuFile $root 'scripts/windows11/admin-provisioning.original.sql'
    $execution=Resolve-MuFile $root 'scripts/windows11/admin-provisioning.sql'
    Assert-MuFileHash $original $Contract.originalSqlSha256
    Assert-MuFileHash $execution $Contract.executionSqlSha256
    $before=[IO.File]::ReadAllBytes($original);$after=[IO.File]::ReadAllBytes($execution)
    if ($before.Length -ne $after.Length+3 -or $before[0] -ne 239 -or
        $before[1] -ne 187 -or $before[2] -ne 191) { throw 'ADMIN_SQL_MISMATCH' }
    for ($i=0;$i -lt $after.Length;$i++) {
        if ($before[$i+3] -ne $after[$i]) { throw 'ADMIN_SQL_MISMATCH' }
    }
    return [Text.UTF8Encoding]::new($false,$true).GetString($after)
}

function Assert-MuAdminProvisioningInputs($State,$Contract) {
    if ($State.stage -cne 'admin-provision' -or $null -eq $State.pgOwner -or
        !$State.pgStartAttempted -or $State.pgStopped) { throw 'ADMIN_SETUP_REQUIRED' }
    $files=@($State.inventory.Keys | Where-Object {
        ($_ -csplit '/')[-1] -ceq 'MUnique.OpenMU.Persistence.EntityFramework.dll'
    })
    if ($files.Count -ne 1 -or $State.inventory[$files[0]].sha256 -cne $Contract.persistenceSha256) {
        throw 'ADMIN_BINARY_MISMATCH'
    }
    Assert-MuFileHash (Resolve-MuFile $State.request.packageRoot $files[0]) $Contract.persistenceSha256
    Assert-MuFileHash $State.dump $State.policy.dumpSha256
    Assert-MuFileHash (Resolve-MuFile $PSScriptRoot 'database-source-contract.json') $Contract.databaseSourceContractSha256
    $source=Get-MuDatabaseSourceContract
    if ($source.sourceCommit -cne $Contract.sourceCommit) { throw 'ADMIN_BINARY_MISMATCH' }
    Assert-MuExactStrings $Contract.migrationIds $source.migrationHistories['AdminAuth.AdminPanelContext'].ids '^[0-9]{14}_[A-Za-z0-9_]+$'
    return $source
}

function Get-MuAdminTargetSnapshot($State,[switch]$After) {
    # Values only: no account records, hashes, connection strings or SQL error text.
    $admin=if ($After) {
        '(SELECT json_agg(h ORDER BY "MigrationId") FROM admin."__EFMigrationsHistory" h)'
    } else { 'NULL' }
    $sql=@'
SELECT pg_catalog.json_build_object(
 'database',current_database(),'sessionUser',session_user,'currentUser',current_user,
 'systemIdentifier',(SELECT system_identifier::text FROM pg_catalog.pg_control_system()),
 'listenAddress',current_setting('listen_addresses'),'port',current_setting('port'),
 'directory',current_setting('data_directory'),'encoding',current_setting('server_encoding'),
 'locale',(SELECT datcollate FROM pg_catalog.pg_database WHERE datname=current_database()),
 'ctype',(SELECT datctype FROM pg_catalog.pg_database WHERE datname=current_database()),
 'adminAbsent',NOT EXISTS(SELECT FROM pg_catalog.pg_namespace WHERE nspname='admin'),
 'game',(SELECT json_agg(h ORDER BY "MigrationId") FROM public."__EFMigrationsHistory" h),
 'configurationIds',(SELECT json_agg("Id" ORDER BY "Id") FROM config."GameConfiguration"),
 'system',(SELECT json_agg(s) FROM (SELECT "Id","AutoStart","AutoUpdateSchema","ReadConsoleInput" FROM config."SystemConfiguration") s),
 'admin',
'@ + $admin + ');'
    return (Invoke-MuSetupSql $State $sql | ConvertFrom-Json -AsHashtable -Depth 10)
}

function Assert-MuAdminTarget($State,$Snapshot,$Source,[switch]$After) {
    Assert-MuKeys $Snapshot @('database','sessionUser','currentUser','directory','systemIdentifier','listenAddress','port','encoding','locale','ctype','adminAbsent','game','configurationIds','system','admin')
    if ($Snapshot.database -cne 'openmu' -or $Snapshot.sessionUser -cne 'mu_setup' -or
        $Snapshot.currentUser -cne 'mu_setup' -or $State.systemIdentifier -cnotmatch '^[0-9]{10,20}$' -or
        $Snapshot.systemIdentifier -cne $State.systemIdentifier -or $Snapshot.listenAddress -cne '127.0.0.1' -or
        $Snapshot.port -cne '5432' -or $Snapshot.encoding -cne 'SQL_ASCII' -or
        $Snapshot.locale -cne 'C' -or $Snapshot.ctype -cne 'C' -or
        $Snapshot.directory -isnot [string] -or
        [IO.Path]::GetFullPath($Snapshot.directory) -ine [IO.Path]::GetFullPath($State.pgData)) {
        throw 'ADMIN_TARGET_MISMATCH'
    }
    if ($Snapshot.adminAbsent -isnot [bool] -or $Snapshot.adminAbsent -eq [bool]$After) {
        throw 'ADMIN_SCHEMA_STATE_MISMATCH'
    }
    if ($Snapshot.game -isnot [array]) { throw 'ADMIN_BASELINE_MISMATCH' }
    foreach ($row in $Snapshot.game) {
        Assert-MuKeys $row @('MigrationId','ProductVersion')
        if ($row.ProductVersion -isnot [string] -or !$row.ProductVersion) { throw 'ADMIN_BASELINE_MISMATCH' }
    }
    Assert-MuExactStrings @($Snapshot.game | ForEach-Object {$_.MigrationId}) $Source.migrationHistories.EntityDataContext.ids '^[0-9]{14}_[A-Za-z0-9_]+$'
    Assert-MuExactStrings $Snapshot.configurationIds $Source.configurationIds '^[a-f0-9-]{36}$'
    if ($Snapshot.system -isnot [array] -or $Snapshot.system.Count -ne 1) { throw 'ADMIN_BASELINE_MISMATCH' }
    $system=$Snapshot.system[0]
    Assert-MuKeys $system @('Id','AutoStart','AutoUpdateSchema','ReadConsoleInput')
    if ($system.Id -cne $Source.systemConfigurationId -or $system.AutoStart -isnot [bool] -or
        $system.AutoUpdateSchema -isnot [bool] -or $system.ReadConsoleInput -isnot [bool] -or
        !$system.AutoStart -or !$system.AutoUpdateSchema -or $system.ReadConsoleInput) { throw 'ADMIN_BASELINE_MISMATCH' }
}

function Assert-MuAdminProvisioningResult($Before,$After,$Contract) {
    if ($After.admin -isnot [array]) { throw 'ADMIN_HISTORY_MISMATCH' }
    Assert-MuExactStrings @($After.admin | ForEach-Object {$_.MigrationId}) $Contract.migrationIds '^[0-9]{14}_[A-Za-z0-9_]+$'
    foreach ($row in $After.admin) {
        Assert-MuKeys $row @('MigrationId','ProductVersion')
        if ($row.ProductVersion -cne $Contract.productVersion) { throw 'ADMIN_HISTORY_MISMATCH' }
    }
    foreach ($row in $Before.game) {
        $historyMatches=@($After.game | Where-Object MigrationId -CEQ $row.MigrationId)
        if ($historyMatches.Count -ne 1 -or $historyMatches[0].ProductVersion -cne $row.ProductVersion) { throw 'ADMIN_BASELINE_MISMATCH' }
    }
}

function Invoke-MuSetupAdminProvisioning($State) {
    Assert-MuSetupApplication $State
    $contract=Get-MuAdminProvisioningContract
    $source=Assert-MuAdminProvisioningInputs $State $contract
    $sql=Read-MuReviewedAdminSql $State $contract
    Assert-MuSetupPgOwner $State
    $before=Get-MuAdminTargetSnapshot $State
    Assert-MuAdminTarget $State $before $source
    Assert-MuSetupPgOwner $State
    # Fixed mu_setup connection, exact reviewed SQL only; never runtime DDL or grants.
    $null=Invoke-MuSetupSql $State $sql
    Assert-MuSetupPgOwner $State
    $after=Get-MuAdminTargetSnapshot $State -After
    Assert-MuAdminTarget $State $after $source -After
    Assert-MuAdminProvisioningResult $before $after $contract
    # Exceptions propagate to the existing owned-stop/retained-state orchestration.
}
