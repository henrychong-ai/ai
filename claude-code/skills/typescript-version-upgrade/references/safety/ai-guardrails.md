# AI Safety Guardrails for Version Upgrades

Critical safety protocols for AI-assisted version migrations in production systems.

## The Problem: AI Refactoring Risks

AI coding assistants face specific challenges during version upgrades:

| Risk Category | Description | Severity |
|---------------|-------------|----------|
| **Hallucination** | Generating non-existent APIs/methods | Critical |
| **Context Limits** | Losing track of changes across files | High |
| **Business Logic Drift** | Accidentally changing behavior | Critical |
| **Over-Optimization** | "Improving" code beyond requirements | Medium |
| **Missing Edge Cases** | Not handling all scenarios | High |

## Mandatory AI Constraints

### Constraint 1: No Business Logic Modifications

**Rule:** Version upgrades must ONLY change version-related code.

**Allowed:**
- Syntax updates (import assert → import with)
- API replacements (same behavior, different method)
- Type annotation updates
- Import path changes

**Prohibited:**
- Algorithm changes
- Conditional logic modifications
- Data transformation alterations
- Error handling behavior changes

### Constraint 2: Explicit Change Justification

Before every code modification, AI must state:

```
CHANGE JUSTIFICATION:
- File: [path]
- Line(s): [numbers]
- Reason: [specific version requirement]
- Source: [official documentation reference]
- Behavior Change: NO
```

### Constraint 3: File-by-File Processing

**Never batch process multiple files simultaneously.**

Protocol:
1. Process ONE file
2. Show diff
3. Explain changes
4. Wait for approval
5. Move to next file

### Constraint 4: Conservative Transformation

When multiple solutions exist, choose the most conservative:

```
Option A: Rewrite entire function (risky)
Option B: Minimal syntax update (conservative) ← CHOOSE THIS
```

### Constraint 5: Test Verification Loop

After every change:
1. Run related tests
2. Verify pass
3. If fail → STOP and report
4. Never "fix" tests to pass

## Prohibited AI Actions

### Hard Prohibitions

1. **NEVER** delete code without explicit instruction
2. **NEVER** rename functions/variables for "clarity"
3. **NEVER** add new dependencies not required by upgrade
4. **NEVER** refactor working code for "improvement"
5. **NEVER** modify test assertions to match new behavior
6. **NEVER** skip failing tests with TODO comments
7. **NEVER** make changes in files outside upgrade scope
8. **NEVER** assume deprecated API behavior

### Soft Prohibitions (Require Explicit Permission)

1. Adding new type annotations (may change behavior)
2. Updating error messages (may affect downstream)
3. Changing logging output (may affect monitoring)
4. Modifying configuration defaults

## Required AI Assertions

### Before Starting
```
PRE-UPGRADE ASSERTION:
I will only modify code necessary for [version X → Y] migration.
I will not change business logic, algorithms, or behavior.
I will stop and ask if I encounter unexpected situations.
```

### During Processing
```
FILE: [path]
CHANGE TYPE: [syntax/api/import/type]
OFFICIAL SOURCE: [link to docs]
BEHAVIOR CHANGE: NO
```

### After Each File
```
FILE COMPLETE: [path]
CHANGES: [count]
TESTS: [pass/fail/none]
PROCEED TO NEXT: [awaiting approval]
```

## Error Recovery Protocol

### When Tests Fail

```
TEST FAILURE DETECTED

Action: STOP
File: [last modified]
Test: [failing test name]
Error: [error message]

DO NOT:
- Modify test to pass
- Make additional code changes
- Assume the change was correct

REQUIRED:
1. Report failure to user
2. Show exact change that may have caused it
3. Await user instruction
```

### When Encountering Unknown APIs

```
UNKNOWN API DETECTED

API: [name]
Context: [where found]

DO NOT:
- Guess the replacement
- Use AI training data assumptions

REQUIRED:
1. Search official documentation
2. If not found, ask user
3. Never proceed with uncertainty
```

### When Scope Unclear

```
SCOPE CLARIFICATION NEEDED

Question: [specific question]
Options: [A, B, C]

WAITING FOR USER INPUT
DO NOT proceed with assumptions
```

## Validation Checkpoints

### Checkpoint 1: Pre-Flight
- [ ] Clean git state
- [ ] Tests passing
- [ ] Backup branch created
- [ ] Scope defined

### Checkpoint 2: Per-File
- [ ] Change justified with source
- [ ] No business logic modified
- [ ] Tests still pass
- [ ] User approved

### Checkpoint 3: Per-Phase
- [ ] All files in phase complete
- [ ] Integration tests pass
- [ ] No new warnings
- [ ] Diff reviewed

### Checkpoint 4: Final
- [ ] All tests pass
- [ ] Build succeeds
- [ ] Coverage unchanged or improved
- [ ] User final approval

## Monitoring AI Behavior

### Warning Signs

| Sign | Risk | Action |
|------|------|--------|
| "Let me improve this..." | High | Stop immediately |
| "I'll also fix..." | High | Reject scope creep |
| "This looks like it could be better..." | Medium | Refocus on upgrade |
| "I noticed an issue..." | Low | Defer to separate task |

### Red Flags (Immediate Stop)

1. AI modifies files not in upgrade scope
2. AI changes test expectations
3. AI adds new features
4. AI removes "unnecessary" code
5. AI suggests "while we're here..."

## Human Oversight Requirements

### Mandatory Review Points

1. **After version file updates** (.nvmrc, package.json)
2. **After each source file modification**
3. **After dependency updates**
4. **Before final commit**
5. **Before push to remote**

### Approval Phrases

User must explicitly say:
- "Approved" or "Approve"
- "Continue" or "Proceed"
- "LGTM" (Looks Good To Me)
- "Commit it"

AI must NOT interpret:
- "Okay" (ambiguous)
- "Sure" (ambiguous)
- Silence (never assume approval)

## Financial Application Specifics

For applications handling money/crypto:

### Extra Constraints

1. **Zero tolerance for behavior changes** in transaction code
2. **Double verification** of any numeric operations
3. **Explicit approval** for any code touching balances
4. **No changes** to cryptographic operations
5. **Freeze** on business-critical paths during upgrade

### Critical Paths (Do Not Touch)

- Payment processing
- Balance calculations
- Transaction signing
- Authentication flows
- Authorization checks

If upgrade requires changes to these areas:
1. STOP
2. Report to user
3. Require explicit written approval
4. Consider manual implementation

---

*Safety first. When in doubt, do less and verify more.*
