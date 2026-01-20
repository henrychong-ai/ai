# React 18 to 19 Migration Guide

Focused migration guide for the React 18 → 19 upgrade. This is a relatively minor upgrade with targeted breaking changes.

## Migration Overview

React 19 is a focused release that removes deprecated APIs and adds new features. Most React 18 applications will require minimal changes.

### Impact Assessment

| Category | Severity | Description |
|----------|----------|-------------|
| createFactory | 🔴 HIGH | Removed - must replace |
| defaultProps (functions) | 🟠 MEDIUM | Deprecated - use default params |
| act() location | 🟡 LOW | Moved to react package |
| ref as prop | 🟢 NEW | forwardRef optional |
| use() hook | 🟢 NEW | Read resources in render |

## Phase 1: Pre-Migration Check

### Identify Breaking Changes

```bash
# Check for createFactory (removed)
grep -r "React\.createFactory" src/

# Check for function defaultProps (deprecated)
grep -rn "\.defaultProps\s*=" src/ | grep -v "class.*Component"

# Check for old act import location
grep -r "from 'react-dom/test-utils'" src/ test/

# Check for propTypes runtime (removed in production)
grep -r "\.propTypes\s*=" src/
```

### Quick Impact Assessment

Most React 18 apps need:
1. Replace `defaultProps` on function components → Default parameters
2. Update `act` import → From 'react' instead of 'react-dom/test-utils'
3. Optional: Simplify forwardRef → Regular ref prop

## Phase 2: Breaking Changes

### 1. React.createFactory Removed

**If you use createFactory (rare):**

```javascript
// OLD: React 18
const div = React.createFactory('div');
return div({ className: 'container' }, children);

// NEW: React 19 - Use JSX
return <div className="container">{children}</div>;
```

**Codemod:**
```bash
npx codemod@latest react/19/replace-create-factory
```

### 2. defaultProps Deprecated for Function Components

```javascript
// OLD: React 18
function Button({ size, variant }) {
  return <button className={`btn-${size} btn-${variant}`} />;
}
Button.defaultProps = {
  size: 'medium',
  variant: 'primary'
};

// NEW: React 19 - Default parameters
function Button({ size = 'medium', variant = 'primary' }) {
  return <button className={`btn-${size} btn-${variant}`} />;
}
```

**Class components still support defaultProps** - no change needed for classes.

**TypeScript pattern:**
```typescript
interface ButtonProps {
  size?: 'small' | 'medium' | 'large';
  variant?: 'primary' | 'secondary';
}

function Button({
  size = 'medium',
  variant = 'primary'
}: ButtonProps) {
  return <button className={`btn-${size} btn-${variant}`} />;
}
```

### 3. act() Moved to React Package

```javascript
// OLD: React 18
import { act } from 'react-dom/test-utils';

// NEW: React 19
import { act } from 'react';
```

**Codemod:**
```bash
npx codemod@latest react/19/replace-act-import
```

### 4. propTypes Runtime Removal

PropTypes no longer checked at runtime in production builds. TypeScript is the recommended replacement.

```javascript
// OLD: Runtime prop validation
Button.propTypes = {
  size: PropTypes.oneOf(['small', 'medium', 'large']),
  onClick: PropTypes.func.isRequired
};

// NEW: TypeScript (compile-time)
interface ButtonProps {
  size: 'small' | 'medium' | 'large';
  onClick: () => void;
}
```

## Phase 3: New Features

### 1. ref as Regular Prop

forwardRef is now optional:

```javascript
// OLD: React 18 - Required forwardRef
const Input = forwardRef<HTMLInputElement, Props>((props, ref) => {
  return <input ref={ref} {...props} />;
});

// NEW: React 19 - ref as regular prop
function Input({ ref, ...props }: Props & { ref?: Ref<HTMLInputElement> }) {
  return <input ref={ref} {...props} />;
}
```

**Note:** forwardRef still works - this is just a new option.

### 2. Ref Cleanup Functions

```javascript
// NEW: React 19 - Cleanup function for refs
<div ref={(node) => {
  // Called when mounted
  node.addEventListener('scroll', handleScroll);

  // Cleanup function
  return () => {
    node.removeEventListener('scroll', handleScroll);
  };
}} />
```

### 3. use() Hook

Read promises and context in render:

```javascript
// NEW: React 19
import { use } from 'react';

function Comments({ commentsPromise }) {
  // Suspends until promise resolves
  const comments = use(commentsPromise);
  return comments.map(c => <Comment key={c.id} {...c} />);
}

// With context
function Theme() {
  const theme = use(ThemeContext);
  return <div style={{ color: theme.primary }} />;
}
```

### 4. Actions

Form handling improvements:

```javascript
// NEW: React 19
function Form() {
  async function submitAction(formData) {
    'use server';
    await saveToDatabase(formData);
  }

  return (
    <form action={submitAction}>
      <input name="email" />
      <button type="submit">Submit</button>
    </form>
  );
}
```

### 5. useOptimistic Hook

```javascript
// NEW: React 19
import { useOptimistic } from 'react';

function LikeButton({ likes, onLike }) {
  const [optimisticLikes, addOptimisticLike] = useOptimistic(
    likes,
    (state) => state + 1
  );

  async function handleLike() {
    addOptimisticLike(); // Immediately show +1
    await onLike();      // Server update
  }

  return <button onClick={handleLike}>{optimisticLikes} likes</button>;
}
```

## Phase 4: Migration Steps

### Step 1: Update Dependencies

```bash
pnpm add react@19 react-dom@19
pnpm add -D @types/react@19 @types/react-dom@19
```

### Step 2: Run Codemods

```bash
# All React 19 codemods
npx codemod@latest react/19/replace-act-import
npx codemod@latest react/19/replace-create-factory
```

### Step 3: Fix defaultProps Manually

Find function components with defaultProps:
```bash
grep -rn "\.defaultProps" src/
```

For each, convert to default parameters:
```javascript
// Find pattern like:
function Foo({ bar, baz }) { ... }
Foo.defaultProps = { bar: 1, baz: 'hello' };

// Replace with:
function Foo({ bar = 1, baz = 'hello' }) { ... }
```

### Step 4: Verify Tests

```bash
pnpm test
```

Check for:
- `act` import errors
- Deprecation warnings
- Unexpected behavior changes

## Validation Checklist

### Pre-Commit

- [ ] No `React.createFactory()` usage
- [ ] No function component `defaultProps`
- [ ] `act` imports from 'react'
- [ ] All tests passing
- [ ] No console warnings
- [ ] TypeScript compilation clean

### Post-Deploy

- [ ] Application renders correctly
- [ ] All interactive features working
- [ ] No console errors
- [ ] Performance baseline maintained

## Common Issues

### Error: act is not exported from react-dom/test-utils

**Fix:** Update import to `import { act } from 'react'`

### Warning: defaultProps is deprecated

**Fix:** Convert to default parameters in function signature

### TypeScript: ref type errors

**Fix:** Update @types/react to version 19, adjust ref typing

### Children type error

React 19 requires explicit children in TypeScript:
```typescript
// React 19
interface Props {
  children: ReactNode;  // Must be explicit
}
```

---

**Target Version: React 19.x**

*Smallest migration in this series - focused changes, minimal disruption.*
