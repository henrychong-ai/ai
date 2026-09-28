# Guardrails for Agent-Run Upgrades

How the coding agent keeps a version upgrade scoped and verifiable in production systems. The approval and test-edit precedence rule in SKILL.md wins over anything here.

## Known failure modes

| Risk | Guardrail |
|---|---|
| Invented APIs or options | Take every replacement from the official migration guide, changelog or deprecations page for the exact version, and cite it in the checkpoint report |
| Losing track across many files | Work from the file-by-file change list in the plan; tick items off as they complete |
| Business-logic drift | Compare test results with the pre-upgrade baseline after every phase |
| Scope creep ("while we're here…") | Log the idea as a follow-up item in the report; keep the diff to what the version requires |
| Missed call sites | Grep for every removed API before and after; codemods do not find dynamic or string-built usages |

## Scope

The upgrade diff contains only:
- version files and manifests (`.nvmrc`, `engines`, Dockerfile, pipeline images, `package.json`, lockfile changes produced by the install);
- syntax updates the new version requires (e.g. `assert` → `with`);
- one-for-one API replacements with the same behaviour (e.g. `fs.F_OK` → `fs.constants.F_OK`);
- type annotation and import-path changes the new compiler or types require;
- config changes the new version requires (tsconfig options, framework config keys).

Everything else — refactors, renames, new dependencies not required by the upgrade, logging or error-message changes, formatting sweeps — goes into a separate follow-up.

## Change record

For each non-mechanical change, record in the checkpoint report: file and lines, the version requirement that forced it, the source link, and whether behaviour changes (expected answer: no). Codemod output is recorded per codemod, not per line.

## Stop conditions

Stop, report and wait for the user when:
1. A test fails and the cause is not one of the allowed test edits in SKILL.md.
2. A change would touch payment processing, balance or fee calculation, transaction signing, key handling or other cryptographic operations, authentication or authorisation. Explain the required change and ask for explicit approval; consider having a human implement it.
3. The only fix available is a workaround that weakens security (`--openssl-legacy-provider`, lowering the OpenSSL security level, disabling TLS verification, `--legacy-peer-deps` in production builds).
4. The official documentation does not cover an API you need to replace, or two sources disagree.
5. The scope in the approved plan turns out to be wrong (more packages, a second major, a data migration).

## Approval

Approval comes at the phase checkpoints in SKILL.md. Treat only an explicit go-ahead ("approved", "proceed", "go ahead", "LGTM", "commit it") as approval; ask again if the reply is ambiguous. Silence is never approval.

## Checkpoints

1. **Pre-flight:** clean git state, baseline captured outside the worktree, rollback plan written, scope agreed.
2. **After version files and dependencies:** install clean, native modules rebuilt, type check status known.
3. **After code migration:** all gates green, change record complete, test edits listed.
4. **Before commit:** diff reviewed, CI plan known, user approval.
