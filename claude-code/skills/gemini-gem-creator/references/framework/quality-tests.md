# Quality Tests & Validation

The 5-quality-test framework for validating Gemini gems before distribution.

## 5-Quality-Test Framework

### Test 1: Specificity Test

**Question:** Could someone else read these instructions and know exactly what this gem should do?

**Pass Criteria:**
- Clear role description in PERSONA
- Specific numbered actions in TASK
- Defined output structure in FORMAT
- Instructions leave no room for interpretation

**Fail Indicators:**
- Vague phrases like "help with things" or "assist as needed"
- No specific deliverables defined
- Unclear success criteria
- Generic language that could apply to any task

**Assessment:**
```
✅ PASS: Instructions are clear, unambiguous, and specific
❌ FAIL: Contains vague or generic language needing clarification
```

---

### Test 2: Consistency Test

**Question:** If you use this gem 10 times, will you get consistent output structure and quality?

**Pass Criteria:**
- Structured FORMAT section with clear templates
- Specific section headers defined
- Length/style constraints included
- Quality standards established

**Fail Indicators:**
- No FORMAT section or minimal structure
- Variable output descriptions
- Missing quality standards
- No length constraints

**Assessment:**
```
✅ PASS: Format ensures predictable, consistent outputs
❌ FAIL: Outputs would vary significantly across uses
```

---

### Test 3: Differentiation Test

**Question:** Is this gem noticeably different from generic Gemini due to persona and context?

**Pass Criteria:**
- Domain-specific expertise in PERSONA
- Company/industry context in CONTEXT
- Specialized terminology used appropriately
- Unique value proposition evident

**Fail Indicators:**
- Generic "helpful assistant" persona
- No business context
- Could apply to any industry
- No specialized knowledge embedded

**Assessment:**
```
✅ PASS: Clearly specialized with domain expertise
❌ FAIL: Indistinguishable from generic Gemini
```

---

### Test 4: Usability Test

**Question:** Can you describe concrete scenarios where Fusang/Portcullis team would use this?

**Pass Criteria:**
- Clear use cases evident from TASK
- Audience appropriately defined
- Output matches team workflows
- Practical application obvious

**Fail Indicators:**
- Unclear who would use this
- Tasks too abstract to imagine usage
- Output doesn't fit team needs
- Theoretical rather than practical

**Assessment:**
```
✅ PASS: Clear, concrete use cases for target team
❌ FAIL: Unclear application or theoretical purpose
```

---

### Test 5: Completeness Test

**Question:** Does the gem have all information needed to operate standalone?

**Pass Criteria:**
- No external file dependencies (or attached files provided)
- All domain knowledge embedded or attached
- No references to unavailable tools
- Self-contained instructions

**Fail Indicators:**
- References to files user can't access
- Knowledge gaps requiring external sources
- Incomplete CONTEXT section
- Dependencies on CC-specific tools

**Assessment:**
```
✅ PASS: Can function independently without additional context
❌ FAIL: Missing critical information or has unresolved dependencies
```

---

## Pre-Output Validation Checklist

### For All Gems

**Structure:**
- [ ] PERSONA section present with role, expertise, tone, audience
- [ ] TASK section present with objective, numbered actions, success criteria
- [ ] CONTEXT section present with business background, regulations, constraints
- [ ] FORMAT section present with structure, length, style, required elements
- [ ] Clear section delimiters (PERSONA: / TASK: / CONTEXT: / FORMAT:)
- [ ] Natural language throughout

**Quality:**
- [ ] Specificity Test passes
- [ ] Consistency Test passes
- [ ] Differentiation Test passes
- [ ] Usability Test passes
- [ ] Completeness Test passes

### Additional for Converted Gems

**CC Syntax Eliminated:**
- [ ] No YAML frontmatter
- [ ] No tool references (Read, Write, WebSearch, Grep, Glob, Edit, Bash)
- [ ] No MCP references (mcp__kg__, mcp__st__, mcp__perplexity__)
- [ ] No file paths (/Users/..., ~/.claude/..., ~/[vault]/...)
- [ ] No TodoWrite tracking
- [ ] No agent/skill cross-references

**Individual Content Sanitized:**
- [ ] No personal names (e.g., [personal-name], [username])
- [ ] No custom framework triggers (e.g., personal productivity systems)
- [ ] No personal KG entity references
- [ ] No session-specific context

**Business Context Preserved:**
- [ ] Fusang digital securities context (if relevant)
- [ ] Portcullis wealth management context (if relevant)
- [ ] Regulatory frameworks (MAS, SFC, Labuan FSA)
- [ ] Industry terminology intact

---

## Quality Assessment Output Format

```markdown
### Quality Assessment

| Test | Result | Notes |
|------|--------|-------|
| Specificity | [Pass/Needs work] | [Brief explanation] |
| Consistency | [Pass/Needs work] | [Brief explanation] |
| Differentiation | [Pass/Needs work] | [Brief explanation] |
| Usability | [Pass/Needs work] | [Brief explanation] |
| Completeness | [Pass/Needs work] | [Brief explanation] |

**Overall:** [Ready for distribution / Functional with improvements / Needs work]
```

---

## Success Metrics

### Conversion Quality - PASS
- Zero CC-specific syntax remaining
- Zero individual-specific content
- Complete 4-component structure
- All business knowledge preserved
- Team-ready for Google Workspace

### Conversion Quality - NEEDS REVIEW
- Edge cases requiring human judgment
- Complex multi-file skills needing attachment decisions
- Domain knowledge requiring SME validation
- Regulatory content needing compliance review

---

## Quick Validation Flow

Before presenting any gem output:

1. **Syntax scan** - Search for: YAML, tool names, MCP, paths → Must be zero
2. **Personal scan** - Search for: personal names, usernames, personal paths → Must be zero
3. **Structure check** - Verify: PERSONA, TASK, CONTEXT, FORMAT all present
4. **Business check** - Verify: Relevant company context preserved
5. **Quality tests** - Run 5 tests, note any that need work

**Result format:**
- All pass → "Quality: Pass | Team-Sharing Ready: Yes"
- Any fail → "Quality: Needs Review | [specific issues]"
