# Transformation Mapping

Systematic mapping from Claude Code instruction patterns to Gemini gem components.

## Core Mapping: CC → Gem Components

### YAML Frontmatter → PERSONA + Description Field

| CC Element | Gem Target | Transformation |
|------------|------------|----------------|
| `name:` | Gem Name | **Title-cased mirror of the skill name** (`compliance-review` → "Compliance Review", `contract-analyzer` → "Contract Analyzer") — never invent a descriptive title; one skill → multiple gems uses "Name — Suffix" |
| `description:` | PERSONA + Description field | Extract role and purpose; descriptive text lives here, not in the name |
| `model:` | N/A | Remove (Gemini uses fixed model) |
| `allowed-tools:` | TASK | Convert capabilities to actions |
| `skills:` | CONTEXT | Inline relevant knowledge |

**Example:**
```yaml
# CC Frontmatter
---
name: compliance-analyzer
description: Analyzes regulatory compliance for payments operations
model: opus
allowed-tools: Read, Grep, WebSearch
skills: compliance-review
---

# Gem Mapping
Gem Name: "Compliance Analyzer"
PERSONA: You are a regulatory compliance analyst specializing in payments regulation...
Description field: "Regulatory compliance analyzer for payments operations"
```

---

### Agent Identity → PERSONA

| CC Pattern | PERSONA Element |
|------------|-----------------|
| Agent name/title | Role definition |
| Domain specialization | Expertise areas |
| Communication style | Tone and audience |
| Knowledge references | Embedded expertise |

**Transformation:**
```markdown
# CC Agent Identity
You are the compliance-review agent, a payments-regulation specialist with access to mcp__memory__ for regulatory lookups...

# Gem PERSONA
You are a regulatory compliance analyst specializing in payments regulation for online payment platforms. You have deep expertise in payment-services licensing, AML/KYC requirements, and operational compliance. You communicate with technical precision suitable for compliance officers and senior executives.
```

---

### Tool Usage Patterns → TASK Actions

| CC Tool Pattern | TASK Transformation |
|-----------------|---------------------|
| `Read file` | "Examine/Review/Analyze [content type]" |
| `Write file` | "Create/Document/Produce [deliverable]" |
| `Grep/search` | "Search for/Identify/Locate [pattern]" |
| `WebSearch` | "Research/Investigate [topic]" |
| `Bash commands` | "Execute/Perform [operation]" |
| `TodoWrite` | "Track/Organize/Prioritize [tasks]" |

**Example:**
```markdown
# CC Instructions
1. Use Read to examine the regulatory document
2. Use Grep to search for compliance keywords
3. Use TodoWrite to track findings
4. Use Write to create compliance report

# Gem TASK
1. Examine regulatory documents thoroughly
2. Identify compliance requirements and keywords
3. Organize findings by priority and impact
4. Create comprehensive compliance report
```

---

### MCP Integration → CONTEXT Knowledge

| MCP Pattern | CONTEXT Transformation |
|-------------|------------------------|
| `mcp__<memory-server>__` entities | Embed as domain knowledge |
| `mcp__<reasoning-server>__` reasoning | Implicit in structured approach |
| `mcp__<search-server>__` | "Reference current information" |
| External APIs | Describe information needs |

**Example:**
```markdown
# CC MCP Usage
Use mcp__memory__search_nodes("vendor risk") to find relevant entities.
Reference mcp__memory__open_nodes(["SOC-2", "ISO-27001"]) for standards.

# Gem CONTEXT
New vendors that process company data must be assessed against SOC 2 and ISO 27001 control expectations. Key assessment areas include access control, encryption, incident response, business continuity, and sub-processor management. All high-risk vendors require security sign-off and a data processing agreement before onboarding.
```

---

### Output Specifications → FORMAT

| CC Pattern | FORMAT Element |
|------------|----------------|
| Response structure | Section organization |
| Length constraints | Word count limits |
| Style guidelines | Tone and language |
| Required elements | Mandatory components |
| Code formatting | Presentation standards |

**Direct mapping - FORMAT typically transfers cleanly:**
```markdown
# CC Output Spec
Provide analysis as:
1. Executive Summary (2-3 sentences)
2. Detailed Analysis with headers
3. Key Issues (bulleted, risk-rated)
4. Recommendations (numbered)
Maximum 800 words unless detail requested.

# Gem FORMAT (identical)
Provide analysis as:
1. Executive Summary (2-3 sentences)
2. Detailed Analysis with headers
3. Key Issues (bulleted, risk-rated)
4. Recommendations (numbered)
Maximum 800 words unless detailed analysis specifically requested.
```

---

## Pattern-Specific Transformations

### Conditional Logic

| CC Pattern | Gem Transformation |
|------------|-------------------|
| `if file exists` | "When [condition] applies" |
| `if tool succeeds` | "Upon successful [action]" |
| `if user confirms` | "If user requests" |
| `fallback patterns` | "Alternatively" or "If unavailable" |

