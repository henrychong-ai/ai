# Output Formats

Standard formats for gem deliverables in both Create and Convert modes.

---

## Create Mode Output

### Complete New Gem Package

```markdown
# Gemini Custom Gem: [Gem Name]
*Created for: [Team/Purpose]*
*Domain: [Category]*
*Created: [Date]*

---

## Gem Description (Copy to Gemini "Description" Field)

[1-2 sentences describing what the gem does - this goes in Gemini's description field]

---

## Quality Assessment

| Test | Result | Notes |
|------|--------|-------|
| Specificity | [Pass/Needs work] | [Brief explanation] |
| Consistency | [Pass/Needs work] | [Brief explanation] |
| Differentiation | [Pass/Needs work] | [Brief explanation] |
| Usability | [Pass/Needs work] | [Brief explanation] |
| Completeness | [Pass/Needs work] | [Brief explanation] |

**Overall:** [Ready for distribution / Needs improvements]

---

## Usage Scenarios

1. **[Scenario Name]**
   - Input: "[Example user prompt]"
   - Output: [Brief description of expected output]

2. **[Scenario Name]**
   - Input: "[Example user prompt]"
   - Output: [Brief description of expected output]

3. **[Scenario Name]**
   - Input: "[Example user prompt]"
   - Output: [Brief description of expected output]

---

## Recommended File Attachments

[List any files that should be attached to enhance the gem, or "None needed - all context embedded"]

**Optional Enhancement Attachments:**
- [File type]: For [purpose]

---

## Next Steps

1. Copy the **Gem Description** above to Gemini's "Description" field
2. Copy the **Gem Instructions** below to Gemini's "Instructions" field
3. Name the gem "[Suggested Name]"
4. [Add any attachments if recommended]
5. Test with sample prompts from Usage Scenarios
6. Use Gemini's magic wand feature to expand sections if needed
7. Share with team via Google Workspace

---

## Gem Instructions (Copy to Gemini "Instructions" Field)

**Copy everything between the BEGIN and END markers below:**

---BEGIN GEM INSTRUCTIONS---

PERSONA:
[Complete persona section]

TASK:
[Complete task section with numbered actions]

CONTEXT:
[Complete context section]

FORMAT:
[Complete format section]

---END GEM INSTRUCTIONS---
```

---

## Convert Mode Output

### CC → Gem Conversion Package

```markdown
# Gemini Gem Conversion: [Original Name] → [Gem Name]
*Source: [CC skill/agent path]*
*Domain: [Category]*
*Converted: [Date]*

---

## Conversion Summary

**Source Type:** [Skill / Agent / Command]
**Original File:** [Path]
**Conversion Complexity:** [Simple / Moderate / Complex]

### Elements Removed
- [List of CC-specific elements removed]
- [YAML frontmatter, tool references, MCP calls, etc.]

### Elements Transformed
- [List of transformations applied]
- [Tool patterns → actions, MCP → knowledge, etc.]

### Elements Preserved
- [Business context retained]
- [Domain expertise maintained]

---

## Gem Description (Copy to Gemini "Description" Field)

[1-2 sentences describing what the gem does]

---

## Quality Assessment

| Test | Result | Notes |
|------|--------|-------|
| Specificity | [Pass/Needs work] | [Brief explanation] |
| Consistency | [Pass/Needs work] | [Brief explanation] |
| Differentiation | [Pass/Needs work] | [Brief explanation] |
| Usability | [Pass/Needs work] | [Brief explanation] |
| Completeness | [Pass/Needs work] | [Brief explanation] |

### Conversion Validation

| Check | Status |
|-------|--------|
| CC Syntax Removed | [✅/❌] |
| Personal Content Sanitized | [✅/❌] |
| Business Context Preserved | [✅/❌] |
| 4-Component Structure Complete | [✅/❌] |

**Overall:** [Ready for team sharing / Needs review]

---

## Usage Scenarios

1. **[Scenario Name]**
   - Input: "[Example user prompt]"
   - Output: [Brief description of expected output]

2. **[Scenario Name]**
   - Input: "[Example user prompt]"
   - Output: [Brief description of expected output]

---

## Recommended File Attachments

[List any files that should be attached, or "None needed"]

---

## Next Steps

1. Copy the **Gem Description** to Gemini's "Description" field
2. Copy the **Gem Instructions** to Gemini's "Instructions" field
3. Name the gem "[Suggested Name]"
4. Test with sample prompts
5. Share with team via Google Workspace

---

## Gem Instructions (Copy to Gemini "Instructions" Field)

**Copy everything between the BEGIN and END markers below:**

---BEGIN GEM INSTRUCTIONS---

PERSONA:
[Complete persona section]

TASK:
[Complete task section with numbered actions]

CONTEXT:
[Complete context section]

FORMAT:
[Complete format section]

---END GEM INSTRUCTIONS---
```

