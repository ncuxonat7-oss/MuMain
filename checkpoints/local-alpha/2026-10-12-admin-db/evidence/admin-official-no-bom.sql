DO $EF$
BEGIN
    IF NOT EXISTS(SELECT 1 FROM pg_namespace WHERE nspname = 'admin') THEN
        CREATE SCHEMA admin;
    END IF;
END $EF$;
CREATE TABLE IF NOT EXISTS admin."__EFMigrationsHistory" (
    "MigrationId" character varying(150) NOT NULL,
    "ProductVersion" character varying(32) NOT NULL,
    CONSTRAINT "PK___EFMigrationsHistory" PRIMARY KEY ("MigrationId")
);

START TRANSACTION;
DO $EF$
BEGIN
    IF NOT EXISTS(SELECT 1 FROM pg_namespace WHERE nspname = 'admin') THEN
        CREATE SCHEMA admin;
    END IF;
END $EF$;

CREATE TABLE admin."AdminUser" (
    "Id" uuid NOT NULL,
    "LoginName" character varying(100) NOT NULL,
    "NormalizedLoginName" character varying(100) NOT NULL,
    "PasswordHash" text NOT NULL,
    "SecurityStamp" text NOT NULL,
    "Roles" character varying(200) NOT NULL,
    "IsTwoFactorEnabled" boolean NOT NULL,
    "ProtectedAuthenticatorKey" text,
    "RecoveryCodeHashes" text,
    "LastAcceptedTotpStep" bigint NOT NULL,
    "AccessFailedCount" integer NOT NULL,
    "LockoutEnd" timestamp with time zone,
    "IsDisabled" boolean NOT NULL,
    "CreatedAt" timestamp with time zone NOT NULL,
    "LastLoginAt" timestamp with time zone,
    CONSTRAINT "PK_AdminUser" PRIMARY KEY ("Id")
);

CREATE UNIQUE INDEX "IX_AdminUser_NormalizedLoginName" ON admin."AdminUser" ("NormalizedLoginName");

INSERT INTO admin."__EFMigrationsHistory" ("MigrationId", "ProductVersion")
VALUES ('20260824171349_InitialAdminPanelUsers', '10.0.2');

COMMIT;

START TRANSACTION;
CREATE TABLE admin."ApiKey" (
    "Id" uuid NOT NULL,
    "Name" character varying(100) NOT NULL,
    "KeyHash" character varying(100) NOT NULL,
    "KeyPrefix" character varying(16) NOT NULL,
    "Roles" character varying(200) NOT NULL,
    "IsDisabled" boolean NOT NULL,
    "CreatedAt" timestamp with time zone NOT NULL,
    CONSTRAINT "PK_ApiKey" PRIMARY KEY ("Id")
);

CREATE UNIQUE INDEX "IX_ApiKey_KeyHash" ON admin."ApiKey" ("KeyHash");

INSERT INTO admin."__EFMigrationsHistory" ("MigrationId", "ProductVersion")
VALUES ('20260829110159_AddApiKeys', '10.0.2');

COMMIT;

