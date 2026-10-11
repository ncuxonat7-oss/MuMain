"""Focused offline evidence/source-contract checks. These are NOT PowerShell execution.
Optional PowerShell mock suite is skipped when pwsh is unavailable; no DB/process launch.
"""
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT.parent / 'evidence'
WIN = ROOT / 'scripts/windows11'


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class DatabaseContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = read_json(WIN / 'database-source-contract.json')
        cls.allow = read_json(EVIDENCE / 'exact-migration-allowlist.json')
        cls.compiled = read_json(EVIDENCE / 'compiled-migration-metadata.json')
        cls.baseline = read_json(EVIDENCE / 'baseline-configuration-evidence.json')
        cls.guards = (WIN / 'Guards.ps1').read_text()
        cls.database = (WIN / 'Database.ps1').read_text()
        cls.harness = (ROOT / 'tests/windows11/Test-DatabaseGuards.ps1').read_text()

    def test_expected_contract_has_fixed_digest_in_guard(self):
        expected = digest(WIN / 'database-source-contract.json')
        self.assertIn("Assert-MuFileHash $path '" + expected + "'", self.guards)
        self.assertIn('Assert-MuLocalPath $path', self.guards)
        self.assertNotIn('Invoke-MuQuery', self.guards)

    def test_no_unknown_or_merged_migration_context(self):
        self.assertEqual(set(self.contract['migrationHistories']), {'EntityDataContext', 'AdminAuth.AdminPanelContext'})
        self.assertEqual(self.contract['sourceCommit'], 'd067b3c11c23c3145de6e2c76201ab9a93b267c8')
        self.assertEqual(self.contract['sourceCommit'], self.allow['commit'])

    def test_source_tree_completeness_and_attribute_sha_provenance(self):
        self.assertTrue(self.allow['completeMigrationDirectoryTree'])
        self.assertFalse(self.allow['treeTruncated'])
        raw = read_json(EVIDENCE / 'pinned-migration-attribute-reads.json')
        self.assertFalse(raw['treeTruncated'])
        self.assertEqual(len(raw['migrationTreeEntries']), 127)
        tree = {r['path']: r['sha'] for r in raw['migrationTreeEntries']}
        actual = []
        for entry in raw['reads']:
            data = entry['result']['structuredContent']
            self.assertEqual(data['sha'], tree[entry['tree']['path']])
            content = data['content']
            contexts = re.findall(r'\[DbContext\(typeof\((\w+)\)\)\]', content)
            migrations = re.findall(r'\[Migration\("([^"]+)"\)\]', content)
            self.assertEqual(len(contexts), 1)
            self.assertEqual(len(migrations), 1)
            actual.append((contexts[0], migrations[0]))
        expected = [(c, i) for c, ids in self.allow['contexts'].items() for i in ids]
        self.assertEqual(sorted(actual), sorted(expected))
        self.assertEqual(len(actual), len(set(actual)))

    def test_exact_game_migration_set_from_source(self):
        values = self.contract['migrationHistories']['EntityDataContext']['ids']
        self.assertEqual(values, self.allow['contexts']['EntityDataContext'])
        self.assertEqual(len(values), 63)
        self.assertEqual(values[0], '00000000000000_Initial')
        self.assertEqual(values[-1], '20261006212931_AddCashShop')

    def test_exact_admin_migration_set_from_source(self):
        values = self.contract['migrationHistories']['AdminAuth.AdminPanelContext']['ids']
        self.assertEqual(values, self.allow['contexts']['AdminPanelContext'])
        self.assertEqual(values, ['20260824171349_InitialAdminPanelUsers', '20260829110159_AddApiKeys'])

    def test_compiled_migration_ids_and_contexts_match_source(self):
        actual = []
        for r in self.compiled['migrations']:
            self.assertEqual(len(r['migrationAttributeValues']), 1)
            self.assertEqual(len(r['contextAttributeValues']), 1)
            self.assertEqual(r['extends'], 'Microsoft.EntityFrameworkCore.Migrations.Migration')
            self.assertFalse(r['flags'] & 0x80)  # abstract class
            context = r['contextAttributeValues'][0].rsplit('.', 1)[-1]
            actual.append((context, r['id']))
        expected = [(c, i) for c, ids in self.allow['contexts'].items() for i in ids]
        self.assertEqual(sorted(actual), sorted(expected))
        self.assertEqual(len(actual), len(set(actual)))

    def test_compiled_identity_pinned_by_new_guard(self):
        self.assertEqual(self.contract['migrationAssemblySha256'], self.compiled['artifactSha256'])
        self.assertEqual(self.contract['migrationAssemblySha256'], 'f05e117d596f6bb74f953d8b4cbe83c73c0b30a6acf94876b6e8619bf92f1042')
        self.assertIn('$Setup.hashes[$migrationAssembly] -cne $databaseSource.migrationAssemblySha256', self.guards)
        self.assertEqual(self.contract['runtimeArchiveSha256'], '505d1053d235417876c59f31e2dbb0338bad955dee31c193ccf167da28355f8c')

    def test_configuration_comes_from_pinned_preserved_export(self):
        self.assertEqual(self.baseline['archiveSha256'], self.contract['baselineArchiveSha256'])
        self.assertEqual(self.baseline['exportSha256'], self.contract['configurationExportSha256'])
        self.assertEqual(self.baseline['exportSha256'], '8bc79da233fef2b91f703a8189423bbb573830b573b8657b4c7fd21c5467a54a')
        self.assertEqual(self.contract['configurationIds'], [r['Id'] for r in self.baseline['tables']['GameConfiguration']])
        self.assertEqual(self.contract['configurationIds'], ['00000001-0001-0000-0000-000000000000'])

    def test_original_baseline_settings_are_not_rewritten(self):
        rows = self.baseline['tables']['SystemConfiguration']
        self.assertEqual(len(rows), 1)
        self.assertTrue(rows[0]['AutoUpdateSchema'])
        self.assertFalse(rows[0]['ReadConsoleInput'])
        self.assertEqual(self.contract['systemConfigurationId'], rows[0]['Id'])
        self.assertIn('$systems[0].autoUpdateSchema -cne $false', self.database)
        self.assertIn('$systems[0].readConsoleInput -cne $true', self.database)
        self.assertIn('$systems[0].id -cne (Get-MuDatabaseSourceContract).systemConfigurationId', self.database)

    def test_endpoint_contract_matches_independent_export(self):
        rows = self.baseline['tables']
        expected = {'game': [{'port': r['NetworkPort'], 'published': r['AlternativePublishedPort']} for r in rows['GameServerEndpoint']],
                    'chat': [{'port': r['NetworkPort']} for r in rows['ChatServerEndpoint']],
                    'connect': [{'port': r['ClientListenerPort']} for r in rows['ConnectServerDefinition']]}
        self.assertEqual(self.contract['endpoints'], expected)
        self.assertIn('$expectedEndpoints=(Get-MuDatabaseSourceContract).endpoints', self.guards)

    def test_schema_v2_rejects_old_single_history_shape(self):
        self.assertIn('if ($Setup.schema -ne 2)', self.guards)
        self.assertIn("'migrationHistories'", self.guards)
        self.assertNotIn("'migrationSchema'", self.guards)
        self.assertNotIn('$Setup.database.migrationIds', self.database)
        self.assertIn("Assert-MuKeys $Db.migrationHistories @('EntityDataContext','AdminAuth.AdminPanelContext')", self.guards)

    def test_both_contexts_use_probe_and_their_own_runtime_credential(self):
        orchestrator = self.database.split('function Assert-MuDatabase($Setup) {', 1)[1]
        self.assertIn("foreach ($context in @('EntityDataContext','AdminAuth.AdminPanelContext'))", orchestrator)
        self.assertIn('Invoke-MuQuery $Setup $sql -PreserveSearchPath', orchestrator)
        self.assertIn('Invoke-MuQuery $Setup $sql $credentials[$context] -PreserveSearchPath', orchestrator)

    def test_history_source_query_is_read_only_and_fixed_table(self):
        query = self.database.split('function Get-MuHistorySql', 1)[1].split('function Assert-MuHistory', 1)[0]
        self.assertIn('Assert-MuDatabaseShape $Setup.database', query)
        self.assertIn("$Context -cnotin @('EntityDataContext','AdminAuth.AdminPanelContext')", query)
        self.assertIn('FROM "$schema"."__EFMigrationsHistory"', query)
        self.assertNotRegex(query, r'(?i)\b(INSERT|UPDATE|DELETE|CREATE|ALTER|DROP|TRUNCATE|GRANT|REVOKE)\b')
        self.assertIn("'BEGIN READ ONLY; ' + $Sql + '; COMMIT;'", self.database)
        self.assertIn('statement_timeout=5000', self.database)
        self.assertIn("$child.PGCONNECT_TIMEOUT='5'", self.database)

    def test_product_version_read_and_type_guarded_for_ef_compatibility(self):
        self.assertIn("'productVersion',\"ProductVersion\"", self.database)
        self.assertIn("Assert-MuKeys $row @('id','productVersion')", self.database)
        self.assertIn('$row.productVersion -isnot [string]', self.database)
        self.assertIn('$row.id -isnot [string]', self.database)
        self.assertIn('$History.migrations.Count -ne $expected.ids.Count', self.database)
        self.assertIn('array history ID rejected before pipeline projection', self.harness)
        self.assertIn("missing ProductVersion rejected", self.harness)
        self.assertIn("null ProductVersion rejected", self.harness)
        self.assertIn("ProductVersion SELECT denial blocks", self.harness)

    def test_game_search_path_checked_without_overriding_runtime_resolution(self):
        self.assertIn('[switch]$PreserveSearchPath', self.database)
        self.assertIn("if (!$PreserveSearchPath) { $child.PGOPTIONS+=' -c search_path=pg_catalog' }", self.database)
        self.assertIn('pg_catalog.to_regclass', self.database)
        self.assertIn('$History.resolvedSchema -cne $expected.schema', self.database)
        self.assertEqual(self.contract['migrationHistories']['EntityDataContext']['schema'], 'public')
        self.assertEqual(self.contract['migrationHistories']['AdminAuth.AdminPanelContext']['schema'], 'admin')

    def test_safe_array_shape_and_duplicates_checked(self):
        self.assertIn('$Actual -isnot [array]', self.guards)
        self.assertIn('$Actual.Count -ne $Expected.Count', self.guards)
        self.assertIn('@($Actual | Sort-Object -Unique).Count -ne $Actual.Count', self.guards)
        self.assertIn('$value -isnot [string]', self.guards)

    def test_launcher_disabled_and_host_values_unknown(self):
        launch = read_json(WIN / 'local-session-contract.json')
        draft = read_json(ROOT / 'docs/windows11-database-manifest-draft.json')
        for data in (launch, draft):
            self.assertIs(data['launchEnabled'], False)
            self.assertIsNone(data['approvedLaunchManifestSha256'])
        for key in ('queryUser', 'pgPassFile', 'systemIdentifier', 'runtimeRoles'):
            self.assertIsNone(draft['database'][key])
        self.assertEqual(draft['status'], 'DRAFT_NOT_APPROVED')

    def test_mock_harness_is_prepared_and_has_no_actual_service_invocation(self):
        self.assertGreaterEqual(len(re.findall(r"^Check '", self.harness, re.M)), 32)
        self.assertIn('function Invoke-MuQuery(', self.harness)
        self.assertIn('function Get-MuConnections(', self.harness)
        self.assertNotRegex(self.harness, r'(?i)\b(Start-Process|Start-MuSession|pg_restore|initdb|postgres\.exe|psql\.exe)\b')

    def test_source_evidence_hashes_unchanged(self):
        verification = read_json(EVIDENCE / 'migration-contract-verification.json')
        for name, expected in verification['evidence_files'].items():
            self.assertEqual(digest(EVIDENCE / name), expected, name)

    @unittest.skipUnless(shutil.which('pwsh'), 'PowerShell unavailable; mock behavior suite NOT_RUN')
    def test_powershell_mock_behavior_if_runtime_available(self):
        result = subprocess.run([shutil.which('pwsh'), '-NoProfile', '-NonInteractive', '-File',
                                 str(ROOT / 'tests/windows11/Test-DatabaseGuards.ps1')],
                                text=True, capture_output=True, timeout=60)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('PASS TOTAL 40', result.stdout)


if __name__ == '__main__':
    unittest.main(verbosity=2)
