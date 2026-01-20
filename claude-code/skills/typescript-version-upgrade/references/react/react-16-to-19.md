# React 16 to 19 Migration Guide

**CRITICAL: Major migration spanning 3 major versions. React 16 patterns require significant modernization.**

## Migration Overview

This guide covers the complete migration path from React 16 → 19, including all breaking changes across React 17 and 18.

### Impact Assessment

| Category | Severity | Description |
|----------|----------|-------------|
| JSX Transform | 🔴 HIGH | New JSX runtime required |
| createRoot API | 🔴 HIGH | ReactDOM.render deprecated |
| Concurrent Mode | 🟠 MEDIUM | New rendering behavior |
| Removed APIs | 🟠 MEDIUM | createFactory, defaultProps for functions |
| Event System | 🟡 LOW | Event delegation changes |
| Lifecycle Methods | 🟡 LOW | Legacy lifecycles deprecated |

## Phase 1: Pre-Migration Analysis

### Identify Blocking Patterns

```bash
# Check for deprecated APIs
grep -r "React.createFactory\|ReactDOM.render\|findDOMNode" src/

# Check for legacy lifecycle methods
grep -r "componentWillMount\|componentWillReceiveProps\|componentWillUpdate" src/

# Check for string refs
grep -r "ref=\"\|ref='" src/

# Check for defaultProps on function components
grep -r "\.defaultProps\s*=" src/ | grep -v "class\|Component"
```

### Critical Blockers Checklist

- [ ] No `ReactDOM.render()` - must use `createRoot()`
- [ ] No `React.createFactory()` - use JSX directly
- [ ] No string refs - use `useRef()` or callback refs
- [ ] No `defaultProps` on function components - use default parameters
- [ ] JSX transform updated in build config

## Phase 2: Breaking Changes by Version

### React 17 Breaking Changes

**1. New JSX Transform (CRITICAL)**

React 17 introduced a new JSX transform that doesn't require React import.

```javascript
// OLD: React 16 (required import)
import React from 'react';
function Component() {
  return <div>Hello</div>;
}

// NEW: React 17+ (optional import)
function Component() {
  return <div>Hello</div>;
}
```

**Babel Configuration:**
```json
{
  "presets": [
    ["@babel/preset-react", {
      "runtime": "automatic"
    }]
  ]
}
```

**TypeScript Configuration:**
```json
{
  "compilerOptions": {
    "jsx": "react-jsx"  // Instead of "react"
  }
}
```

**2. Event Delegation Changes**

Events now attach to root DOM node, not document.

```javascript
// Impact: Event.stopPropagation() behavior may differ
// If mixing React with vanilla JS event handlers:
document.addEventListener('click', (e) => {
  // This may fire differently in React 17+
});
```

**3. Event Pooling Removed**

```javascript
// OLD: React 16 (required persist())
function handleChange(e) {
  e.persist(); // Required to use event async
  setTimeout(() => console.log(e.target.value), 100);
}

// NEW: React 17+ (no persist needed)
function handleChange(e) {
  setTimeout(() => console.log(e.target.value), 100);
}
```

**4. Effect Cleanup Timing**

Effects now clean up asynchronously:
```javascript
useEffect(() => {
  // Effect
  return () => {
    // Cleanup runs asynchronously in React 17+
    // May not complete before next render
  };
}, []);
```

### React 18 Breaking Changes

**1. createRoot API (CRITICAL)**

```javascript
// OLD: React 16-17
import ReactDOM from 'react-dom';
ReactDOM.render(<App />, document.getElementById('root'));

// NEW: React 18+
import { createRoot } from 'react-dom/client';
const root = createRoot(document.getElementById('root'));
root.render(<App />);
```

**Hydration:**
```javascript
// OLD: React 16-17
ReactDOM.hydrate(<App />, document.getElementById('root'));

// NEW: React 18+
import { hydrateRoot } from 'react-dom/client';
hydrateRoot(document.getElementById('root'), <App />);
```

**2. Automatic Batching**

React 18 batches all state updates by default:
```javascript
// React 16-17: Two separate renders
setTimeout(() => {
  setCount(c => c + 1);
  setFlag(f => !f);
}, 1000);

// React 18: Single batched render
// Same code, but now batched automatically
```

