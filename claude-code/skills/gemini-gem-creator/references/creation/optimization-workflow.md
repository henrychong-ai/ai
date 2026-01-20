# Optimization Workflow

Process for analyzing and improving existing Gemini gems.

## Phase 1: Analysis

### Request Existing Gem

Start with:
> "Share your current gem instructions so I can analyze them and suggest improvements."

### Parsing Process

1. **Identify Components**: Locate PERSONA, TASK, CONTEXT, FORMAT sections (or lack thereof)
2. **Extract Content**: Parse each component's content
3. **Assess Structure**: Determine if 4-component framework properly implemented
4. **Note Completeness**: Identify missing components or insufficient detail

### Component Boundaries

- **PERSONA**: Usually first section, defines role and expertise
- **TASK**: Describes what gem does, actions it performs
- **CONTEXT**: Background information and domain knowledge
- **FORMAT**: Output structure and requirements

### Parsing Challenges

- Gems without explicit component labels → Infer component boundaries
- Mixed components → Separate into proper structure
- Missing components → Flag for addition
- Insufficient detail → Identify gaps

---

## Phase 2: Assessment

### Apply 5-Quality-Test Framework

Run each test against existing gem:

**Test 1: Specificity Test**
- Evaluate: Are instructions clear and unambiguous?
- Pass: Instructions leave no room for interpretation
- Fail: Vague terms, unclear actions, ambiguous requirements
- Findings: Document specific vague elements

**Test 2: Consistency Test**
- Evaluate: Would multiple uses produce consistent outputs?
- Pass: Format and standards ensure predictable results
- Fail: Insufficient structure or conflicting guidelines
- Findings: Note inconsistency sources

**Test 3: Differentiation Test**
- Evaluate: Is this noticeably different from generic Gemini?
- Pass: Specialized expertise and domain knowledge evident
- Fail: Generic capabilities, no domain specialization
- Findings: Identify where differentiation lacking

**Test 4: Usability Test**
- Evaluate: Are there clear, concrete use cases?
- Pass: Obvious when and why to use this gem
- Fail: Unclear application or theoretical purpose
- Findings: Document usability gaps

**Test 5: Completeness Test**
- Evaluate: Can gem operate standalone?
- Pass: All necessary context and requirements included
- Fail: Missing critical information or dependencies
- Findings: List missing elements

### Assessment Report

```markdown
### Current State Assessment

**Test Results:**
- Specificity Test: [PASS/FAIL - findings]
- Consistency Test: [PASS/FAIL - findings]
- Differentiation Test: [PASS/FAIL - findings]
- Usability Test: [PASS/FAIL - findings]
- Completeness Test: [PASS/FAIL - findings]

**Component Analysis:**
PERSONA: [Present/Absent - quality assessment]
TASK: [Present/Absent - quality assessment]
CONTEXT: [Present/Absent - quality assessment]
FORMAT: [Present/Absent - quality assessment]

**Priority Improvements:**
1. [Highest priority fix with component affected]
2. [Second priority fix with component affected]
3. [Third priority fix with component affected]
```

---

## Phase 3: Refinement

### Targeted Improvements

**For Missing Components:**
Create complete section following construction guidelines based on gem's apparent purpose.

**For Incomplete Components:**
Add missing elements while preserving working content.

**For Vague Components:**
Add specificity through:
- Concrete examples
- Precise terminology
- Clear boundaries
- Specific standards

**For Inconsistent Elements:**
Resolve conflicts by:
- Clarifying conflicting guidelines
- Establishing priority rules
- Removing contradictions
- Adding structure

### Refinement Principles

- Preserve what's working
- Target specific failures
- Maintain coherence across components
- Keep original intent intact
- Improve without complete rewrite

### Example Refinement

**Original (Failing Specificity Test):**
```
TASK: Help with regulatory analysis
```

**Refined (Passing Specificity Test):**
```
TASK:
Analyze regulatory announcements and new regulations to:
1. Identify key regulatory changes and their effective dates
2. Assess direct impact on company operations
3. Determine required compliance actions with deadlines
4. Evaluate strategic implications
5. Recommend implementation approach with timeline

Focus on regulations affecting digital securities and VASP operations.
```

### Presentation

> "Here's the optimized gem with improvements addressing the failing tests:"

```
---BEGIN OPTIMIZED GEM INSTRUCTIONS---

[Complete refined instructions]

---END OPTIMIZED GEM INSTRUCTIONS---
```

---

## Phase 4: Validation

### Re-Run Quality Tests

Apply 5-quality-test framework to refined gem:

**Verification Checklist:**
- [ ] Specificity Test now passes (or improved)
- [ ] Consistency Test now passes (or improved)
- [ ] Differentiation Test now passes (or improved)
- [ ] Usability Test now passes (or improved)
- [ ] Completeness Test now passes (or improved)

### Before/After Comparison

```markdown
### Optimization Results

**Before:**
- Specificity Test: FAIL
- Consistency Test: FAIL
- Differentiation Test: PASS
- Usability Test: PASS
- Completeness Test: FAIL

**After:**
- Specificity Test: PASS ✅ Improved
- Consistency Test: PASS ✅ Improved
- Differentiation Test: PASS ✅ Maintained
- Usability Test: PASS ✅ Maintained
- Completeness Test: PASS ✅ Improved

**Key Improvements:**
1. [Specific improvement 1 with impact]
2. [Specific improvement 2 with impact]
3. [Specific improvement 3 with impact]
```

### Success Criteria

All previously failing tests now pass. If any test still fails, either:
- Iterate refinement further
- Explain why passing may require fundamental restructuring

---

## Edge Cases

### Vague Requirements from User

**Scenario:** User provides unclear requirements for optimization

**Response:**
1. Ask clarifying questions about what's not working
2. Request specific examples of problematic outputs
3. Identify concrete improvement goals before proceeding

### Conflicting Requirements

**Scenario:** User wants contradictory improvements

**Response:**
1. Flag the conflict explicitly
2. Explain why requirements conflict
3. Present options with trade-offs
4. Ask user to prioritize

### Fundamental Restructuring Needed

**Scenario:** Gem is so flawed it needs complete rewrite

**Response:**
1. Acknowledge that targeted optimization isn't sufficient
2. Explain why (e.g., wrong approach entirely)
3. Offer to restart with Create Mode workflow
4. Preserve any salvageable elements
