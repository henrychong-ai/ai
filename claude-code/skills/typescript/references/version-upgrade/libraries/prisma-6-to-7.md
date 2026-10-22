# Prisma ORM 6 → 7

Recommended: product apps run **Prisma 7**, pinned as `prisma@^7` and `@prisma/client@^7` (`../../tech-stack/version-policy.md`); the target shape (generator, `prisma.config.ts`, driver adapter) is `../../tech-stack/orm.md` → Prisma 7. This guide covers moving an existing Prisma 6 app there.

Primary source: Prisma's "Upgrade to Prisma ORM 7" guide, https://www.prisma.io/docs/guides/upgrade-prisma-orm/v7 (checked 2026-10-22). Prisma publishes no codemod for this hop; the guide links a migration prompt for AI agents instead. Read the guide for the installed 7.x minor before starting: adapter and config details change between minors.

**Install the 7 line explicitly.** npm `prisma@latest` is an 8.0 release candidate (checked 2026-10-22), so a bare `add prisma` installs a pre-release:

```bash
pnpm add @prisma/client@^7 @prisma/adapter-pg@^7      # or @prisma/adapter-mssql@^7 for SQL Server
pnpm add -D prisma@^7
```

Keep `prisma`, `@prisma/client` and the adapter on the same version.

## Requirements

| Item | Prisma 7 |
|---|---|
| Node.js | 20.19.0 or later per the guide; `prisma@7` `engines` is `^20.19 \|\| ^22.12 \|\| >=24.0` (npm, checked 2026-10-22). The recommended runtimes (Node 24/26) satisfy it |
| TypeScript | 5.4.0 or later (5.9 recommended); the recommended `~6.0` satisfies it |
| Module format | Prisma ships as ESM. The guide sets `"type": "module"` and an ES module tsconfig; the `../../coding-standards/tooling.md` Node tsconfig (`NodeNext`) works with the `.js` import extensions shown in `orm.md` |
| MongoDB | Not supported by Prisma 7; stay on 6 |

## Breaking changes

| Area | Prisma 6 | Prisma 7 |
|---|---|---|
| Generator | `prisma-client-js`, generated into `node_modules` | `prisma-client`; `output` is required and imports change to the generated path |
| Connection | Built-in engines; `datasources` / `datasourceUrl` options | A driver adapter for every database (`@prisma/adapter-pg`, `@prisma/adapter-mssql`): `new PrismaClient({ adapter })` |
| Datasource URLs | `url`, `directUrl`, `shadowDatabaseUrl` in `schema.prisma` | Deprecated there; the CLI reads `prisma.config.ts`. A `directUrl` used for migrations becomes the config's `url` |
| `.env` loading | Loaded automatically | Not loaded; load it yourself (e.g. `dotenv`) for the CLI and the app |
| Middleware | `prisma.$use` | Removed; use Client Extensions |
| Metrics preview | Available | Removed |
| Seeding | Ran after `migrate dev` / `migrate reset` | Run `prisma db seed` explicitly |
| CLI | `--skip-generate`, `--skip-seed`; `migrate dev` and `db push` ran `generate` | Flags removed; run `prisma generate` yourself. `db execute --schema/--url` and several `migrate diff` URL options removed (use `--from-config-datasource` / `--to-config-datasource`) |
| Environment variables | `PRISMA_CLIENT_ENGINE_TYPE`, `PRISMA_QUERY_ENGINE_LIBRARY` and others | Removed |
| Accelerate | `prisma+postgres://accelerate.prisma-data.net` URLs | Standalone Accelerate URLs retire on 2026-12-01; never pass them to a driver adapter |

## Behaviour changes to test

- **TLS:** invalid certificates are no longer ignored; a database with a self-signed or private-CA certificate fails with `P1010`. Configure the CA in the adapter's TLS options. Setting `rejectUnauthorized: false` disables verification and needs an explicit, recorded security decision.
- **Connection pools:** defaults now come from the Node driver, not Prisma. `pg` has no connection timeout by default (Prisma 6 had 5 s). On SQL Server the `mssql` defaults are a 15 s connection timeout (6: 5 s) and a 30 s idle timeout (6: 300 s) (https://www.prisma.io/docs/orm/overview/databases/sql-server, checked 2026-10-22). Set pool size and timeouts explicitly in the adapter so behaviour under load does not change silently.
- **Build and deploy:** `prisma generate` must run in the build (Dockerfile and CI) because `migrate dev` and `db push` no longer trigger it, and the generated client now lives in the source tree's `output` path. Decide whether that path is committed or generated; add it to `.gitignore` if generated.
- **Seeds and test fixtures** that relied on automatic seeding after `migrate reset` now need an explicit `prisma db seed` step.

## Migration steps

1. Baseline on Prisma 6 (upgrade protocol Phase 1), including `prisma migrate status` against a non-production database.
2. Install the 7 line with explicit ranges (above) and the adapter for the database.
3. Change the generator to `prisma-client` with an `output`, then update every `@prisma/client` import to the generated path.
4. Add `prisma.config.ts` (shape: `orm.md`), move the datasource URLs out of `schema.prisma`, and load `.env` explicitly where the CLI or app relied on it.
5. Construct the client with the adapter; set pool size, timeouts and TLS in the adapter.
6. Replace `$use` middleware with Client Extensions and remove metrics usage.
7. Update scripts, Dockerfiles and pipelines: explicit `prisma generate`, explicit `prisma db seed`, removed CLI flags.
8. Run `prisma migrate diff` (config-datasource form) against a staging database to confirm the schema produces no migration: the upgrade must not change the database.
9. Run the validation gates, then an integration run against a staging database on the real TLS and pool settings.

## Checklist

- [ ] `prisma`, `@prisma/client` and the adapter on the same `^7` version; no unpinned install
- [ ] Generator `prisma-client` with `output`; imports updated
- [ ] `prisma.config.ts` holds the URLs; `.env` loading explicit
- [ ] Adapter configured with explicit pool size, timeouts and TLS (no silent `rejectUnauthorized: false`)
- [ ] No `$use` middleware, metrics, removed CLI flags or removed environment variables
- [ ] Build runs `prisma generate`; seeds run explicitly
- [ ] `migrate diff` shows no schema change; staging integration run passes
- [ ] Not on Prisma 8: decide on 8 after its GA (`../../tech-stack/version-policy.md`)
