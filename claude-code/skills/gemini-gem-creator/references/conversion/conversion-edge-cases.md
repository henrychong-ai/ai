# Conversion Edge Cases

Handling complex and unusual scenarios during CC → Gem conversion.

## Multi-File Skills

### Scenario
CC skill has multiple reference files that need consolidation.

**Example Structure:**
```
skill-name/
├── SKILL.md
└── references/
    ├── framework.md
    ├── templates.md
    ├── examples.md
    └── domain-knowledge.md
```

### Resolution Options

**Option 1: Selective Inclusion**
- Identify most critical content
- Inline essential knowledge into CONTEXT
- Summarize remaining content
- Document what was excluded

**Option 2: Attachment Strategy**
- Convert core instructions to gem
- Recommend attaching key reference files
- Note: Gemini supports file attachments

**Option 3: Split into Multiple Gems**
- Create separate gems for distinct functions
- Better than one bloated gem
- Each gem focused and effective

### Decision Framework
| Reference File Size | Content Type | Recommendation |
|--------------------|--------------|----------------|
| < 500 words | Core knowledge | Inline to CONTEXT |
| 500-2000 words | Supporting detail | Summarize + attach |
| > 2000 words | Extensive reference | Separate gem or attachment |

---

## Tool-Heavy Instructions

### Scenario
CC instructions are primarily tool orchestration with minimal conceptual content.

**Example:**
```markdown
1. Use Glob to find all *.ts files
2. Use Grep to search for "TODO" comments
3. Use Read on each matched file
4. Use TodoWrite to track findings
5. Use Write to create summary.md
```

### Resolution

**Transform to intent-based instructions:**
```markdown
TASK:
1. Identify all TypeScript files in the codebase
2. Search for TODO comments and technical debt markers
3. Analyze each occurrence for context and priority
4. Organize findings by severity and effort required
5. Create comprehensive summary document

Provide systematic code review focused on identifying and prioritizing technical debt.
```

**Key principle:** Extract the *purpose* behind each tool operation, not the tool itself.

---

## Complex MCP Workflows

### Scenario
CC instructions heavily integrate multiple MCP tools in sophisticated patterns.

**Example:**
```markdown
1. mcp__kg__semantic_search("compliance requirements")
2. mcp__st__sequentialthinking for analysis planning
3. mcp__perplexity__research for current regulations
4. mcp__kg__create_entities for findings
5. mcp__bifrost__create_route for results publication
```

### Resolution

**Decompose and describe:**
```markdown
TASK:
1. Research compliance requirements using available knowledge
2. Apply structured analytical thinking to assess findings
3. Investigate current regulatory developments
4. Document key findings for future reference
5. Prepare results for appropriate distribution

CONTEXT:
[Embed the domain knowledge that would have come from KG searches]
Compliance requirements include... Current regulatory landscape shows...
```

**Principle:** The MCP tools are *how* CC accomplishes tasks; gems need the *what* and *why*.

---

## Recursive Agent Calls

### Scenario
CC instruction delegates to other agents or triggers subagent workflows.

**Example:**
```markdown
For compliance review, spawn compliance-fusang agent.
For security assessment, use Task tool with security-auditor.
For content creation, delegate to content-marketer agent.
```

### Resolution

**Inline the delegated expertise:**
```markdown
CONTEXT:
This gem combines multiple domain expertise areas:

Compliance Expertise:
- Labuan FSA digital securities regulations
- AML/KYC requirements and monitoring
- Regulatory reporting obligations

Security Expertise:
- OWASP compliance assessment
- Authentication and access control review
- Data protection verification

Content Expertise:
- Professional communication standards
- Brand voice guidelines
- Target audience considerations
```

**Or recommend gem ecosystem:**
> Note: For comprehensive coverage, consider using this gem alongside:
> - Compliance Review Gem (for regulatory deep-dives)
> - Security Assessment Gem (for technical security)

---

## Session State Dependencies

### Scenario
CC instructions reference or depend on persistent session state.

**Example:**
```markdown
Reference the analysis from our earlier discussion.
Build on the compliance gaps identified in the previous session.
Use the entity created earlier: `Active-Compliance-Review-2024`.
```

### Resolution

**Remove state dependencies completely:**
```markdown
# Before
Continue the compliance review from our previous session.

# After
Conduct comprehensive compliance review. If building on prior analysis, please provide the previous findings for continuity.
```

**Make stateless and self-contained:**
- Gems cannot access prior session context
- All necessary context must be provided in prompt
- Instructions should work from cold start

