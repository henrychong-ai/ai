# Agent vs Skill Decision Guide

**Complete decision matrix for choosing between agents and skills**

---

## Quick Decision Framework

**Use Agent** when you need:
- Autonomous delegation with "Use PROACTIVELY" pattern
- Complex autonomous decision-making
- TodoWrite for multi-step task tracking
- Business context integration
- Continuous domain specialist operation

**Use Skill** when you need:
- Knowledge augmentation via semantic auto-triggering
- Bundled reusable resources (scripts, references, assets)
- Progressive disclosure (load as needed)
- Token-efficient resource loading
- Specialized knowledge packages

**Use Both** when you need:
- Autonomous operation + knowledge resources
- Complex domain requiring flexibility
- Both delegation capability and bundled assets

**Note:** Both agents and skills auto-trigger via semantic description matching. The key difference is agents add autonomous delegation capabilities.

---

## Detailed Comparison

### Agents

**Characteristics:**
- Location: `~/.claude/agents/*.md`
- Invocation: Automatic via triggers in description, or explicit via Task tool
- Format: YAML frontmatter (name, description, model) + markdown content
- Complexity: Complex autonomous workflows
- Integration: References project-instructions.md for business context
- Tools: TodoWrite capability required for task tracking

**Best For:**
- Domain specialists (compliance-officer, things, typescript)
- Business-critical operations requiring context
- Multi-step workflows with progress tracking
- Operations requiring escalation criteria
- Proactive system monitoring and optimization

**Examples:**
- **compliance-officer**: Autonomous compliance review with business context
- **things**: Proactive task management and optimization
- **typescript**: Automatic code review and TypeScript best practices
- **security-auditor**: Continuous security scanning and vulnerability detection

### Skills

**Characteristics:**
- Location: `~/.claude/skills/*/SKILL.md`
- Invocation: Explicit via "use skill [name]" or auto-triggers
- Format: YAML frontmatter (name, description) + markdown + bundled resources
- Resources: scripts/, references/, assets/ subdirectories
- Loading: Progressive disclosure (metadata → SKILL.md → resources)
- Efficiency: Only load resources when Claude determines needed

**Best For:**
- Specialized knowledge with reusable components
- Operations requiring bundled scripts/templates
- Reference documentation loaded as needed
- Token-efficient progressive disclosure
- Explicit user control over invocation

**Examples:**
- **pdf**: PDF manipulation with scripts for rotation, merging
- **xlsx**: Spreadsheet operations with formula handling
- **travel**: Travel planning with dietary guidelines references
- **instruction-creator**: Comprehensive instruction file creation with templates and tooling

### Hybrid Approach (Agent + Skill)

**Use Both When:**
- Complex domain benefits from both proactive and explicit invocation
- Want automatic monitoring + manual deep-dive capability
- Need business integration (agent) + reusable resources (skill)
- Desire flexibility in how capability is accessed

**Example: instruction-creator**
- **Agent** (`~/.claude/agents/instruction-creator.md`):
  - Proactive architectural review
  - System-wide instruction optimization
  - Complex multi-file creation
  - Business context integration

- **Skill** (`~/.claude/skills/instruction-creator/SKILL.md`):
  - Explicit reference when creating single file
  - Quick lookup for YAML frontmatter
  - Decision guidance without full context load
  - Progressive disclosure to reference materials

### Differentiating Same-Named Skill/Agent Pairs

When creating both a skill and agent with the same name, **differentiate their descriptions** to avoid trigger overlap:

**Skill Description Pattern** (reference/guidance focus):
```yaml
description: This skill should be used for quick reference and guidance about [domain].
Use for questions about [formats], [decisions], [options], and [best practices].
Triggers: "[what format]", "[how to structure]", "[which option]", "[template]".
For actual implementation, use the [name] agent instead.
```

**Agent Description Pattern** (implementation/execution focus):
```yaml
description: [Role] for [domain]. Use PROACTIVELY for creating/updating [items],
building [deliverables], complex multi-step [workflows], and [domain] review.
```

**Trigger Word Strategy:**

| Skill Triggers (Reference) | Agent Triggers (Implementation) |
|----------------------------|--------------------------------|
| "what format", "how to structure" | "create", "build", "update" |
| "which option", "should I use" | "implement", "generate", "modify" |
| "template", "example", "best practice" | "review", "optimize", "fix" |
| Question words: what, how, which | Action words: create, build, update |

**Key Principle:** Skills answer "what/how" questions; Agents execute "do this" requests.

---

## Decision Tree

```
Need instruction capability?
│
├─ Need autonomous delegation ("Use PROACTIVELY")?
│  ├─ YES → Agent (or Agent + Skill for bundled resources)
│  └─ NO → Continue
│
├─ Need bundled resources (scripts/references/assets)?
│  ├─ YES → Skill (or Agent + Skill if also need delegation)
│  └─ NO → Continue
│
├─ Need complex autonomous decision-making with TodoWrite?
│  ├─ YES → Agent
│  └─ NO → Continue
│
├─ Need business context integration?
│  ├─ YES → Agent
│  └─ NO → Continue
│
├─ Need progressive disclosure for token efficiency?
│  ├─ YES → Skill
│  └─ NO → Continue
│
└─ Default: Start with Skill, upgrade to Agent if autonomous delegation needed
```