**If you need synchronous updates:**
```javascript
import { flushSync } from 'react-dom';

flushSync(() => {
  setCount(c => c + 1);
});
// DOM updated here
setFlag(f => !f);
```

**3. Strict Mode Double Rendering**

Strict Mode now mounts/unmounts components twice in development:
```javascript
// Components must be resilient to remounting
useEffect(() => {
  // This will run twice in Strict Mode
  const subscription = subscribe();
  return () => subscription.unsubscribe();
}, []);
```

**4. useId Hook**

New hook for generating stable IDs:
```javascript
// OLD: Manual ID generation
const id = `input-${Math.random()}`;

// NEW: React 18+
import { useId } from 'react';
function Component() {
  const id = useId();
  return <input id={id} />;
}
```

### React 19 Breaking Changes

**1. React.createFactory Removed**

```javascript
// OLD: React 16
const Button = React.createFactory('button');
function Component() {
  return Button({ className: 'btn' }, 'Click me');
}

// NEW: React 19 - Use JSX
function Component() {
  return <button className="btn">Click me</button>;
}
```

**Codemod:**
```bash
npx codemod@latest react/19/replace-reactdom-render
```

**2. defaultProps Deprecated for Function Components**

```javascript
// OLD: React 16
function Button({ color }) {
  return <button style={{ color }}></button>;
}
Button.defaultProps = { color: 'blue' };

// NEW: React 19 - Use default parameters
function Button({ color = 'blue' }) {
  return <button style={{ color }}></button>;
}
```

**Class components still support defaultProps.**

**3. act() Moved to react Package**

```javascript
// OLD: React 16-18
import { act } from 'react-dom/test-utils';

// NEW: React 19
import { act } from 'react';
```

**4. useContext Behavior Change**

```javascript
// React 19: useContext reading from provider above it
// May behave differently with nested contexts
```

**5. ref as a Prop (Function Components)**

```javascript
// NEW: React 19 - ref directly as prop
function Input({ ref, ...props }) {
  return <input ref={ref} {...props} />;
}

// OLD: Required forwardRef
const Input = React.forwardRef((props, ref) => {
  return <input ref={ref} {...props} />;
});
```

**6. Cleanup Functions for Refs**

```javascript
// NEW: React 19
<div ref={(node) => {
  // Setup
  return () => {
    // Cleanup when unmounted
  };
}} />
```

## Phase 3: Removed/Deprecated APIs

### APIs to Replace

| Old API | Status | Replacement |
|---------|--------|-------------|
| `ReactDOM.render()` | Removed 19 | `createRoot().render()` |
| `ReactDOM.hydrate()` | Removed 19 | `hydrateRoot()` |
| `ReactDOM.unmountComponentAtNode()` | Removed 19 | `root.unmount()` |
| `React.createFactory()` | Removed 19 | JSX directly |
| `defaultProps` (function) | Deprecated 19 | Default parameters |
| `propTypes` | Runtime removed | TypeScript |
| String refs | Deprecated 16 | `useRef()` / callback refs |
| `componentWillMount` | Deprecated | `useEffect` |
| `componentWillReceiveProps` | Deprecated | `useEffect` with deps |
| `componentWillUpdate` | Deprecated | `useEffect` with deps |

### Legacy Lifecycle Migration

```javascript
// OLD: Class with legacy lifecycles
class Component extends React.Component {
  componentWillMount() {
    this.fetchData();
  }

  componentWillReceiveProps(nextProps) {
    if (nextProps.id !== this.props.id) {
      this.fetchData(nextProps.id);
    }
  }

  componentWillUpdate(nextProps, nextState) {
    if (nextState.count !== this.state.count) {
      console.log('Count will change');
    }
  }
}

// NEW: Function component with hooks
function Component({ id }) {
  const [data, setData] = useState(null);

  // componentWillMount equivalent
  useEffect(() => {
    fetchData();
  }, []);

  // componentWillReceiveProps equivalent
  useEffect(() => {
    fetchData(id);
  }, [id]);

  // componentWillUpdate equivalent
  const prevCountRef = useRef();
  useEffect(() => {
    if (prevCountRef.current !== count) {
      console.log('Count changed');
    }
    prevCountRef.current = count;
  });
}
```

