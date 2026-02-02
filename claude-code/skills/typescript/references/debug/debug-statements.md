# Debug Statements in Production Code

## The Problem

Unconditional `process.stderr.write('[DEBUG]...')` or `console.log('[DEBUG]...')` statements left in production code can cause critical issues:

1. **Terminal Memory Exhaustion**: During test runs, thousands of debug statements flood the terminal, eventually crashing iTerm or other terminal emulators
2. **Performance Degradation**: Even when not crashing, excessive output slows test execution significantly
3. **CI/CD Timeouts**: Log buffers fill, causing pipeline failures or excessive log storage costs
4. **Silent Production Noise**: Debug output in production logs obscures real errors

## Real-World Case: mcp-neo4j-knowledge-graph v1.8.2

### Symptoms
- iTerm memory usage spiking during `npm test`
- Tests taking 10+ seconds instead of ~7 seconds
- Terminal becoming unresponsive
- System memory pressure alerts

### Root Cause
30+ unconditional debug statements across production code:

```typescript
// BAD: These run unconditionally
process.stderr.write('[DEBUG] Processing observation...\n');
process.stderr.write(`[DEBUG] Entity: ${JSON.stringify(entity)}\n`);
```

Key files with violations:
- `addObservations.ts` - 9 debug statements
- `callToolHandler.ts` - 21+ debug statements
- `logger.ts` - no log level control

### The Fix

1. **Remove debug statements from production code entirely**

2. **Implement proper logging with levels**:
```typescript
// logger.ts
const LOG_LEVELS = { debug: 0, info: 1, warn: 2, error: 3, silent: 4 };

function getLogLevel(): number {
  // Silent during tests unless explicitly requested
  if (process.env.NODE_ENV === 'test' && !process.env.LOG_LEVEL) {
    return LOG_LEVELS.silent;
  }
  if (process.env.DEBUG) return LOG_LEVELS.debug;
  const level = process.env.LOG_LEVEL?.toLowerCase();
  if (level && level in LOG_LEVELS) {
    return LOG_LEVELS[level as keyof typeof LOG_LEVELS];
  }
  return LOG_LEVELS.warn; // Default to warn
}

export const logger = {
  debug: (msg: string, ...args: any[]) => {
    if (getLogLevel() <= LOG_LEVELS.debug) {
      process.stderr.write(`[DEBUG] ${msg} ${args.join(' ')}\n`);
    }
  },
  // ... info, warn, error methods
};
```

3. **Configure test environment**:
```typescript
// vitest.config.ts
export default defineConfig({
  test: {
    env: { NODE_ENV: 'test' },
    // ...
  },
});
```

## Prevention Patterns

### DO: Use Conditional Logging
```typescript
// Logger respects LOG_LEVEL and NODE_ENV
logger.debug('Processing entity', entityName);
```

### DO: Use Debugger Instead
```typescript
// Only runs when debugger attached
debugger;
// Or conditional debugger
if (process.env.DEBUG_HANDLER) debugger;
```

### DON'T: Unconditional stderr/console
```typescript
// These ALWAYS run, even during tests
process.stderr.write('[DEBUG] ...\n');  // BAD
console.log('[DEBUG] ...');              // BAD
```

### DON'T: Forget to Remove Temp Debug Code
```typescript
// This often gets committed accidentally
console.log('=== DEBUG ===', data);  // BAD
```

## Quick Detection

Find debug statements in a codebase:
```bash
# Find process.stderr.write debug statements
grep -r "process\.stderr\.write.*DEBUG" src/

# Find console debug statements
grep -r "console\.log.*DEBUG\|console\.debug" src/

# Find any hardcoded debug markers
grep -rn "\[DEBUG\]" src/
```

## Related Patterns

- **Environment-Based Configuration**: Always use env vars for debug flags
- **Log Level Control**: Implement LOG_LEVEL with silent default during tests
- **Test Isolation**: Tests should have minimal stdout/stderr side effects
- **Pre-commit Hooks**: Add grep patterns to block debug statements

## Reference

- **KG Entity**: "MCP KG Test Memory Issue Fix"
- **Version**: mcp-neo4j-knowledge-graph v1.8.2 (2025-12-22)
- **Severity**: P0 - caused terminal crashes
