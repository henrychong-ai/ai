# Removal Protocols

Systematic protocols for removing Claude Code-specific elements when converting to Gemini gems.

## CC Syntax Removal

### YAML Frontmatter
**Remove completely:**
```yaml
---
name: skill-name
description: ...
model: opus
allowed-tools: Read, Grep, Glob
user-invocable: true
---
```

**No equivalent in Gemini.** The gem description field handles basic identification.

---

### Tool References

**Remove all tool references:**

| CC Tool | Action |
|---------|--------|
| `Read` | Remove - describe information gathering instead |
| `Write` | Remove - describe content creation instead |
| `Edit` | Remove - describe modification instead |
| `Grep` | Remove - describe search intent |
| `Glob` | Remove - describe file discovery intent |
| `Bash` | Remove - describe actions conceptually |
| `WebSearch` | Remove - describe research needs |
| `WebFetch` | Remove - describe URL analysis needs |
| `Task` | Remove - describe delegation approach |
| `TodoWrite` | Remove - describe task tracking approach |

**Example transformation:**
```
# Before (CC)
Use Read tool to examine configuration files, then Grep for error patterns.

# After (Gem)
Examine configuration files to identify error patterns and system settings.
```

---

### MCP References

**Remove all MCP tool patterns:**

| MCP Pattern | Action |
|-------------|--------|
| `mcp__kg__*` | Remove knowledge graph operations |
| `mcp__st__*` | Remove sequential thinking references |
| `mcp__perplexity__*` | Remove Perplexity integration |
| `mcp__bifrost__*` | Remove edge router references |
| `mcp__codex__*` | Remove Codex references |

**Example:**
```
# Before (CC)
Use mcp__kg__semantic_search to find related entities, then mcp__st__sequentialthinking for analysis.

# After (Gem)
Search for related information and apply systematic analysis to understand connections.
```

---

### File Path References

**Remove all path patterns:**

| Path Pattern | Action |
|--------------|--------|
| `/Users/...` | Remove absolute paths |
| `~/.claude/...` | Remove Claude Code paths |
| `~/[vault]/...` | Remove knowledge vault references |
| `~/[app]/...` | Remove app-specific paths |
| `./relative/path` | Remove relative paths |

**Transform to conceptual descriptions:**
```
# Before (CC)
Reference ~/[vault]/_reference/regulations/MAS-guidelines.md for regulatory context.

# After (Gem)
Reference MAS regulatory guidelines for compliance context.
```

---

### Agent/Skill Cross-References

**Remove all cross-references:**

| Pattern | Action |
|---------|--------|
| `use skill [name]` | Remove or inline functionality |
| `/command-name` | Remove slash command references |
| `{agent-name} agent` | Remove agent delegation |
| `subagent_type=X` | Remove subagent patterns |

**Transform to self-contained instructions:**
```
# Before (CC)
For compliance analysis, use the compliance-fusang skill with /compliance command.

# After (Gem)
For compliance analysis, apply regulatory assessment framework covering Labuan FSA, SFC, and MAS requirements.
```

---

## Individual Content Sanitization

### Personal Information

**Remove all personal identifiers:**

| Element | Action |
|---------|--------|
| `[personal-name]`, `[username]` | Remove or replace with role-based reference |
| Personal email addresses | Remove completely |
| Personal phone numbers | Remove completely |
| Home addresses | Remove completely |
| Personal account IDs | Remove completely |

**Example:**
```
# Before
Contact [personal-name] at [user@company.com] for approval.

# After
Escalate to appropriate approver for sign-off.
```

---

### Custom Productivity Frameworks

**Remove all personal framework references:**

| Element | Action |
|---------|--------|
| Custom system names | Remove system references |
| Personal methodology terms | Remove or generalize |
| Framework-specific jargon | Convert to plain language |
| Personal workflow triggers | Remove completely |
| Life area categorizations | Remove personal framework |

**Retain universal concepts, remove personal framework:**
```
# Before (CC)
Apply [custom-framework] for productivity optimization.

# After (Gem)
Focus on raising quality standards while eliminating inefficiencies.
```

---

### Knowledge Graph Entities

**Remove all KG entity references:**

| Pattern | Action |
|---------|--------|
| Entity names in backticks | Remove or convert to descriptions |
| KG domain prefixes | Remove |
| Entity type references | Convert to plain descriptions |

**Example:**
```
# Before
Reference `Fusang-Exchange` entity for company context and `MAS-Regulations` for compliance.

# After
Reference Fusang Exchange operations and MAS regulatory requirements.
```

---

### Session-Specific Context

**Remove all session artifacts:**

| Element | Action |
|---------|--------|
| Conversation references | Remove |
| "Earlier we discussed..." | Remove |
| Session IDs | Remove |
| Temporary states | Remove |
| User-specific preferences | Generalize |

---

## Business Context Preservation

### What to Keep

**Preserve company-relevant content:**

| Element | Preserve |
|---------|----------|
| Fusang digital securities context | ✅ Keep |
| Portcullis wealth management context | ✅ Keep |
| Regulatory frameworks (MAS, SFC, Labuan FSA) | ✅ Keep |
| Industry terminology | ✅ Keep |
| Domain expertise | ✅ Keep |
| Business processes | ✅ Keep (generalized) |

---

### Transformation Examples

**Company Context:**
```
# Before (CC with personal refs)
[Personal-name]'s [Company] operates under [Regulator] license. Check ~/[vault]/_reference/[company]/ for details.

# After (Gem)
[Company] operates under [Regulator] license, providing [services description].
```

**Team Member Context:**
```
# Before (CC)
Use the [company] skill for [service]. Reference [team-member]'s expertise.

# After (Gem)
Apply [service] expertise for [domain] across [jurisdictions].
```

**Regulatory Context:**
```
# Before (CC)
Use compliance-fusang skill with mcp__kg__search_nodes("MAS") for regulatory lookup.

# After (Gem)
Reference MAS regulatory requirements for Singapore operations, including licensing, AML/KYC, and reporting obligations.
```

---

## Removal Checklist

Before finalizing any converted gem:

### CC Syntax
- [ ] YAML frontmatter removed
- [ ] All tool references removed (Read, Write, Edit, Grep, Glob, Bash, etc.)
- [ ] All MCP references removed (mcp__kg__, mcp__st__, etc.)
- [ ] All file paths removed (/Users/, ~/.claude/, ~/[vault]/, etc.)
- [ ] All agent/skill cross-references removed
- [ ] All TodoWrite patterns removed

### Personal Content
- [ ] Personal names removed (e.g., [personal-name], [username])
- [ ] Custom framework references removed (personal productivity systems)
- [ ] Personal KG entity references removed
- [ ] Session-specific context removed
- [ ] Personal email/phone/addresses removed

### Business Context
- [ ] Fusang context preserved (if relevant)
- [ ] Portcullis context preserved (if relevant)
- [ ] Regulatory frameworks preserved (MAS, SFC, Labuan FSA)
- [ ] Industry terminology intact
- [ ] Domain expertise maintained

### Quality Check
- [ ] Instructions make sense without CC tools
- [ ] No orphaned references to removed elements
- [ ] Self-contained and standalone
- [ ] Ready for team distribution