## Phase 4: Migration Steps

### Step 1: Update Dependencies

```bash
# Update React and ReactDOM
pnpm add react@19 react-dom@19

# Update types
pnpm add -D @types/react@19 @types/react-dom@19
```

### Step 2: Fix createRoot Migration

**Entry point (index.js/index.tsx):**
```javascript
// Before
import React from 'react';
import ReactDOM from 'react-dom';
import App from './App';

ReactDOM.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
  document.getElementById('root')
);

// After
import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import App from './App';

const root = createRoot(document.getElementById('root')!);
root.render(
  <StrictMode>
    <App />
  </StrictMode>
);
```

### Step 3: Update JSX Transform

**tsconfig.json:**
```json
{
  "compilerOptions": {
    "jsx": "react-jsx"
  }
}
```

**Babel:**
```json
{
  "presets": [
    ["@babel/preset-react", { "runtime": "automatic" }]
  ]
}
```

### Step 4: Fix defaultProps

```bash
# Find function components with defaultProps
grep -rn "\.defaultProps" src/ --include="*.tsx" --include="*.jsx"
```

**Convert each:**
```javascript
// Before
function Button({ size, variant }) { ... }
Button.defaultProps = { size: 'medium', variant: 'primary' };

// After
function Button({ size = 'medium', variant = 'primary' }) { ... }
```

### Step 5: Remove createFactory

```bash
# Find createFactory usage
grep -rn "createFactory" src/
```

**Convert to JSX:**
```javascript
// Before
const div = React.createFactory('div');
return div({ className: 'container' }, children);

// After
return <div className="container">{children}</div>;
```

### Step 6: Update Test Utils

```javascript
// Before
import { act } from 'react-dom/test-utils';

// After
import { act } from 'react';
```

### Step 7: Fix String Refs

```javascript
// Before
class Component extends React.Component {
  componentDidMount() {
    this.refs.input.focus();
  }
  render() {
    return <input ref="input" />;
  }
}

// After (function component)
function Component() {
  const inputRef = useRef(null);
  useEffect(() => {
    inputRef.current?.focus();
  }, []);
  return <input ref={inputRef} />;
}
```

## Phase 5: Running Codemods

React provides official codemods for common migrations:

```bash
# Replace ReactDOM.render with createRoot
npx codemod@latest react/19/replace-reactdom-render

# Replace string refs
npx codemod@latest react/19/replace-string-refs

# Replace createFactory
npx codemod@latest react/19/replace-create-factory

# Fix act imports
npx codemod@latest react/19/replace-act-import
```

## Phase 6: TypeScript Considerations

### Updated Type Imports

```typescript
// React 19 namespace changes
import type { ReactNode, ReactElement } from 'react';

// Children prop is no longer implicit
interface Props {
  children: ReactNode;  // Must be explicit
}
```

### Strict Type Changes

```typescript
// React 19: useRef initial value
const ref = useRef<HTMLInputElement>(null);  // null allowed
const ref = useRef<number>(0);  // Or explicit initial value
```

## Validation Checklist

### Pre-Commit

- [ ] No `ReactDOM.render()` calls
- [ ] No `React.createFactory()` usage
- [ ] No `defaultProps` on function components
- [ ] No string refs
- [ ] JSX transform configured correctly
- [ ] All tests passing
- [ ] No console deprecation warnings
- [ ] TypeScript compilation clean

### Post-Deploy

- [ ] Application renders without errors
- [ ] All routes accessible
- [ ] Interactive elements functioning
- [ ] No console errors/warnings
- [ ] Performance baseline maintained

## Common Migration Errors

### Error: ReactDOM.render is no longer supported

```
Warning: ReactDOM.render is no longer supported in React 18.
Use createRoot instead.
```
**Fix:** Update entry point to use `createRoot()`

### Error: Invalid hook call

```
Error: Invalid hook call. Hooks can only be called inside of a function component.
```
**Fix:** Ensure React version matches across all packages, check for duplicate React instances

### Error: Cannot find module 'react-dom/client'

```
Module not found: Can't resolve 'react-dom/client'
```
**Fix:** Update react-dom to version 18+

---

**Target Version: React 19.x**

*This is a major migration. Plan for comprehensive testing and staged rollout.*
