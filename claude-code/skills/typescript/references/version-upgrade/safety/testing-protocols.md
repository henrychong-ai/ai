# Testing Protocols for Version Upgrades

A version upgrade must not change application behaviour; the tests prove it. Replace `<pm>` with the repo's package manager (table in `../upgrade-protocol.md`). Test framework configuration belongs to the repo and to the testing standards (`../../testing/testing-strategies.md`); this file covers what to run and how to compare.

## Baseline (before any change)

Keep baselines **outside the worktree** so they are never committed:

```bash
BASE="${TMPDIR:-/tmp}/upgrade-baseline-$(basename "$PWD")-$(date +%Y%m%d)"
mkdir -p "$BASE"

node --version            >  "$BASE/versions.txt"
<pm> --version            >> "$BASE/versions.txt"
<pm> exec tsc --version   >> "$BASE/versions.txt"

<pm> exec tsc --noEmit 2>&1 | tee "$BASE/typecheck.txt"
<pm> run lint          2>&1 | tee "$BASE/lint.txt"
<pm> test              2>&1 | tee "$BASE/test.txt"
<pm> run build         2>&1 | tee "$BASE/build.txt"
```

Capture coverage with the repo's own coverage script (e.g. `<pm> exec vitest run --coverage --coverage.reporter=json-summary`) and keep `coverage/coverage-summary.json` in `$BASE`.

## During the upgrade

- After each file or codemod: `<pm> exec tsc --noEmit` and the related tests (`<pm> exec vitest related <files>` or the runner's equivalent).
- After each phase: the full suite and the build.

## Gates

| Gate | Requirement |
|---|---|
| Type check | 0 errors |
| Lint | 0 errors; each new warning explained or fixed |
| Unit tests | 100% pass; coverage ≥ baseline (lines, branches, functions) |
| Integration / E2E (if present) | 100% pass on critical flows |
| Build | Succeeds; artefact inspected |
| Container (if deployed as one) | Image builds on the new base and the service passes its health check |

## Comparing with the baseline

```bash
<pm> test 2>&1 | tee "$BASE/test-after.txt"
diff <(grep -E "passed|failed|skipped" "$BASE/test.txt") <(grep -E "passed|failed|skipped" "$BASE/test-after.txt")
```

For coverage, compare the `total` block of the two `coverage-summary.json` files:

```bash
node -e '
const [a,b]=process.argv.slice(1).map(f=>require(f).total);
for (const k of ["lines","branches","functions","statements"])
  console.log(k, a[k].pct, "->", b[k].pct, b[k].pct < a[k].pct ? "DROP" : "ok");
' "$BASE/coverage-summary.json" "$PWD/coverage/coverage-summary.json"
```

## When a test fails

1. Stop the upgrade work and identify the failing test and the most recent change.
2. Classify it:
   - **Version-driven output change** (error text, deprecation warning, renamed import) — allowed test edit under the `../upgrade-protocol.md` precedence rule; list it in the report.
   - **Behaviour change** — revert the change that caused it and investigate; report before continuing.
   - **Flaky** — prove it by running the test on the baseline commit; report it, do not mask it.
3. Never loosen an assertion, skip a test, or lower a coverage threshold to get green.

## Performance

Required when upgrading a Node major, a framework major, or TypeScript (for compile time).

```bash
/usr/bin/time -p <pm> run build 2>&1 | tail -3 | tee "$BASE/perf-build.txt"
/usr/bin/time -p <pm> test      2>&1 | tail -3 | tee "$BASE/perf-test.txt"
```

| Metric | Acceptable change |
|---|---|
| Build time | ≤ 120% of baseline |
| Test time | ≤ 120% of baseline |
| Service startup | ≤ 110% of baseline |
| Memory (steady state) | ≤ 110% of baseline |

## CI

The pipeline must run the same gates with a frozen lockfile on the new runtime image before merge. Pipeline structure, images and caching: your CI/CD runbook.

## After rollback

If you roll back (`git revert`), reinstall with the frozen lockfile and re-run the gates to confirm the baseline results return:

```bash
<pm> install --frozen-lockfile   # npm: npm ci; Yarn 2+: yarn install --immutable
<pm> test && <pm> run build
```

## Checklist

- Before: all tests passing, baseline captured outside the worktree, CI green.
- During: tests after each change; every test edit justified.
- After: gates green, coverage ≥ baseline, performance within thresholds, CI green on the new runtime.
