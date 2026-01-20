# React 17 to 19 Migration Guide

Migration guide for upgrading from React 17 to React 19, covering React 18 intermediate changes.

## Migration Overview

React 17 served as a "stepping stone" release with minimal breaking changes. The main work is adapting to React 18 concurrent features and React 19 API removals.

### Impact Assessment

| Category | Severity | Description |
|----------|----------|-------------|
| createRoot API | 🔴 HIGH | ReactDOM.render deprecated |
| Concurrent Features | 🟠 MEDIUM | Automatic batching behavior |
| Removed APIs | 🟠 MEDIUM | createFactory, function defaultProps |
| act() Location | 🟡 LOW | Moved to react package |
| Strict Mode | 🟡 LOW | Double-invoke effects |

## Phase 1: Pre-Migration Analysis

### Check for Blocking Patterns

```bash
# Check for ReactDOM.render
grep -r "ReactDOM\.render\|ReactDOM\.hydrate" src/

# Check for removed APIs
grep -r "React\.createFactory\|\.defaultProps\s*=" src/

# Check for old act import
grep -r "from 'react-dom/test-utils'" src/
```

## Phase 2: Breaking Changes

### React 18 Changes (from 17)

**1. createRoot API (CRITICAL)**

```javascript
// OLD: React 17
import ReactDOM from 'react-dom';
ReactDOM.render(<App />, document.getElementById('root'));

// NEW: React 18+
import { createRoot } from 'react-dom/client';
const root = createRoot(document.getElementById('root'));
root.render(<App />);
```

**Hydration for SSR:**
```javascript
// OLD: React 17
ReactDOM.hydrate(<App />, document.getElementById('root'));

// NEW: React 18+
import { hydrateRoot } from 'react-dom/client';
hydrateRoot(document.getElementById('root'), <App />);
```

**2. Automatic Batching**

React 18 batches all state updates, including those in promises, timeouts, and event handlers:

```javascript
// React 17: Multiple renders
setTimeout(() => {
  setCount(c => c + 1);  // Render 1
  setFlag(f => !f);       // Render 2
}, 1000);

// React 18: Single batched render
// Same code, automatically batched
```

**Opt-out of batching:**
```javascript
import { flushSync } from 'react-dom';

flushSync(() => {
  setCount(c => c + 1);
});
// DOM is updated synchronously here
```

**3. Strict Mode Behavior**

Development-only double invocation:
```javascript
// Effects run twice in development
useEffect(() => {
  const subscription = subscribe();
  return () => subscription.unsubscribe();
}, []);
```

Ensure effects are idempotent and clean up properly.

**4. New Concurrent Features**

Optional concurrent features available:
- `useTransition()` - Mark updates as non-urgent
- `useDeferredValue()` - Defer expensive re-renders
- `<Suspense>` improvements - Better loading states

### React 19 Changes (from 18)

**1. createFactory Removed**

```javascript
// OLD: React 17
const Button = React.createFactory('button');
return Button({ onClick: handleClick }, 'Click');

// NEW: React 19
return <button onClick={handleClick}>Click</button>;
```

**2. Function Component defaultProps Deprecated**

```javascript
// OLD: React 17
function Button({ color }) { ... }
Button.defaultProps = { color: 'blue' };

// NEW: React 19
function Button({ color = 'blue' }) { ... }
```

**3. act() Moved**

```javascript
// OLD: React 17-18
import { act } from 'react-dom/test-utils';

// NEW: React 19
import { act } from 'react';
```

**4. ref as Regular Prop**

```javascript
// NEW: React 19 - No forwardRef needed
function Input({ ref, ...props }) {
  return <input ref={ref} {...props} />;
}

// OLD: Required forwardRef wrapper
const Input = forwardRef((props, ref) => {
  return <input ref={ref} {...props} />;
});
```

## Phase 3: Migration Steps

### Step 1: Update Dependencies

```bash
pnpm add react@19 react-dom@19
pnpm add -D @types/react@19 @types/react-dom@19
```

### Step 2: Update Entry Point

```javascript
// src/index.tsx or src/main.tsx
import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import App from './App';

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>
);
```

### Step 3: Fix defaultProps

Find and replace:
```bash
grep -rn "\.defaultProps" src/
```

Convert each function component:
```javascript
// Before
function Card({ padding, shadow }) { ... }
Card.defaultProps = { padding: 16, shadow: true };

// After
function Card({ padding = 16, shadow = true }) { ... }
```

### Step 4: Update Test Imports

```javascript
// Before
import { act } from 'react-dom/test-utils';
import { render } from '@testing-library/react';

// After
import { act } from 'react';
import { render } from '@testing-library/react';
```

### Step 5: Run Codemods

```bash
# Replace ReactDOM.render
npx codemod@latest react/19/replace-reactdom-render

# Replace act imports
npx codemod@latest react/19/replace-act-import
```

## Phase 4: Concurrent Feature Adoption

### Optional: useTransition for Non-Urgent Updates

```javascript
import { useTransition } from 'react';

function SearchResults({ query }) {
  const [isPending, startTransition] = useTransition();
  const [results, setResults] = useState([]);

  function handleSearch(input) {
    startTransition(() => {
      setResults(search(input));  // Non-urgent
    });
  }

  return isPending ? <Spinner /> : <ResultsList results={results} />;
}
```

### Optional: useDeferredValue

```javascript
import { useDeferredValue } from 'react';

function List({ items }) {
  const deferredItems = useDeferredValue(items);

  return (
    <ul>
      {deferredItems.map(item => <li key={item.id}>{item.name}</li>)}
    </ul>
  );
}
```

## Validation Checklist

### Pre-Commit

- [ ] Entry point uses `createRoot()`
- [ ] No `ReactDOM.render()` calls
- [ ] No function component `defaultProps`
- [ ] Test imports use `react` for `act`
- [ ] All tests passing
- [ ] No deprecation warnings

### Post-Deploy

- [ ] Application renders correctly
- [ ] No console errors
- [ ] Interactive features working
- [ ] SSR hydration correct (if applicable)

## Common Issues

### Warning: ReactDOM.render is no longer supported

**Fix:** Update to createRoot API

### Strict Mode causing double API calls

**Fix:** Ensure effects clean up properly - this is expected behavior in development

### Types error with ref prop

**Fix:** Update @types/react to version 19

---

**Target Version: React 19.x**