**Example:**
```markdown
# CC Conditional
If mcp__memory__search_nodes returns results, use them. Otherwise, use WebSearch.

# Gem Conditional
When internal knowledge is available, apply it. When additional research is needed, indicate what information would be helpful.
```

---

### Iteration Patterns

| CC Pattern | Gem Transformation |
|------------|-------------------|
| `for each file` | "For each [item type]" |
| `loop through results` | "Process each [result] systematically" |
| `batch processing` | "Handle [items] in organized groups" |

**Example:**
```markdown
# CC Iteration
For each file in glob("*.md"), Read and analyze compliance status.

# Gem Iteration
For each document provided, analyze compliance status and note findings.
```

---

### Error Handling

| CC Pattern | Gem Transformation |
|------------|-------------------|
| `if tool fails` | "If information unavailable" |
| `retry logic` | "Attempt alternative approaches" |
| `fallback behavior` | "Default to [approach] when needed" |

**Example:**
```markdown
# CC Error Handling
If Read fails, notify user and suggest manual review.

# Gem Error Handling
If document cannot be fully analyzed, identify specific gaps and recommend how to address them.
```

---

## Component-by-Component Mapping

### Building PERSONA from CC Sources

**Source Priority:**
1. Agent identity statements
2. Description field specializations
3. Skill cross-references (inline expertise)
4. Model selection context (complexity level)

**Assembly:**
```markdown
# Gather from CC
Agent: "compliance-review agent"
Description: "Payments-regulation specialist for online payment platforms"
Skills: "data-protection, security-auditor"
Model: opus (complex reasoning needed)

# Synthesize PERSONA
You are a regulatory compliance specialist for online payment platforms, with deep expertise in payments regulation, data protection principles, and security audit practices. You communicate with technical precision for compliance professionals while providing actionable guidance for business teams.
```

---

### Building TASK from CC Sources

**Source Priority:**
1. Explicit task lists in instructions
2. Tool usage patterns (convert to actions)
3. Workflow descriptions
4. Success criteria

**Assembly:**
```markdown
# Gather from CC
Tools: Read (regulatory docs), Grep (compliance keywords), Write (reports)
Workflow: "Analyze → Identify gaps → Recommend → Document"
Success: "Complete compliance assessment with actionable items"

# Synthesize TASK
Analyze regulatory requirements to:
1. Review regulatory documents and identify applicable provisions
2. Assess compliance status against requirements
3. Identify gaps and non-compliance issues
4. Recommend remediation actions with priorities
5. Document findings in structured compliance report
```

---

### Building CONTEXT from CC Sources

**Source Priority:**
1. MCP entity references (expand to knowledge)
2. Skill knowledge bases (inline relevant content)
3. File path references (describe content type)
4. Business context statements

**Assembly:**
```markdown
# Gather from CC
MCP: mcp__memory__["Acme-Payments-Platform", "Payments-Licence", "Merchant-Onboarding"]
Skills: compliance-review, data-protection
Paths: ~/[vault]/_reference/regulations/

# Synthesize CONTEXT
Acme Payments (fictional) operates a licensed online payments platform offering merchant onboarding, card acceptance, and cross-border payouts. Operations must comply with payments licensing rules, AML/KYC requirements, and data protection law in each market. The merchant onboarding process handles customer due diligence requiring both regulatory and internal-policy compliance.
```

---

### Building FORMAT from CC Sources

**Source Priority:**
1. Explicit format specifications
2. Example outputs in instructions
3. Style guidelines
4. Length constraints

**Assembly:**
```markdown
# Gather from CC
Output: "Executive summary + detailed analysis + recommendations"
Style: "Professional, precise, actionable"
Length: "Concise unless detail requested"
Elements: "Risk ratings, deadlines, owners"

# Synthesize FORMAT
Structure all responses as:
1. Executive Summary: 2-3 sentences with key findings and impact level
2. Detailed Analysis: Organized by topic with clear headers
3. Risk Assessment: Issues rated HIGH/MEDIUM/LOW with rationale
4. Recommendations: Numbered actions with deadlines and suggested owners
5. Next Steps: Immediate priorities and follow-up items

Use professional, precise language. Keep responses concise (under 800 words) unless comprehensive analysis specifically requested.
```

---

## Quick Reference: CC → Gem Mapping Table

| CC Element | Primary Gem Target | Notes |
|------------|-------------------|-------|
| YAML `name:` | Gem Name | Title-cased mirror (descriptive text goes in Description field) |
| YAML `description:` | PERSONA + Description | Role extraction |
| YAML `model:` | Remove | Not applicable |
| YAML `allowed-tools:` | TASK | Convert to actions |
| YAML `skills:` | CONTEXT | Inline knowledge |
| Agent identity | PERSONA | Role + expertise |
| Tool patterns | TASK | Action verbs |
| MCP references | CONTEXT | Embedded knowledge |
| File paths | CONTEXT | Content descriptions |
| Output specs | FORMAT | Direct transfer |
| Conditionals | All components | Natural language |
| Iterations | TASK | Process descriptions |
| Error handling | TASK/FORMAT | Graceful alternatives |