---

## Platform-Specific Features

### Scenario
CC instructions use features not available in Gemini.

| CC Feature | Gemini Status | Resolution |
|------------|---------------|------------|
| TodoWrite tracking | Not available | Describe task organization approach |
| File system access | Limited (attachments) | Use attachment recommendations |
| Web search | Available (different) | "Research current information" |
| Code execution | Available (different) | Describe computational needs |
| Image generation | Available | Can reference directly |

### Example Resolution
```markdown
# Before (CC)
Use TodoWrite to track:
- [ ] Review document A
- [ ] Review document B
- [ ] Create summary

# After (Gem)
Systematically process each document:
1. First, review document A and note key findings
2. Next, review document B and note key findings
3. Finally, synthesize findings into comprehensive summary

Present progress through your response as you complete each step.
```

---

## Domain Knowledge Gaps

### Scenario
CC skill relies on extensive reference files or KG entities not available in gem.

**Example:**
```markdown
Reference ~/[vault]/_reference/regulations/MAS-comprehensive-guide.md
Use mcp__kg__open_nodes(["MAS-Guidelines-2024", "SFC-Requirements"])
```

### Resolution Options

**Option 1: Embed Critical Knowledge**
```markdown
CONTEXT:
MAS Regulatory Framework:
- Payment Services Act requirements for digital payment tokens
- Securities and Futures Act provisions for capital markets
- Technology risk management guidelines (MAS TRM)
- AML/CFT requirements under MAS Notice 626
```

**Option 2: Recommend Attachments**
```markdown
## Recommended Attachments
For comprehensive regulatory analysis, attach:
- Current MAS guidelines document
- Relevant SFC circulars
- Company-specific compliance matrix
```

**Option 3: Acknowledge Limitations**
```markdown
CONTEXT:
...When specific regulatory provisions are needed, request the relevant regulatory document or guideline for precise analysis.
```

---

## Conflicting Instructions

### Scenario
CC skill has instructions that conflict when converted to static gem format.

**Example:**
```markdown
If using opus model, provide detailed 2000-word analysis.
If using haiku model, provide concise 500-word summary.
```

### Resolution

**Choose appropriate default, document flexibility:**
```markdown
FORMAT:
Provide comprehensive analysis (approximately 800-1200 words) by default.

If user requests:
- "Brief summary" → Provide concise 300-500 word overview
- "Detailed analysis" → Provide thorough 1500-2000 word examination
```

---

## Personal Workflow Integration

### Scenario
CC skill deeply integrates with personal systems (Obsidian, Things, etc.)

**Example:**
```markdown
Create task in [task-app] via [task-agent].
Save to knowledge vault at ~/[vault]/projects/.
Reference daily note for context.
```

### Resolution

**Abstract to general workflow:**
```markdown
# Before
Save findings to ~/[vault]/_todo/compliance-items.md
Create [task-app] tasks for follow-up items

# After
TASK:
...
5. Present findings in format suitable for task management import
6. Highlight action items with clear ownership and deadlines

FORMAT:
...
Action Items Section:
- [ ] [Action] - [Owner] - [Deadline]
(Format compatible with standard task management tools)
```

---

## Conversion Decision Tree

```
Is the CC instruction tool-dependent?
├── Yes → Extract intent, describe conceptually
└── No → Preserve instruction logic

Does it reference external files?
├── Yes, critical → Embed or recommend attachment
├── Yes, supplementary → Summarize key points
└── No → Proceed normally

Does it delegate to other agents?
├── Yes → Inline expertise or recommend gem ecosystem
└── No → Proceed normally

Does it depend on session state?
├── Yes → Make stateless, request context in prompt
└── No → Proceed normally

Is the result self-contained?
├── Yes → Proceed to quality validation
└── No → Iterate on identified gaps
```

---

## When to Recommend Not Converting

Some CC skills should NOT be converted to gems:

| Scenario | Reason | Alternative |
|----------|--------|-------------|
| Primarily tool orchestration | No conceptual value without tools | Document process manually |
| Heavy external integrations | Depends on systems unavailable to Gemini | Keep as CC skill |
| Real-time data requirements | Needs live API access | Use Gemini with manual data |
| Personal workflow automation | Too individual-specific | Not for team sharing |
| Security-sensitive operations | Credential handling, etc. | Keep in controlled environment |

**Recommendation format:**
> This CC skill is not suitable for Gemini gem conversion because [reason].
> Suggested alternative: [alternative approach].
