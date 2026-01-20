# Transformation Mapping

Systematic mapping from Claude Code instruction patterns to Gemini gem components.

## Core Mapping: CC → Gem Components

### YAML Frontmatter → PERSONA + Description Field

| CC Element | Gem Target | Transformation |
|------------|------------|----------------|
| `name:` | Description field | Convert to descriptive gem name |
| `description:` | PERSONA + Description | Extract role and purpose |
| `model:` | N/A | Remove (Gemini uses fixed model) |
| `allowed-tools:` | TASK | Convert capabilities to actions |
| `skills:` | CONTEXT | Inline relevant knowledge |

**Example:**
```yaml
# CC Frontmatter
---
name: compliance-analyzer
description: Analyzes regulatory compliance for Fusang operations
model: opus
allowed-tools: Read, Grep, WebSearch
skills: compliance-fusang
---

# Gem Mapping
PERSONA: You are a regulatory compliance analyst specializing in digital securities...
Description field: "Regulatory compliance analyzer for Fusang operations"
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
You are the compliance-fusang agent, a Labuan FSA specialist with access to mcp__kg__ for regulatory lookups...

# Gem PERSONA
You are a regulatory compliance analyst specializing in Labuan FSA regulations for digital securities exchanges. You have deep expertise in VASP licensing, AML/KYC requirements, and operational compliance. You communicate with technical precision suitable for compliance officers and senior executives.
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
| `mcp__kg__` entities | Embed as domain knowledge |
| `mcp__st__` thinking | Implicit in structured approach |
| `mcp__perplexity__` | "Reference current information" |
| External APIs | Describe information needs |

**Example:**
```markdown
# CC MCP Usage
Use mcp__kg__semantic_search("sukuk structures") to find relevant entities.
Reference mcp__kg__open_nodes(["AAOIFI", "Labuan-FSA"]) for standards.

# Gem CONTEXT
Sukuk structures must comply with AAOIFI accounting standards and Labuan FSA regulations. Key sukuk types include Ijara (lease-based), Mudaraba (profit-sharing), Musharaka (partnership), and Wakalah (agency). All structures require Shariah certification and proper asset backing.
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
If mcp__kg__search returns results, use them. Otherwise, use WebSearch.

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
Agent: "compliance-fusang agent"
Description: "Labuan FSA specialist for digital securities"
Skills: "islamic-finance, security-auditor"
Model: opus (complex reasoning needed)

# Synthesize PERSONA
You are a regulatory compliance specialist for digital securities exchanges, with deep expertise in Labuan FSA regulations, Islamic finance principles, and security audit practices. You communicate with technical precision for compliance professionals while providing actionable guidance for business teams.
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
MCP: mcp__kg__["Fusang-Exchange", "Labuan-FSA", "IILM-Sukuk"]
Skills: compliance-fusang, islamic-finance
Paths: ~/[vault]/_reference/regulations/

# Synthesize CONTEXT
Fusang operates a Labuan FSA-licensed digital securities exchange offering sukuk tokenization, crypto trading, and Vault custody services. Operations must comply with Labuan FSA, Hong Kong SFC (for VASP operations), and Singapore MAS (for regional expansion). The IILM Sukuk platform handles Islamic liquidity management instruments requiring both regulatory and Shariah compliance.
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
| YAML `name:` | Description field | Descriptive title |
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
