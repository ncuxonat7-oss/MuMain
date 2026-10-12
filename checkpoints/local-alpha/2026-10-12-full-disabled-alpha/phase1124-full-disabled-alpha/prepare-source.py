import pathlib,json,hashlib
R=pathlib.Path(__file__).resolve().parent; S=R/'source/scripts/windows11';h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def jsave(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
p=S/'database-source-contract.json';d=json.loads(p.read_text());d['migrationAssemblySha256']='67adf087ec8f0d3de395740f0ce09e8040777698085747fdb23d89fee4f393a1';jsave(p,d);dbhash=h(p)
p=S/'first-setup-policy.json';d=json.loads(p.read_text());d.pop('packageInventorySha256');d.update(runtimeGrantStatus='RUNTIME_GRANTS_UNRESOLVED',runtimeSourceStatus='REVIEWED',runtimeBinaryAlignment=True,liveValidationStatus='NOT_RUN');d['blockers']=['Full Entity/Typed feature-specific grant closure unresolved; grant setter remains unconditionally fenced.','Windows package/HTTP/lifecycle acceptance has not run; this package cannot be activated.'];jsave(p,d);policyhash=h(p)
p=S/'runtime-pin.json';jsave(p,{'schema':1,'kind':'LOCAL_FRAMEWORK_DEPENDENT_PUBLISHED_SERVER','checkpoint':'35f0ab6eab69974cab60f30780daed019cc0f8d5','sourceCheckpoint':'7f1f061f9201f460cd13a3dc8cd9a455870bdc36','sdk':'10.0.401','publishInventorySha256':'69c131ec847e6a730b13e53e49cf97f038003849b96bd83b810c3f415e0ce660','parentOverlayPlanSha256':'08dea6de7a5fcc67bda71b6e68d9f72d1a64b5366f804766cb9a4537164f1d59','correctedEfSha256':'67adf087ec8f0d3de395740f0ce09e8040777698085747fdb23d89fee4f393a1','serverFiles':8440,'originalRuntimeArchiveCertifiesNewServer':False,'launchEnabled':False,'approvedLaunchManifestSha256':None})
p=S/'local-session-contract.json';d=json.loads(p.read_text());d['stage']='FULL_PACKAGE_INTEGRITY_ONLY_GRANTS_AND_WINDOWS_BLOCKED';jsave(p,d)
p=S/'Guards.ps1';s=p.read_text().replace('0718c51ba1367d476a5d3fff7a46e55b16f334688ecbb650af7148b836c2cac6',dbhash)
s=s.replace('function Get-MuApprovedSetup([string]$Root) {','''function Get-MuApprovedSetup([string]$Root) {
    $null=Assert-MuPackageContract $Root
    # Package integrity is not deployment approval. This candidate cannot launch.
    throw 'RUNTIME_GRANTS_UNRESOLVED'
''')
s=s.replace("'schema','runtimeArchive','server'", "'schema','runtimeProvenance','server'").replace('$Setup.schema -ne 2','$Setup.schema -ne 3').replace("@('runtimeArchive','server'","@('server'")
a=s.index('function Read-MuRuntimeInventory(');b=s.index('\nfunction Assert-MuTree',a)
s=s[:a]+'''function Read-MuRuntimeInventory($Setup) {
    $package=Assert-MuPackageContract $Setup.root
    $result=@{}
    foreach ($key in $package.inventory.Keys) {
        if ($key.StartsWith('server/',[StringComparison]::Ordinal)) {
            $result[$key.Substring(7)]=$package.inventory[$key].sha256
        }
    }
    if ($result.Count -ne 8440) { throw 'HASH_MISMATCH' }
    return $result
}
''' +s[b:]
s=s.replace('$serverEntries.Count -ne 186','$serverEntries.Count -ne 8440')
s=s.replace("if ($file.Extension -eq '.config' -or", "if (($file.Extension -eq '.config' -and !($file.FullName -ceq (Join-Path $server 'web.config') -and (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash -ieq '3e8ddb5c187787e3ce976c1acba177a3789c0613e344dc8918d2fa1c7f8424c1')) -or")
p.write_text(s)
p=S/'FirstSetup.ps1';s=p.read_text().replace('65bea58489911fc5c1da1ee99a0ffdd8de085bad9c37251fb04d6f4e9a5c6cb0',policyhash)
s=s.replace("Assert-MuFileHash $inventoryPath $p.packageInventorySha256\n    $State.inventory=Read-MuJson $inventoryPath", "$State.inventory=(Assert-MuPackageContract $r.packageRoot).inventory")
s=s.replace('$contract.launchEnabled -ne $false', '$contract.launchEnabled -isnot [bool] -or $contract.launchEnabled -ne $false')
s=s.replace('Assert-MuSetupRequest $Request\n        $state.policy',"Assert-MuSetupRequest $Request\n        $state.stage='package-integrity';$null=Assert-MuPackageContract $Request.packageRoot\n        $state.policy")
p.write_text(s)
p=S/'Launcher.psm1';s=p.read_text();s=s.replace("'PREFLIGHT_OK','STOPPED_WITH_WARNINGS')", "'PREFLIGHT_OK','STOPPED_WITH_WARNINGS','PACKAGE_INTEGRITY_OK','RUNTIME_GRANTS_UNRESOLVED','WINDOWS_ACCEPTANCE_REQUIRED')")
s=s.replace('function Test-MuPreflight($Session, [string]$Root) {','function Test-MuPreflight($Session, [string]$Root, [switch]$IntegrityOnly, [string]$ExpectedInventorySha256) {')
s=s.replace("$setup=Get-MuApprovedSetup $Root", """if ($IntegrityOnly) {
            if ($ExpectedInventorySha256 -cnotmatch '^[a-f0-9]{64}$') { throw 'MANIFEST_REQUIRED' }
            $null=Assert-MuPackageContract $Root -VerifyPayload -ExpectedInventorySha256 $ExpectedInventorySha256
            Set-MuCode $Session 'PACKAGE_INTEGRITY_OK';return $true
        }
        $setup=Get-MuApprovedSetup $Root""",1)
s=s.replace("if (!('MuConsoleObserver' -as [type])) { Add-Type -Path (Join-Path $PSScriptRoot 'ConsoleObserver.cs') }", "# Observer compilation is deferred to the process path, unreachable while gates are closed.")
# Preserve future observer semantics without compilation at import.
s=s.replace('function Start-MuServer($Setup) {', "function Start-MuServer($Setup) {\n    if (!('MuConsoleObserver' -as [type])) { Add-Type -Path (Join-Path $PSScriptRoot 'ConsoleObserver.cs') }")
s=s.replace("runtimeArtifact='11689365514'; build='38104421623';", "runtimeArtifact='LOCAL_PUBLISHED_SERVER'; build='PUBLISH_ONLY_NO_BUILD';").replace("source='71159136c8f8cba949735be3ed0904fc15e5ad73'", "source='7f1f061f9201f460cd13a3dc8cd9a455870bdc36'")
p.write_text(s)
p=S/'StartMU.ps1';s=p.read_text();s=s.replace("[ValidateSet('Menu','Preflight','Start','Stop')]", "[ValidateSet('Menu','Verify','Preflight','Start','Stop')]").replace("[string]$PackageRoot=(Split-Path (Split-Path $PSScriptRoot))", "[string]$PackageRoot=(Split-Path (Split-Path $PSScriptRoot)),\n    [string]$ExpectedInventorySha256")
s=s.replace('$session=New-MuSession', '''$session=New-MuSession
if ($Action -eq 'Verify') {
    $ok=Test-MuPreflight $session $PackageRoot -IntegrityOnly -ExpectedInventorySha256 $ExpectedInventorySha256
    Write-Host $session.Code
    if (!$ok) { exit 2 }; exit 0
}''')
s=s.replace("WINDOWS_REQUIRED: Windows 11 required. No processes started.", "WINDOWS_ACCEPTANCE_REQUIRED: Windows 11 acceptance has not run. No processes started.")
s=s.replace("SETUP_REQUIRED='", "RUNTIME_GRANTS_UNRESOLVED='Права базы не согласованы. Запуск заблокирован.'\n        WINDOWS_ACCEPTANCE_REQUIRED='Windows-проверка не выполнена. Запуск заблокирован.'\n        SETUP_REQUIRED='")
p.write_text(s)
