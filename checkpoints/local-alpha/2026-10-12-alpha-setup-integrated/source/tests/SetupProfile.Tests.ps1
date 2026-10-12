# Actual PowerShell unit tests. Synthetic fixtures only; never launches utilities.
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$code=Join-Path (Split-Path $PSScriptRoot) 'scripts/windows11'
. (Join-Path $code 'Guards.ps1')
. (Join-Path $code 'FirstSetup.ps1')
$script:results=@();$script:sqlCalls=@();$script:utilityCalls=0
function Test-Case([string]$Name,[scriptblock]$Body,[string]$Failure='') {
    try {
        & $Body
        if ($Failure) { throw 'EXPECTED_REJECTION_MISSING' }
        $script:results+=@{name=$Name;status='PASS'}
    } catch {
        if ($Failure -and ($Failure -eq '*' -or $_.Exception.Message -ceq $Failure)) { $script:results+=@{name=$Name;status='PASS'} }
        else { $script:results+=@{name=$Name;status='FAIL';error=$_.Exception.Message} }
    }
}
function Must($Condition) { if (!$Condition) { throw 'ASSERTION_FAILED' } }
function Clone($Value) { return ($Value | ConvertTo-Json -Depth 40 | ConvertFrom-Json -AsHashtable -Depth 40) }
# External process/database boundaries only. The profile, path, credential,
# approval, identity and migration validators below execute without stubbing.
function Invoke-MuSetupUtility { $script:utilityCalls++;throw 'EXTERNAL_UTILITY_FORBIDDEN_IN_UNIT_TEST' }
function Assert-MuSetupPgOwner { param($State) if ($null -eq $State.pgOwner) { throw 'OWNER_LOST' } }
function Invoke-MuSetupSql { param($State,$Sql,$Database='openmu')
    $script:sqlCalls+=@{sql=$Sql;database=$Database}
    if ($Sql.StartsWith('BEGIN READ ONLY;')) { return $script:observedIdentity | ConvertTo-Json -Depth 20 -Compress }
    return ''
}
$temp=Join-Path ([IO.Path]::GetTempPath()) ('mu-profile-unit-'+[Guid]::NewGuid().ToString('N'))
$null=New-Item -ItemType Directory $temp
try {
    $policy=Get-MuFirstSetupPolicy
    $contract=Get-MuDatabaseSourceContract
    $profile=Get-MuDisposableProfile
    $originalHashes=@{}
    foreach ($f in Get-ChildItem $code -File) { $originalHashes[$f.Name]=(Get-FileHash $f.FullName).Hash }
    Test-Case 'valid-prepared-policy-not-runtime-acceptance' { Assert-MuSetupGrantPolicy $policy;Must ($policy.liveValidationStatus -ceq 'NOT_RUN') }
    Test-Case 'explicit-pending-role-split' {
        $consumer=@($profile.roles.mu_account.tables | Where-Object table -CEQ 'data.CastleSiegePendingReward')[0]
        $producer=@($profile.roles.mu_typed.tables | Where-Object table -CEQ 'data.CastleSiegePendingReward')[0]
        Must (($consumer.operations -join ',') -ceq 'SELECT,DELETE');Must (($producer.operations -join ',') -ceq 'INSERT')
    }
    $sql=Get-MuSetupKnownGrantsSql
    Test-Case 'explicit-sql-no-schema-wide-or-minigame-ranking-grants' {
        Must ($sql -notmatch 'ALL TABLES|ALL SEQUENCES|DEFAULT PRIVILEGES|MiniGameRankingEntry|SUPERUSER|CREATE ROLE|MIGRATE')
        Must ($sql.Contains('GRANT SELECT,DELETE ON data."CastleSiegePendingReward" TO mu_account;'))
        Must ($sql.Contains('GRANT INSERT ON data."CastleSiegePendingReward" TO mu_typed;'))
        Must ($sql.Contains('GRANT SELECT ON friend."Friend" TO mu_friend;'))
    }
    foreach ($mutation in @('runtimeGrantStatus','runtimeSourceStatus','runtimeBinaryAlignment','liveValidationStatus','profileSha256','listenAddress','launchEnabled','approvedLaunchManifestSha256')) {
        $p=Clone $policy
        switch ($mutation) {
            'runtimeBinaryAlignment' {$p[$mutation]=$false}
            'launchEnabled' {$p[$mutation]=$true}
            'approvedLaunchManifestSha256' {$p[$mutation]='a'*64}
            'liveValidationStatus' {$p[$mutation]='PASSED'}
            'listenAddress' {$p[$mutation]='0.0.0.0'}
            default {$p[$mutation]='ALTERED'}
        }
        Test-Case ('reject-policy-'+$mutation) { Assert-MuSetupGrantPolicy $p } '*'
    }
    $credentialPath=Join-Path $temp 'synthetic-fixture.json'
    $credentials=@{}
    foreach ($role in @('mu_setup','mu_entity','mu_typed','mu_admin','mu_account','mu_config','mu_friend','mu_guild','mu_probe')) {
        $credentials[$role]='UNIT_TEST_ONLY_NOT_A_DEPLOYED_SECRET_0000'
    }
    Write-MuNewPrivateText $credentialPath ($credentials | ConvertTo-Json)
    Test-Case 'synthetic-credential-shape-valid' { Assert-MuSetupCredentialValues $credentials }
    Test-Case 'missing-credentials' { Assert-MuSetupCredentialValues $null } 'CREDENTIALS_REQUIRED'
    Test-Case 'missing-credential-role' { $v=Clone $credentials;$v.Remove('mu_admin');Assert-MuSetupCredentialValues $v } 'UNSAFE_CONFIG'
    Test-Case 'empty-credential' { $v=Clone $credentials;$v.mu_account='';Assert-MuSetupCredentialValues $v } 'INVALID_PRIVATE_INPUT'
    Test-Case 'wrong-type-credential' { $v=Clone $credentials;$v.mu_account=123;Assert-MuSetupCredentialValues $v } 'INVALID_PRIVATE_INPUT'
    Test-Case 'invalid-credential-not-echoed' {
        $v=Clone $credentials;$v.mu_account='DO_NOT_ECHO_THIS_PRIVATE_TEST_MARKER!'
        try { Assert-MuSetupCredentialValues $v;throw 'EXPECTED_REJECTION_MISSING' }
        catch { Must ($_.Exception.Message -ceq 'INVALID_PRIVATE_INPUT') }
    }
    $request=@{packageRoot=$temp;setupRelative='database/setup-test';archive=(Join-Path $temp 'baseline.zip');credentialBundle=$credentialPath;confirmNewDatabase=$true;confirmCredentialHandling=$true;applyReviewedFlags=$true}
    Test-Case 'valid-setup-request' { Assert-MuSetupRequest $request }
    foreach ($key in @('confirmNewDatabase','confirmCredentialHandling','applyReviewedFlags')) {
        $v=Clone $request;$v[$key]=$false
        Test-Case ('missing-request-approval-'+$key) { Assert-MuSetupRequest $v } 'SETUP_APPROVAL_REQUIRED'
    }
    Test-Case 'unsafe-setup-relative' { $v=Clone $request;$v.setupRelative='database/../server';Assert-MuSetupRequest $v } 'UNSAFE_CONFIG'
    $state=@{request=$request;policy=$policy;credentials=$credentials;pgData=(Join-Path $temp 'database/setup-test/cluster');pgOwner=@{pid=999};systemIdentifier='1234567890123456789'}
    Test-Case 'missing-application-approval-before-sql' { Assert-MuSetupApplication $state } 'SETUP_APPLICATION_APPROVAL_REQUIRED'
    $approval=@{schema=1;scope='NEW_DISPOSABLE_LOCAL_ALPHA_SETUP';packageRoot=$temp;setupRelative=$request.setupRelative;profileSha256=$policy.profileSha256;credentialBundleSha256=(Get-FileHash $credentialPath).Hash.ToLowerInvariant();adminSchemaMode='ExternallyProvisioned';launchEnabled=$false;approvedLaunchManifestSha256=$null}
    $approvalPath=Join-Path $temp 'setup-application-approval.json'
    Write-MuNewPrivateText $approvalPath ($approval | ConvertTo-Json)
    $state.policy=Clone $policy;$state.policy.setupApplicationApprovalSha256=(Get-FileHash $approvalPath).Hash.ToLowerInvariant()
    Test-Case 'valid-synthetic-application-approval' { Assert-MuSetupApplication $state }
    Test-Case 'wrong-application-target' { $v=Clone $state;$v.request.setupRelative='database/setup-other';Assert-MuSetupApplication $v } 'SETUP_APPLICATION_APPROVAL_REQUIRED'
    Test-Case 'altered-application-evidence' { $v=Clone $state;$v.policy.setupApplicationApprovalSha256='a'*64;Assert-MuSetupApplication $v } 'HASH_MISMATCH'
    $identity=@{user='mu_setup';database='openmu';dataDirectory=$state.pgData;listenAddress='127.0.0.1';port='5432';systemIdentifier=$state.systemIdentifier;histories=@{}}
    foreach ($context in $contract.migrationHistories.Keys) { $identity.histories[$context]=$contract.migrationHistories[$context].ids }
    Test-Case 'prepared-identity-with-exact-game-admin-histories' { Assert-MuPreparedGrantIdentity $state $identity }
    foreach ($key in @('user','database','dataDirectory','listenAddress','port','systemIdentifier')) {
        $v=Clone $identity;$v[$key]=if ($key -eq 'dataDirectory') {Join-Path $temp 'other'} else {'WRONG'}
        Test-Case ('reject-identity-'+$key) { Assert-MuPreparedGrantIdentity $state $v } 'PREPARED_DATABASE_IDENTITY_REQUIRED'
    }
    Test-Case 'missing-admin-history-no-auto-migration' { $v=Clone $identity;$v.histories['AdminAuth.AdminPanelContext']=@();Assert-MuPreparedGrantIdentity $state $v } 'UNSAFE_CONFIG'
    Test-Case 'missing-owner' { $v=Clone $state;$v.pgOwner=$null;Assert-MuPreparedGrantIdentity $v $identity } 'PREPARED_DATABASE_IDENTITY_REQUIRED'
    $script:observedIdentity=$identity
    Test-Case 'grant-setter-gated-read-and-transaction-stub-only' {
        $script:sqlCalls=@();Set-MuSetupRuntimeGrants $state
        Must ($script:sqlCalls.Count -eq 2)
        Must ($script:sqlCalls[0].sql.StartsWith('BEGIN READ ONLY;'))
        Must ($script:sqlCalls[1].sql.StartsWith('BEGIN;'))
        Must ($script:sqlCalls[1].sql.Contains('PREPARED_DATABASE_IDENTITY_REQUIRED'))
        Must ($script:sqlCalls[1].sql.EndsWith('COMMIT;'))
    }
    Test-Case 'bad-identity-prevents-grant-call' {
        $script:observedIdentity=Clone $identity;$script:observedIdentity.database='wrong';$script:sqlCalls=@()
        try { Set-MuSetupRuntimeGrants $state;throw 'EXPECTED_REJECTION_MISSING' }
        catch { Must ($_.Exception.Message -ceq 'PREPARED_DATABASE_IDENTITY_REQUIRED');Must ($script:sqlCalls.Count -eq 1) }
    }
    foreach ($path in @('../escape','/absolute','a/../../b','a\\b','NUL','a:stream','a/space ','a//b')) {
        Test-Case ('reject-relative-'+$path) { Assert-MuRelative $path } 'UNSAFE_CONFIG'
    }
    Test-Case 'existing-private-file-no-overwrite' {
        $before=(Get-FileHash $credentialPath).Hash
        try { Write-MuNewPrivateText $credentialPath 'overwrite';throw 'EXPECTED_REJECTION_MISSING' }
        catch { Must ($_.Exception.Message -ne 'EXPECTED_REJECTION_MISSING') }
        Must ((Get-FileHash $credentialPath).Hash -ceq $before)
    }
    $link=Join-Path $temp 'linked'
    $null=New-Item -ItemType SymbolicLink -Path $link -Target $code
    Test-Case 'reject-symlink-parent' { Write-MuNewPrivateText (Join-Path $link 'must-not-exist') 'fixture' } 'UNSAFE_CONFIG'
    # Package verification needs the full unavailable payload. Stub that boundary
    # only for this launcher test; launch contract hash and gate execute for real.
    function Assert-MuPackageContract { param($Root) return @{} }
    Test-Case 'disabled-launch-real-contract' { Get-MuApprovedSetup $temp } 'SETUP_REQUIRED'
    $tampered=Join-Path $temp 'tampered-source';$null=New-Item -ItemType Directory $tampered
    foreach ($f in Get-ChildItem $code -File) { Copy-Item $f.FullName (Join-Path $tampered $f.Name) }
    $tamperedProfile=Read-MuJson (Join-Path $tampered 'disposable-role-profile.json')
    $tamperedProfile.roles.mu_account.tables+=@{table='data.MiniGameRankingEntry';operations=@('INSERT')}
    $tamperedProfile | ConvertTo-Json -Depth 40 | Set-Content (Join-Path $tampered 'disposable-role-profile.json')
    Test-Case 'altered-on-disk-profile-rejected' {
        & { . (Join-Path $tampered 'FirstSetup.ps1');Get-MuDisposableProfile }
    } 'HASH_MISMATCH'
    $tamperedContract=Read-MuJson (Join-Path $tampered 'local-session-contract.json')
    $tamperedContract.launchEnabled=$true;$tamperedContract.approvedLaunchManifestSha256='a'*64
    $tamperedContract | ConvertTo-Json -Depth 20 | Set-Content (Join-Path $tampered 'local-session-contract.json')
    Test-Case 'altered-launch-contract-rejected' {
        & { . (Join-Path $tampered 'Guards.ps1');function Assert-MuPackageContract {param($Root) return @{}};Get-MuApprovedSetup $temp }
    } 'HASH_MISMATCH'
    Test-Case 'nonloopback-hba-rejected' {
        Assert-MuHba @{database=@{runtimeRoles=@('mu_account');queryUser='mu_probe';name='openmu'}} @('host openmu mu_account 0.0.0.0/0 scram-sha-256','host openmu mu_probe 127.0.0.1/32 scram-sha-256')
    } 'UNSAFE_CONFIG'
    Test-Case 'invoke-stops-before-credentials-or-startup' {
        $r=Invoke-MuFirstSetup $request
        Must ($r.stage -ceq 'application-approval');Must (!$r.databaseReady);Must (!$r.launchEnabled)
    }
    . (Join-Path $code 'AdminProvisioning.ps1')
    $adminContract=Get-MuAdminProvisioningContract
    Test-Case 'admin-candidate-pin-and-unchanged-migrations' {
        Must ($adminContract.persistenceSha256 -ceq '67adf087ec8f0d3de395740f0ce09e8040777698085747fdb23d89fee4f393a1')
        Assert-MuExactStrings $adminContract.migrationIds $contract.migrationHistories['AdminAuth.AdminPanelContext'].ids '^[0-9]{14}_[A-Za-z0-9_]+$'
        Must ($adminContract.sourceCommit -ceq $contract.sourceCommit)
    }
    $adminState=Clone $state
    $adminState.stage='admin-provision';$adminState.pgStartAttempted=$true;$adminState.pgStopped=$false
    $adminState.inventory=@{'server/MUnique.OpenMU.Persistence.EntityFramework.dll'=@{sha256=$adminContract.persistenceSha256}}
    $adminState.dump=Join-Path $temp 'baseline.dump'
    $sqlState=@{request=@{packageRoot=(Split-Path (Split-Path $code))}}
    $reviewedSql=Read-MuReviewedAdminSql $sqlState $adminContract
    Test-Case 'admin-official-sql-bom-only-and-pinned' { Must ($reviewedSql.Contains('CREATE TABLE admin."ApiKey"'));Must ($adminContract.executionSqlSha256 -ceq '5e3f625b6c6b0a56596e36763df592fa1fb11a1b000d6a386e3c7e2ed95d62dd') }
    Test-Case 'admin-wrong-sql-hash-rejected' { $c=Clone $adminContract;$c.executionSqlSha256='a'*64;Read-MuReviewedAdminSql $sqlState $c } 'HASH_MISMATCH'
    foreach ($key in @('stage','pgOwner','pgStartAttempted','pgStopped')) {
        $v=Clone $adminState
        switch ($key) { 'stage' {$v.stage='grants'} 'pgOwner' {$v.pgOwner=$null} 'pgStartAttempted' {$v.pgStartAttempted=$false} 'pgStopped' {$v.pgStopped=$true} }
        Test-Case ('admin-reject-state-'+$key) { Assert-MuAdminProvisioningInputs $v $adminContract } 'ADMIN_SETUP_REQUIRED'
    }
    Test-Case 'admin-original-binary-rejected' { $v=Clone $adminState;$v.inventory.Values[0].sha256=$adminContract.originalPersistenceSha256;Assert-MuAdminProvisioningInputs $v $adminContract } 'ADMIN_BINARY_MISMATCH'
    $before=@{database='openmu';sessionUser='mu_setup';currentUser='mu_setup';directory=$state.pgData;systemIdentifier=$state.systemIdentifier;listenAddress='127.0.0.1';port='5432';encoding='SQL_ASCII';locale='C';ctype='C';adminAbsent=$true;game=@($contract.migrationHistories.EntityDataContext.ids | ForEach-Object {@{MigrationId=$_;ProductVersion='10.0.2'}});configurationIds=$contract.configurationIds;system=@(@{Id=$contract.systemConfigurationId;AutoStart=$true;AutoUpdateSchema=$true;ReadConsoleInput=$false});admin=$null}
    $after=Clone $before;$after.adminAbsent=$false;$after.admin=@($adminContract.migrationIds | ForEach-Object {@{MigrationId=$_;ProductVersion='10.0.2'}})
    Test-Case 'admin-valid-before-and-after-exact-histories' { Assert-MuAdminTarget $adminState $before $contract;Assert-MuAdminTarget $adminState $after $contract -After;Assert-MuAdminProvisioningResult $before $after $adminContract }
    foreach ($key in @('database','sessionUser','currentUser','systemIdentifier','listenAddress','port','encoding','locale','ctype')) {
        $v=Clone $before;$v[$key]='wrong'
        Test-Case ('admin-reject-target-'+$key) { Assert-MuAdminTarget $adminState $v $contract } 'ADMIN_TARGET_MISMATCH'
    }
    Test-Case 'admin-existing-schema-rejected' { $v=Clone $before;$v.adminAbsent=$false;Assert-MuAdminTarget $adminState $v $contract } 'ADMIN_SCHEMA_STATE_MISMATCH'
    Test-Case 'admin-missing-game-migration-rejected' { $v=Clone $before;$v.game=$v.game[1..($v.game.Count-1)];Assert-MuAdminTarget $adminState $v $contract } 'UNSAFE_CONFIG'
    Test-Case 'admin-wrong-admin-product-version-rejected' { $v=Clone $after;$v.admin[0].ProductVersion='wrong';Assert-MuAdminProvisioningResult $before $v $adminContract } 'ADMIN_HISTORY_MISMATCH'
    Test-Case 'admin-mutated-game-version-rejected' { $v=Clone $after;$v.game[0].ProductVersion='wrong';Assert-MuAdminProvisioningResult $before $v $adminContract } 'ADMIN_BASELINE_MISMATCH'
    Test-Case 'admin-application-gate-before-sql' { $v=Clone $adminState;$v.policy=$policy;Invoke-MuSetupAdminProvisioning $v } 'SETUP_APPLICATION_APPROVAL_REQUIRED'
    Test-Case 'admin-exact-sql-once-with-real-target-validators' {
        # File inventory input boundary uses synthetic paths; exact real SQL and
        # target/history validators still execute. No process or DB boundary opens.
        function Assert-MuAdminProvisioningInputs { param($State,$Contract) return $script:databaseSourceFixture }
        function Read-MuReviewedAdminSql { param($State,$Contract) return $reviewedSql }
        $script:databaseSourceFixture=$contract;$script:adminBeforeFixture=$before;$script:adminAfterFixture=$after
        $script:adminSql=@();$script:snapshots=0
        function Invoke-MuSetupSql { param($State,$Sql,$Database='openmu')
            $script:adminSql+=,$Sql
            if ($Sql.StartsWith('SELECT pg_catalog.json_build_object')) {
                $script:snapshots++;if ($script:snapshots -eq 1) {return $script:adminBeforeFixture | ConvertTo-Json -Depth 10 -Compress};return $script:adminAfterFixture | ConvertTo-Json -Depth 10 -Compress
            }
            Must ($Sql -ceq $reviewedSql);return ''
        }
        Invoke-MuSetupAdminProvisioning $adminState
        Must ($script:adminSql.Count -eq 3);Must ($script:adminSql[1] -ceq $reviewedSql)
    }
    Test-Case 'admin-inventory-cannot-admit-wrong-file-bytes' {
        $server=Join-Path $temp 'server';$null=New-Item -ItemType Directory $server
        Write-MuNewPrivateText (Join-Path $server 'MUnique.OpenMU.Persistence.EntityFramework.dll') 'SYNTHETIC_NOT_A_DLL'
        Assert-MuAdminProvisioningInputs $adminState $adminContract
    } 'HASH_MISMATCH'
    Test-Case 'admin-sql-failure-propagates-without-retry' {
        $script:databaseSourceFixture=$contract;$script:adminBeforeFixture=$before;$script:adminAfterFixture=$after
        function Assert-MuAdminProvisioningInputs {param($State,$Contract) return $script:databaseSourceFixture}
        function Read-MuReviewedAdminSql {param($State,$Contract) return $reviewedSql}
        $script:failedSqlCount=0
        function Invoke-MuSetupSql {param($State,$Sql,$Database='openmu')
            if ($Sql.StartsWith('SELECT pg_catalog.json_build_object')) { return $script:adminBeforeFixture | ConvertTo-Json -Depth 10 -Compress }
            $script:failedSqlCount++;throw 'SYNTHETIC_SQL_FAILURE'
        }
        try {Invoke-MuSetupAdminProvisioning $adminState;throw 'EXPECTED_REJECTION_MISSING'}
        catch {Must ($_.Exception.Message -ceq 'SYNTHETIC_SQL_FAILURE');Must ($script:failedSqlCount -eq 1)}
    }
    foreach ($failure in @('','admin-provision')) {
        Test-Case ('setup-admin-stage-order-cleanup-'+$(if($failure){'failure'}else{'success'})) {
            $script:stages=@();$script:stops=0
            function Assert-MuSetupApplication {param($State)}
            function Assert-MuSetupCredentialInput {param($State)}
            function Assert-MuSetupHostAndInputs {param($State)}
            function Initialize-MuSetupPrivateArea {param($State)}
            function Read-MuSetupCredentials {param($State)}
            function Expand-MuSetupDump {param($State)}
            function Initialize-MuSetupCluster {param($State)}
            function Start-MuSetupCluster {param($State) $State.pgOwner=@{pid=999};$State.pgStartAttempted=$true}
            function New-MuSetupRolesAndDatabase {param($State)}
            function Restore-MuSetupSnapshot {param($State) $script:stages+='restore'}
            function Invoke-MuSetupAdminProvisioning {param($State) $script:stages+=$State.stage;if($failure){throw 'SYNTHETIC_ADMIN_FAILURE'}}
            function Set-MuSetupRuntimeGrants {param($State) $script:stages+='grants'}
            function Set-MuSetupReviewedFlags {param($State) $script:stages+='flags'}
            function Prepare-MuSetupAcceptance {param($State)}
            function Test-MuSetupReadOnlyAcceptance {param($State)}
            function Seal-MuSetupPrivateOutput {param($State)}
            function Stop-MuSetupCluster {param($State) $script:stops++;$State.pgOwner=$null;$State.pgStopped=$true}
            $r=Invoke-MuFirstSetup $request
            Must ($script:stops -eq 1);Must (!$r.launchEnabled)
            if ($failure) {Must (!$r.databaseReady);Must (($script:stages -join ',') -ceq 'restore,admin-provision');Must ($r.status -ceq 'FAILED_RETAINED')}
            else {Must ($r.databaseReady);Must (($script:stages -join ',') -ceq 'restore,admin-provision,grants,flags')}
        }
    }
    Test-Case 'no-external-utility-called' { Must ($script:utilityCalls -eq 0) }
    Test-Case 'source-inputs-unchanged-by-tests' {
        foreach ($name in $originalHashes.Keys) { Must ((Get-FileHash (Join-Path $code $name)).Hash -ceq $originalHashes[$name]) }
    }
} finally {
    if (Test-Path $temp) { Remove-Item -LiteralPath $temp -Recurse -Force }
}
$failed=@($script:results | Where-Object status -eq 'FAIL').Count
$report=@{kind='ACTUAL_POWERSHELL_UNIT_TESTS_WITH_EXTERNAL_BOUNDARY_STUBS';passed=($script:results.Count-$failed);failed=$failed;total=$script:results.Count;databaseOperations=0;windowsAcceptance='NOT_RUN';utilityCalls=$script:utilityCalls;cases=$script:results}
$report | ConvertTo-Json -Depth 8 | Set-Content (Join-Path $PSScriptRoot 'results.json')
$report | ConvertTo-Json -Depth 8
if ($failed) { exit 1 }
