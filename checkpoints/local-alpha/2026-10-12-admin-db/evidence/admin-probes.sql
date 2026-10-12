BEGIN;
SET LOCAL statement_timeout = '5s';
SET LOCAL lock_timeout = '1s';
SET LOCAL search_path = pg_catalog;
SET LOCAL ROLE :"admin_role";
SELECT "MigrationId", "ProductVersion" FROM admin."__EFMigrationsHistory" WHERE false;
SELECT "Id", "LoginName", "NormalizedLoginName", "PasswordHash", "SecurityStamp", "Roles", "IsTwoFactorEnabled", "ProtectedAuthenticatorKey", "RecoveryCodeHashes", "LastAcceptedTotpStep", "AccessFailedCount", "LockoutEnd", "IsDisabled", "CreatedAt", "LastLoginAt" FROM admin."AdminUser" WHERE false;
SELECT "Id", "Name", "KeyHash", "KeyPrefix", "Roles", "IsDisabled", "CreatedAt" FROM admin."ApiKey" WHERE false;
INSERT INTO admin."AdminUser" ("Id","LoginName","NormalizedLoginName","PasswordHash","SecurityStamp","Roles","IsTwoFactorEnabled","ProtectedAuthenticatorKey","RecoveryCodeHashes","LastAcceptedTotpStep","AccessFailedCount","LockoutEnd","IsDisabled","CreatedAt","LastLoginAt")
SELECT NULL::uuid,NULL::varchar(100),NULL::varchar(100),NULL::text,NULL::text,NULL::varchar(200),NULL::boolean,NULL::text,NULL::text,NULL::bigint,NULL::integer,NULL::timestamptz,NULL::boolean,NULL::timestamptz,NULL::timestamptz WHERE false;
UPDATE admin."AdminUser" SET "LoginName"="LoginName", "NormalizedLoginName"="NormalizedLoginName", "PasswordHash"="PasswordHash", "SecurityStamp"="SecurityStamp", "Roles"="Roles", "IsTwoFactorEnabled"="IsTwoFactorEnabled", "ProtectedAuthenticatorKey"="ProtectedAuthenticatorKey", "RecoveryCodeHashes"="RecoveryCodeHashes", "LastAcceptedTotpStep"="LastAcceptedTotpStep", "AccessFailedCount"="AccessFailedCount", "LockoutEnd"="LockoutEnd", "IsDisabled"="IsDisabled", "CreatedAt"="CreatedAt", "LastLoginAt"="LastLoginAt" WHERE false;
DELETE FROM admin."AdminUser" WHERE false;
INSERT INTO admin."ApiKey" ("Id","Name","KeyHash","KeyPrefix","Roles","IsDisabled","CreatedAt")
SELECT NULL::uuid,NULL::varchar(100),NULL::varchar(100),NULL::varchar(16),NULL::varchar(200),NULL::boolean,NULL::timestamptz WHERE false;
UPDATE admin."ApiKey" SET "Name"="Name","KeyHash"="KeyHash","KeyPrefix"="KeyPrefix","Roles"="Roles","IsDisabled"="IsDisabled","CreatedAt"="CreatedAt" WHERE false;
DELETE FROM admin."ApiKey" WHERE false;
ROLLBACK;
