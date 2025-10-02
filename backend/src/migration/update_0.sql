
CREATE SEQUENCE IF NOT EXISTS user_id_seq INCREMENT 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1;

CREATE TABLE IF NOT EXISTS "public"."user" (
    "id" integer DEFAULT nextval('user_id_seq') NOT NULL,
    "email" character varying(50) NOT NULL,
    "name" character varying(75) NOT NULL,
    "created_at" timestamptz DEFAULT CURRENT_TIMESTAMP NOT NULL,
    "role" character varying(50),
    "last_logged_at" timestamptz,
    "last_realm_roles" text,
    "disabled" boolean,
    CONSTRAINT "user_email_key" UNIQUE ("email"),
    CONSTRAINT "user_pkey" PRIMARY KEY ("id")
) WITH (oids = false);

CREATE INDEX IF NOT EXISTS "user_email" ON "public"."user" USING btree ("email");


CREATE SEQUENCE IF NOT EXISTS usergroup_id_seq INCREMENT 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1;

CREATE TABLE IF NOT EXISTS "public"."usergroup" (
    "id" integer DEFAULT nextval('usergroup_id_seq') NOT NULL,
    "name" character varying(75) NOT NULL,
    "is_default" boolean,
    "description" character varying(75),
    "realm_role" character varying(75),
    "created_at" timestamptz DEFAULT CURRENT_TIMESTAMP NOT NULL,
    "is_assignable" boolean DEFAULT true NOT NULL,
    "is_readonly" boolean,
    CONSTRAINT "usergroup_is_default" UNIQUE ("is_default"),
    CONSTRAINT "usergroup_name" UNIQUE ("name"),
    CONSTRAINT "usergroup_pkey" PRIMARY KEY ("id")
) WITH (oids = false);

INSERT INTO "usergroup" ("name", "description", "realm_role", "is_assignable", "is_readonly")
VALUES
('Admins', 'Application administrators', NULL, false, true),
('Generic', 'Default user group', NULL, false, true);


CREATE INDEX IF NOT EXISTS "usergroup_realm_role" ON "public"."usergroup" USING btree ("realm_role");


CREATE TABLE IF NOT EXISTS "public"."usergroup_user" (
    "usergroup_id" integer NOT NULL,
    "user_id" integer NOT NULL,
    "assigned_at" timestamptz DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT "usergroup_user_usergroup_id_user_id" UNIQUE ("usergroup_id", "user_id"),
    CONSTRAINT "usergroup_user_user_id_fkey" FOREIGN KEY (user_id) REFERENCES "user"(id) ON DELETE CASCADE NOT DEFERRABLE,
    CONSTRAINT "usergroup_user_usergroup_id_fkey" FOREIGN KEY (usergroup_id) REFERENCES usergroup(id) ON DELETE CASCADE NOT DEFERRABLE
) WITH (oids = false);

CREATE TABLE "usergroup_permissions" (
  "name" character varying(64) NOT NULL,
  "usergroup_id" integer NOT NULL,
  "read_only" boolean NOT NULL DEFAULT false,
  "created_at" timestamp DEFAULT CURRENT_TIMESTAMP,
  "updated_at" timestamp DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY ("usergroup_id", "name"),
  FOREIGN KEY ("usergroup_id") REFERENCES "usergroup" ("id") ON DELETE CASCADE
);

INSERT INTO "public". "usergroup_permissions" ("name", "usergroup_id", "read_only")
VALUES
('admin:all', (SELECT "id" FROM "public"."usergroup" WHERE "name" = 'Admins' LIMIT 1), true),
('user:authenticated', (SELECT "id" FROM "public"."usergroup" WHERE "name" = 'Generic' LIMIT 1), true)
ON CONFLICT ("name", "usergroup_id") DO NOTHING;


CREATE TABLE IF NOT EXISTS "public". "config_store" (
    "key" TEXT PRIMARY KEY,
    "value" JSONB,
    "created_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT "key_length" CHECK (char_length("key") > 0)
);

INSERT INTO "public". "config_store" (key, value)
VALUES ('db_version', '0')
SET "value" = EXCLUDED.value,
    "updated_at" = CURRENT_TIMESTAMP;
ON CONFLICT ("key") DO UPDATE
