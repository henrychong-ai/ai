# React 16 / 17 / 18 → 19

Primary sources: https://react.dev/blog/2024/04/25/react-19-upgrade-guide and, for pre-18 code, https://react.dev/blog/2022/03/08/react-18-upgrade-guide. Check the current React version with `npm view react version` (19.3.0 on 2026-09-28).

Start at the section for your version and work down. For a React 16 app, upgrade to 18.3 first (it warns about everything 19 removes), fix the warnings, then move to 19.

## Codemods (verified names)

```bash
npx codemod@latest react/19/migration-recipe          # runs the five below
npx codemod@latest react/19/replace-reactdom-render   # render/hydrate/unmount → createRoot/hydrateRoot
npx codemod@latest react/19/replace-string-ref        # string refs → callback refs
npx codemod@latest react/19/replace-act-import        # act from react-dom/test-utils → react
npx codemod@latest react/19/replace-use-form-state    # useFormState → useActionState
npx codemod@latest react/prop-types-typescript        # propTypes → TypeScript props
npx types-react-codemod@latest preset-19 ./src        # @types/react 19 type changes
```

There is **no** codemod for `createFactory`; replace it by hand with JSX. Commit before running codemods and review each diff.

## From 16

- **New JSX transform** (React 17): `"jsx": "react-jsx"` in tsconfig, or `@babel/preset-react` with `runtime: "automatic"`. `import React` is no longer needed for JSX.
- **Event delegation** moved from `document` to the root container (17): code mixing React and `document`-level listeners with `stopPropagation()` may behave differently.
- **Event pooling removed** (17): `e.persist()` is a no-op.
- **Effect cleanup** runs asynchronously (17).
- **Legacy lifecycles** (`componentWillMount`, `componentWillReceiveProps`, `componentWillUpdate`) are deprecated: convert to `componentDidMount`/`componentDidUpdate`/`getDerivedStateFromProps`, or to hooks when rewriting the component.

## From 17

- **`createRoot` / `hydrateRoot`** (18) replace `ReactDOM.render` / `ReactDOM.hydrate`:
  ```tsx
  import { StrictMode } from 'react';
  import { createRoot } from 'react-dom/client';
  createRoot(document.getElementById('root')!).render(<StrictMode><App /></StrictMode>);
  ```
- **Automatic batching** (18): updates in timeouts, promises and native handlers are batched; use `flushSync` where you need an immediate DOM update.
- **Strict Mode** double-invokes effects in development (18): effects must clean up and be idempotent.
- **`@types/react` 18** removed implicit `children` from `React.FC` / component props: declare `children: React.ReactNode` where used.
- New optional APIs: `useId`, `useTransition`, `useDeferredValue`, `useSyncExternalStore`.

## From 18 (the React 19 removals)

| Removed in 19 | Replacement |
|---|---|
| `ReactDOM.render`, `ReactDOM.hydrate`, `unmountComponentAtNode` | `createRoot().render`, `hydrateRoot`, `root.unmount()` |
| `ReactDOM.findDOMNode` | A DOM ref |
| `React.createFactory` | JSX (manual) |
| String refs | Callback refs or `useRef` |
| `defaultProps` on **function** components — silently ignored | ES default parameters (class components keep `defaultProps`) |
| `propTypes` checks — silently ignored | TypeScript props |
| Legacy context (`contextTypes`, `getChildContext`) | `createContext` |
| `react-dom/test-utils` (all but `act`) | `act` from `react`; Testing Library for the rest |
| `react-test-renderer/shallow` | Install `react-shallow-renderer` directly, or move to Testing Library |

**Silent behaviour risk:** removed `defaultProps` and `propTypes` do not throw — components just receive `undefined` where a default used to apply. Grep for them before upgrading and cover each component with a test:

```bash
grep -rnE "\.defaultProps\s*=|\.propTypes\s*=|createFactory|findDOMNode|ReactDOM\.(render|hydrate)|unmountComponentAtNode|react-dom/test-utils" src/
```

### TypeScript changes (`@types/react@19`)

- `useRef()` requires an argument: `useRef<HTMLInputElement>(null)`, `useRef<number | undefined>(undefined)`.
- Ref callbacks cannot implicitly return a value: `ref={el => { node = el; }}` (a returned function is now a cleanup).
- `ReactElement['props']` defaults to `unknown`; the global `JSX` namespace moves under `declare module 'react'`.
- `useReducer` takes no reducer type argument — rely on inference.

### New in 19 (adopt deliberately, not as part of the upgrade)

`ref` as a regular prop (`forwardRef` optional), ref cleanup functions, `use()`, Actions with `useActionState`/`useFormStatus`/`useOptimistic`, document metadata tags, and in 19.2 `Activity` and `useEffectEvent`.

## Steps

```bash
<pm> add react@^19 react-dom@^19
<pm> add -D @types/react@^19 @types/react-dom@^19
npx codemod@latest react/19/migration-recipe
npx types-react-codemod@latest preset-19 ./src
```

Then fix the removals the codemods do not cover (`createFactory`, `defaultProps`, `findDOMNode`, legacy context), and check every library that peers on `react` (`<pm> install` peer warnings) — UI kits and form libraries often need a major bump for 19.

## Validation

- Type check, lint, unit tests, build.
- No React warnings in the browser console in development.
- Every component that used `defaultProps`/`propTypes` covered by a test asserting its defaults.
- SSR/hydration: no hydration warnings on the main routes.
- For Next.js apps, React is upgraded with Next — see `../frameworks/nextjs-migrations.md`.