---

## Optimization Mode Output

### Gem Optimization Report

```markdown
# Gem Optimization: [Gem Name]
*Optimized: [Date]*

---

## Before/After Comparison

### Test Results

| Test | Before | After | Change |
|------|--------|-------|--------|
| Specificity | [Pass/Fail] | [Pass/Fail] | [✅ Improved / ✅ Maintained / ⚠️ Needs work] |
| Consistency | [Pass/Fail] | [Pass/Fail] | [✅ Improved / ✅ Maintained / ⚠️ Needs work] |
| Differentiation | [Pass/Fail] | [Pass/Fail] | [✅ Improved / ✅ Maintained / ⚠️ Needs work] |
| Usability | [Pass/Fail] | [Pass/Fail] | [✅ Improved / ✅ Maintained / ⚠️ Needs work] |
| Completeness | [Pass/Fail] | [Pass/Fail] | [✅ Improved / ✅ Maintained / ⚠️ Needs work] |

---

## Key Improvements

### 1. [Improvement Category]
**Before:**
```
[Original problematic text]
```

**After:**
```
[Improved text]
```

**Impact:** [Why this improvement matters]

### 2. [Improvement Category]
**Before:**
```
[Original problematic text]
```

**After:**
```
[Improved text]
```

**Impact:** [Why this improvement matters]

---

## Optimized Gem Instructions

**Copy everything between the BEGIN and END markers below:**

---BEGIN OPTIMIZED GEM INSTRUCTIONS---

PERSONA:
[Complete optimized persona section]

TASK:
[Complete optimized task section]

CONTEXT:
[Complete optimized context section]

FORMAT:
[Complete optimized format section]

---END OPTIMIZED GEM INSTRUCTIONS---
```

---

## Quick Output Templates

### Minimal Gem Output (Quick Creation)

```markdown
## [Gem Name]

**Description:** [1-2 sentences]

---BEGIN GEM INSTRUCTIONS---

PERSONA:
[Persona content]

TASK:
[Task content]

CONTEXT:
[Context content]

FORMAT:
[Format content]

---END GEM INSTRUCTIONS---
```

### Quality Assessment Only

```markdown
### Quality Assessment: [Gem Name]

| Test | Result | Notes |
|------|--------|-------|
| Specificity | [Pass/Needs work] | [Explanation] |
| Consistency | [Pass/Needs work] | [Explanation] |
| Differentiation | [Pass/Needs work] | [Explanation] |
| Usability | [Pass/Needs work] | [Explanation] |
| Completeness | [Pass/Needs work] | [Explanation] |

**Verdict:** [Ready / Needs: specific improvements]
```

### Conversion Validation Only

```markdown
### Conversion Validation: [Source] → Gem

| Check | Status | Notes |
|-------|--------|-------|
| YAML Frontmatter | [Removed/N/A] | |
| Tool References | [Removed/N/A] | |
| MCP References | [Removed/N/A] | |
| File Paths | [Removed/N/A] | |
| Personal Names | [Removed/N/A] | |
| Custom Frameworks | [Removed/N/A] | |
| Business Context | [Preserved] | |
| 4-Component Structure | [Complete] | |

**Result:** [Ready for team sharing / Issues found]
```

---

## Output Best Practices

### Always Include
- Clear BEGIN/END markers for copy-paste
- Quality assessment with 5 tests
- At least 2-3 usage scenarios
- Next steps for implementation

### Formatting Standards
- Use markdown tables for structured data
- Use code blocks for gem instructions
- Use clear headers for navigation
- Include dates for version tracking

### Copy-Paste Optimization
- Gem instructions in single continuous block
- No extra whitespace inside markers
- Clear indication of what to copy where
- Gemini field destinations specified
