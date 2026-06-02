# Common Pitfalls

Seven common mistakes when creating Gemini gems, with fixes.

## 1. Vague Persona

**Pitfall:**
```
PERSONA: You are an expert assistant.
```

**Why it fails:** Generic persona produces generic responses. No differentiation from base Gemini.

**Fix:**
```
PERSONA: You are an Islamic finance compliance officer specializing in sukuk structures, with expertise in AAOIFI standards and Labuan FSA regulations. You communicate with technical precision for compliance professionals while ensuring clarity for non-specialists.
```

**Key elements:**
- Specific role name
- Domain expertise listed
- Communication style defined
- Audience specified

---

## 2. Unclear Task

**Pitfall:**
```
TASK: Help with analysis.
```

**Why it fails:** No specific actions, no success criteria, inconsistent outputs.

**Fix:**
```
TASK: Analyze sukuk structures to assess:
1. Shariah compliance (riba, gharar, halal backing)
2. Regulatory adherence (Labuan FSA, SC Malaysia)
3. Structural risks (SPV, ownership, profit distribution)
4. Documentation completeness

Provide risk ratings (HIGH/MEDIUM/LOW) for each area with supporting rationale.
```

**Key elements:**
- Numbered specific actions
- Clear assessment criteria
- Defined deliverables
- Quality standards included

---

## 3. Missing Context

**Pitfall:**
No CONTEXT section, or:
```
CONTEXT: We do finance stuff.
```

**Why it fails:** Gem lacks domain knowledge to provide relevant responses. Generic outputs that don't fit business needs.

**Fix:**
```
CONTEXT: Fusang operates a Labuan FSA-licensed digital securities exchange with sukuk tokenization, crypto trading, and Vault custody services. Operations must comply with Labuan FSA, Hong Kong SFC, and Singapore MAS. Target audience is compliance professionals and senior executives requiring analysis for regulatory submissions and board reporting.
```

**Key elements:**
- Company operations described
- Regulatory environment specified
- Audience defined
- Use case context provided

---

## 4. Format-Free Output

**Pitfall:**
No FORMAT section, or:
```
FORMAT: Just write something helpful.
```

**Why it fails:** Inconsistent output structure. Users can't predict what they'll get.

**Fix:**
```
FORMAT: Structure all responses as:

**Executive Summary:** 2-3 sentences with key findings

**Analysis:** Detailed examination with section headers

**Key Issues:** Bulleted list with risk levels (HIGH/MEDIUM/LOW)

**Recommendations:** Numbered actionable steps

**Next Steps:** Timeline and responsible parties

Use professional tone. Maximum 800 words unless detailed analysis requested.
```

**Key elements:**
- Specific section structure
- Length constraints
- Style guidelines
- Required elements listed

---

## 5. Everything Gem

**Pitfall:**
Single gem trying to do too many unrelated things:
```
TASK: Help with compliance, write marketing content, review contracts, analyze financials, create presentations, and answer HR questions.
```

**Why it fails:** Jack of all trades, master of none. Diluted expertise, inconsistent quality.

**Fix:**
Create specialized gems:
- Compliance Review Gem
- Content Marketing Gem
- Contract Analysis Gem
- Financial Analysis Gem

Each gem focused on one domain with deep expertise.

**Rule of thumb:** If TASK has more than 5-6 related actions, consider splitting into multiple gems.

---

## 6. One-and-Done Approach

**Pitfall:**
Creating gem and never refining based on actual use.

**Why it fails:** Real-world usage reveals gaps that weren't apparent during creation.

**Fix:**
Iterative improvement process:
1. Create initial gem with core 4 components
2. Test on 3-5 real tasks
3. Gather feedback from team members
4. Identify common issues:
   - "Output too long" → Add length constraint to FORMAT
   - "Missing context" → Expand CONTEXT section
   - "Wrong tone" → Refine PERSONA communication style
5. Update gem and re-test
6. Repeat until consistent quality

**Best practice:** Schedule gem review after 2 weeks of team use.

---

## 7. Generic Instead of Specialized

**Pitfall:**
```
PERSONA: You are a helpful assistant that knows about finance.
```

**Why it fails:** No competitive advantage over base Gemini. Doesn't leverage company-specific knowledge.

**Fix:**
```
PERSONA: You are a digital securities compliance analyst specializing in tokenized sukuk under Labuan FSA regulations, with expertise in AAOIFI accounting standards, IFSB prudential requirements, and cross-border Islamic finance structures. You communicate with technical precision suitable for regulatory submissions while providing actionable guidance for business teams.
```

**Specialization sources:**
- Company-specific operations (Fusang exchange, Portcullis trusts)
- Regulatory expertise (specific jurisdictions, standards)
- Industry terminology (sukuk, tokenization, UHNW families)
- Output formats (regulatory submissions, board reports)

---

## Quick Reference: Pitfall Detection

| Symptom | Likely Pitfall | Quick Fix |
|---------|----------------|-----------|
| Generic responses | Vague Persona | Add specific role + expertise |
| Inconsistent outputs | Unclear Task or Format-Free | Add numbered actions + structure |
| Missing context | Missing Context | Add company/regulatory details |
| Too broad | Everything Gem | Split into specialized gems |
| Quality varies | One-and-Done | Test and iterate |
| No differentiation | Generic persona | Add domain specialization |

---

## Prevention Checklist

Before finalizing any gem:

- [ ] PERSONA has specific role, not just "assistant"
- [ ] TASK has numbered actions, not just "help with"
- [ ] CONTEXT includes company and regulatory details
- [ ] FORMAT specifies output structure
- [ ] Gem focuses on one domain (not everything)
- [ ] Planned iteration based on real usage
