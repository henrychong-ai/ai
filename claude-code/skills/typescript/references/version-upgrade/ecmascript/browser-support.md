# Browser Targets

Browser support data changes monthly, so do not keep a hand-written version table. Derive the floor from three inputs and verify it with tools.

## 1. Start from the framework floor

The framework already sets a minimum; your floor cannot be lower.

| Framework | Floor | Source |
|---|---|---|
| Next.js 16 | Chrome 111, Edge 111, Firefox 111, Safari 16.4 | Next.js 16 upgrade guide |
| Vite (current major) | `build.target: 'baseline-widely-available'` = Chrome/Edge 111, Firefox 114, Safari/iOS 16.4 (fixed per Vite major) | https://vite.dev/config/build-options |

Re-read these on every framework major; Vite pins its default to a Baseline date per major.

## 2. Add your audience requirement

Use analytics for real traffic where you have it. Otherwise use a Baseline query:

```
# .browserslistrc — Baseline "widely available" (features interoperable for 30+ months)
baseline widely available
```

Other useful queries: `baseline 2024` (a fixed Baseline year), `defaults` (> 0.5%, last 2 versions, Firefox ESR, not dead). Baseline explained: https://web.dev/baseline.

## 3. Verify what the config resolves to

```bash
npx browserslist                 # the concrete browser versions
npx browserslist --coverage      # global usage share of that set
npx update-browserslist-db@latest   # refresh caniuse-lite first; stale data skews both
```

## 4. Check the features you actually use

For each newer API or syntax the code relies on (`Array.prototype.at`, `toSorted`, `Object.groupBy`, `Set` methods, `Promise.withResolvers`, CSS features), confirm support in the resolved browser set with MDN browser-compat data or https://caniuse.com. Syntax is transpiled down to the build target automatically; APIs are not — they need the floor to include them or a polyfill (`polyfill-strategies.md`).

## 5. Align the pieces

- Bundler build target = the browserslist result (Vite `build.target`, esbuild/SWC targets, Next.js uses browserslist directly) — see `bundler-configuration.md`.
- tsconfig `lib` no higher than the floor supports, plus `"DOM"`.
- Record the floor in the repo's README so product owners know which browsers are supported.

## iOS note

Every browser on iOS uses WebKit, so the Safari version is the floor for all iOS users, including Chrome and Firefox on iOS.