**Remember:** Both auto-trigger via semantic matching. Choose based on delegation needs, not triggering.

---

## Common Scenarios

### Scenario 1: File Format Operations (PDF, XLSX, DOCX)
**Decision: Skill**
- Bundled scripts for deterministic operations
- Reference documentation for complex formats
- Explicit invocation when user needs specific format
- No need for proactive operation

### Scenario 2: Domain Compliance Review
**Decision: Agent**
- Proactive review when compliance-related code detected
- Business context integration critical
- Complex decision-making with escalation
- TodoWrite for tracking multi-step reviews

### Scenario 3: Travel Planning
**Decision: Skill**
- Bundled references for dietary guidelines, preferences
- Explicit invocation when planning travel
- Progressive disclosure (only load dietary guidelines when needed)
- No need for continuous monitoring

### Scenario 4: Code Review System
**Decision: Agent + Skill**
- **Agent**: Proactive code review on commits, PRs
- **Skill**: Explicit invocation for deep-dive analysis
- Agent provides continuous monitoring
- Skill provides on-demand detailed review with patterns

### Scenario 5: Quick Commands (Search, Format, Transform)
**Decision: Neither - use Slash Command**
- Simple, targeted operations
- No complex decision-making
- No bundled resources needed
- Natural language instructions sufficient

---

## Migration Paths

**Skill → Agent:**
When skill usage shows need for proactive operation:
1. Create agent referencing skill for resources
2. Add YAML frontmatter with proactive triggers
3. Add TodoWrite capability
4. Add business context integration
5. Keep skill for explicit invocation option

**Agent → Skill:**
When agent shows bundled resources would help:
1. Extract reusable resources to skill structure
2. Create scripts/, references/, assets/ as needed
3. Agent references skill for resources
4. Maintain agent for proactive operation

**Single → Hybrid (Agent + Skill):**
When both patterns provide value:
1. Keep agent for proactive operation
2. Create skill with complementary resources
3. Agent references skill in its implementation
4. Users get both automatic and explicit access

---

## Summary Table

| Feature | Agent | Skill | Both |
|---------|-------|-------|------|
| **Auto-Trigger (Semantic)** | ✅ | ✅ | ✅ |
| **Autonomous Delegation** | ✅ | ❌ | ✅ |
| **Explicit Invocation** | ✅ | ✅ | ✅ |
| **Bundled Resources** | ❌ | ✅ | ✅ |
| **Progressive Disclosure** | ❌ | ✅ | ✅ |
| **TodoWrite Capability** | ✅ | ❌ | ✅ |
| **Business Context** | ✅ | ❌ | ✅ |
| **Token Efficiency** | ⚠️ | ✅ | ✅ |
| **Complexity** | High | Medium | Highest |
| **Maintenance** | Medium | Low | High |

**Key Distinction:**
- Both skills and agents auto-trigger via semantic description matching
- Agents add autonomous delegation via "Use PROACTIVELY" in description
- Commands require manual invocation (/command-name)

---

## Cross-Platform Skill Compatibility

Skills can be shared and used across multiple Claude platforms:

| Platform | Format | Sharing Method | Supported |
|----------|--------|----------------|-----------|
| **Claude Code** | Directory with `SKILL.md` | Git-based, local directory | ✅ |
| **Claude Desktop** | ZIP file | Manual upload via Projects | ✅ |
| **claude.ai (Web)** | ZIP file | Manual upload via interface | ✅ |
| **Claude Mobile** | N/A | N/A | ❌ |
| **Claude API** | ZIP/String/ID | Programmatic via `custom_instructions` | ✅ |

### Platform-Specific Notes

**Claude Code:**
- Native skill support via `~/.claude/skills/*/SKILL.md` structure
- Full access to bundled resources (scripts/, references/, assets/)
- Auto-triggers via semantic description matching

**Claude Desktop:**
- Upload skills as ZIP files through Projects → Custom Instructions
- Skill content becomes part of project context
- Bundled resources included in ZIP

**claude.ai (Web):**
- Same ZIP upload mechanism as Desktop
- Available in conversation Custom Instructions
- Progressive disclosure works same as Claude Code

**Claude Mobile App:**
- Skills are NOT supported on mobile
- No documentation for skill upload or usage
- Use other platforms for skill-based workflows

**Claude API:**
- Skills can be provided via `custom_instructions` parameter
- Supports ZIP file (base64), string content, or skill ID
- Enables programmatic skill integration in applications

### Skill Packaging for Cross-Platform Use

When creating skills for cross-platform sharing:

1. **Structure**: Maintain standard directory structure
   ```
   skill-name/
   ├── SKILL.md (required)
   ├── scripts/
   ├── references/
   └── assets/
   ```

2. **Package**: Create ZIP file preserving directory structure
   ```bash
   cd ~/.claude/skills
   zip -r skill-name.zip skill-name/
   ```

3. **Share**: Upload ZIP to Desktop/Web, or use programmatically via API

**Note:** Agents are Claude Code-specific and cannot be uploaded to other platforms. For cross-platform portable instructions, skills are the recommended format.

---

**Last Updated:** 2025-11-26
**Use Case:** Decision guidance for instruction file type selection
