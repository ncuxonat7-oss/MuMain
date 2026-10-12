#!/bin/bash
set -euo pipefail
cd /workspace/admin-provision-3f1U4Dge
unset DB_HOST DB_ADMIN_USER DB_ADMIN_PW
export DOTNET_CLI_TELEMETRY_OPTOUT=1 DOTNET_SKIP_FIRST_TIME_EXPERIENCE=1 DOTNET_GENERATE_ASPNET_CERTIFICATE=false DOTNET_NOLOGO=1
export DOTNET_CLI_HOME="$PWD/dotnet-home"
mkdir -m 700 "$DOTNET_CLI_HOME"
/workspace/mumain-tools/dotnet-10.0.401/dotnet exec --depsfile bundle/app/MUnique.OpenMU.Persistence.EntityFramework.deps.json --runtimeconfig bundle/app/MUnique.OpenMU.Persistence.EntityFramework.runtimeconfig.json bundle/tools/ef.dll migrations script 0 20260829110159_AddApiKeys --assembly "$PWD/bundle/app/MUnique.OpenMU.Persistence.EntityFramework.dll" --startup-assembly "$PWD/bundle/app/MUnique.OpenMU.Persistence.EntityFramework.dll" --context MUnique.OpenMU.Persistence.EntityFramework.AdminAuth.AdminPanelContext --output "$PWD/admin-official.sql" --verbose
