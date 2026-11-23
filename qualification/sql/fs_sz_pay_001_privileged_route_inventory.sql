-- FS-SZ-PAY-001: inspect role ownership and all executable functions in protected schema.
-- Run only as isolated qualification database administrator.
\set ON_ERROR_STOP on
SELECT current_database() AS database_name;
SELECT n.nspname AS schema_name, pg_get_userbyid(n.nspowner) AS schema_owner
FROM pg_namespace n WHERE n.nspname='fs_provider';
SELECT c.relname AS relation, c.relkind, pg_get_userbyid(c.relowner) AS owner,
       c.relrowsecurity AS rls_enabled, c.relforcerowsecurity AS force_rls
FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
WHERE n.nspname='fs_provider' ORDER BY c.relname;
SELECT p.proname AS function_name, pg_get_function_identity_arguments(p.oid) AS args,
       pg_get_userbyid(p.proowner) AS owner,
       p.prosecdef AS security_definer,
       p.proconfig AS function_config,
       p.proacl AS grants
FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace
WHERE n.nspname='fs_provider' ORDER BY p.proname;
SELECT r.rolname, r.rolcanlogin, r.rolinherit, r.rolsuper, r.rolcreaterole,
       r.rolcreatedb, r.rolbypassrls
FROM pg_roles r WHERE r.rolname LIKE 'fs_%' ORDER BY r.rolname;
SELECT parent.rolname AS granted_role, member.rolname AS member_role,
       m.admin_option, m.inherit_option, m.set_option
FROM pg_auth_members m JOIN pg_roles parent ON parent.oid=m.roleid
JOIN pg_roles member ON member.oid=m.member
WHERE parent.rolname LIKE 'fs_%' OR member.rolname LIKE 'fs_%'
ORDER BY parent.rolname,member.rolname;
