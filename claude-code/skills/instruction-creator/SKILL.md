---
name: instruction-creator
description: This skill should be used for quick reference and guidance about instruction files (agents, skills, slash commands, MCP servers, project instructions). Use for questions about YAML frontmatter format, agent-vs-skill decisions, model configuration options, templates, and best practices. Provides 5-step skill creation workflow reference, tooling scripts (init_skill.py, package_skill.py, quick_validate.py), and decision matrices. Triggers: "YAML frontmatter", "agent vs skill", "model configuration", "instruction template", "what format", "how do I structure", "skill workflow". For actual creation/implementation of instruction files, use the instruction-creator agent instead.
---

# Instruction Creator Skill

This skill provides complete guidance for creating and reviewing Claude instruction files across the entire instruction ecosystem.

## About Instruction Files

Claude instruction files extend Claude's capabilities through specialized instructions. Understanding when to use each type is critical for effective system design.

### Instruction File Types

| Type | Location | Purpose | Invocation |
|------|----------|---------|------------|
| **Agents** | `~/.claude/agents/*.md` | Autonomous domain specialists | Auto-trigger or Task tool |
| **Skills** | `~/.claude/skills/*/SKILL.md` | Bundled knowledge packages | "use skill [name]" |
| **Commands** | `~/.claude/commands/*.md` | Natural language prompts | `/command-name` |
| **Project** | `project-instructions.md` | Business context | Auto-loaded per project |

## Creating Agents

Agents are autonomous domain specialists with proactive operation capabilities.

### Agent YAML Frontmatter (Required)

```yaml
---
name: agent-name                    # Required: kebab-case identifier
description: Brief description...   # Required: include "Use PROACTIVELY" for auto-trigger
model: sonnet                       # Required: use aliases (opus/sonnet/haiku)
---
```

**Model Configuration**:
- **Use aliases**: `opus`, `sonnet`, `haiku` (automatically use latest version)
- **Model selection analysis** - For each agent, analyze:
  - Complexity level (simple patterns vs multi-step reasoning)
  - Decision-making needs (rule-based vs judgment-based)
  - Performance needs (speed-critical vs quality-critical)
- **Model capabilities**:
  - `opus`: Complex reasoning, strategic analysis, nuanced judgment, multi-step workflows
  - `sonnet`: General-purpose capability, balanced performance, most technical tasks
  - `haiku`: Fast responses, simple patterns, rule-based operations, high-volume tasks
- **Priority order**: Task tool override → Agent YAML → Inherit from parent → System default
- **Override at invocation**: Can specify different model via Task tool `model` parameter

### Agent Template Structure

```markdown
---
name: agent-name
description: [Specialization]. [Capabilities]. Use PROACTIVELY for [triggers].
model: sonnet  # analyze task needs: opus (complex), sonnet (balanced), haiku (fast)
---

# **AGENT NAME: SPECIALIZED PURPOSE**

[Agent identity and mission]

## AUTO-ACTIVATION SEQUENCE
1. Load Context: Reference project-instructions.md if applicable
2. Tool Readiness: Prepare TodoWrite and MCP strategies
3. Success Metrics: Define execution excellence standards

## DOMAIN EXPERTISE
[Specialized knowledge and capabilities]

## OPERATIONAL PROTOCOLS
[Workflows, tool usage, MCP token strategies]

## SUCCESS METRICS
[Measurement and evolution criteria]
```

### Agent Key Requirements

- **TodoWrite capability**: Essential for complex multi-step workflows
- **MCP token strategies**: Include explicit 25000 token limit mitigation
- **Escalation criteria**: Define when to escalate to human review
- **"Use PROACTIVELY"**: Include in description for auto-triggering
- **Model selection**: Use aliases (`opus`/`sonnet`/`haiku`) - analyze task needs for optimal choice

## Creating Skills

Skills are specialized knowledge packages with bundled resources using progressive disclosure.

### 5-Step Skill Creation Process

#### Step 1: Understand the Skill

Clarify what problem the skill solves with concrete examples:
- What functionality should this skill support?
- What would a user say that should trigger this skill?
- What are the success criteria?
- What are the edge cases?

#### Step 2: Write the Name

- Format: lowercase with hyphens (kebab-case)
- Maximum: 64 characters
- Examples: `pdf-editor`, `travel-planner`, `compliance-reviewer`

#### Step 3: Write the Description (CRITICAL)

The description determines when the skill activates. Include:
- **What it does**: Concrete verbs and capabilities
- **When to use it**: Specific triggers and use cases
- **Third-person voice**: "This skill should be used when..."
- **Maximum**: 1024 characters

**Pattern:**
```
This skill should be used when [use cases]. [Capabilities summary]. [Special triggers if any].
```

**Example:**
```yaml
description: This skill should be used when working with PDFs for extraction, creation, merging, splitting, or form handling. Provides scripts for rotation, compression, and text extraction.
```

#### Step 4: Write Main Instructions

Structure with clear hierarchy:
1. Overview and purpose
2. Prerequisites
3. Execution steps with examples
4. Error handling
5. Limitations

**Writing Style**: Use imperative/infinitive form (verb-first), objective instructional language.

#### Step 5: Package and Test

Run validation and packaging scripts:
```bash
# Quick validation
scripts/quick_validate.py ~/.claude/skills/your-skill

# Full packaging
scripts/package_skill.py ~/.claude/skills/your-skill
```

### Skill Directory Structure

```
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter (name, description - required)
│   └── Markdown instructions
└── Bundled Resources (optional)
    ├── scripts/    - Executable code for deterministic operations
    ├── references/ - Documentation loaded as needed
    └── assets/     - Files used in output (templates, icons)
```

### Skill YAML Frontmatter (Required)

```yaml
---
name: skill-name                    # Required: kebab-case, max 64 chars
description: This skill should...   # Required: third-person voice, max 1024 chars
---
```

Optional:
```yaml
allowed-tools: Read, Grep, Glob     # Optional: restrict tool access
```

### Progressive Disclosure Design

Skills use three-level loading for token efficiency:

1. **Metadata** (~100 tokens) - Always in context
2. **SKILL.md body** (<5k tokens) - When skill triggers
3. **Bundled resources** - As needed by Claude

**Best Practice**: Keep SKILL.md lean; move detailed reference material to `references/` subdirectory.

### Bundled Resources

#### scripts/
Executable code for deterministic operations that would otherwise be rewritten repeatedly.
- **When to include**: Code needed for consistent, reliable execution
- **Benefits**: Token efficient, deterministic, may execute without loading into context

#### references/
Documentation loaded as needed into context.
- **When to include**: Detailed guides, schemas, API docs, company policies
- **Best practice**: If files are large (>10k words), include grep patterns in SKILL.md
- **Avoid duplication**: Info in either SKILL.md OR references, not both

#### assets/
Files not loaded into context but used in output.
- **When to include**: Templates, images, boilerplate code, fonts
- **Examples**: Brand logos, PowerPoint templates, HTML scaffolds

### Script Usage

Initialize a new skill:
```bash
scripts/init_skill.py skill-name --path ~/.claude/skills/
```

Validate a skill:
```bash
scripts/quick_validate.py ~/.claude/skills/skill-name
```

Package for distribution:
```bash
scripts/package_skill.py ~/.claude/skills/skill-name
```

### Testing Skills (3 Scenarios)

1. **Normal operations**: Typical requests - should handle perfectly
2. **Edge cases**: Unusual inputs - should degrade gracefully
3. **Out-of-scope**: Related but distinct tasks - skill should NOT activate

## Creating Slash Commands

Slash commands are natural language instruction prompts (NOT executable code) that Claude interprets.

### Command YAML Frontmatter (Optional)

```yaml
---
allowed-tools: Bash(git:*), Read    # Optional: restrict tool access
argument-hint: [pr-number] [assignee]  # Optional: guide expected parameters
description: Brief command purpose  # Optional: command summary
model: sonnet                       # Optional: use aliases (opus/sonnet/haiku)
---
```

### Command Template

```markdown
---
allowed-tools: Tool(specific-commands)  # Optional
argument-hint: [format]                 # Optional
description: Brief command purpose      # Optional
---

# Natural Language Instructions for Claude

[Specific behavior description]

## Input Processing
- $ARGUMENTS represents user input (substituted by Claude Code)
- Process $ARGUMENTS as [expected format/type]
- Handle edge cases: [guidance]

## Tool Usage
- Use [specific tools] to [accomplish task]
- Load documentation from [paths] before execution

## Output Requirements
- Provide [specific format] as response
- Include [specific elements] in output
```

### $ARGUMENTS Handling

```markdown
# All arguments as single string
Fix issue #$ARGUMENTS following our standards
# Usage: /fix 123 high-priority → $ARGUMENTS = "123 high-priority"

# Positional arguments
Review PR #$1 with priority $2
# Usage: /review 456 high → $1 = "456", $2 = "high"
```

**Critical Understanding**: Commands are instruction prompts, not programs. Success depends on instruction clarity, not code implementation.

## Agent vs Skill Decision Matrix

### Quick Decision Framework

**Use Agent When:**
- Proactive operation with auto-triggering needed
- Complex autonomous decision-making required
- Multi-step workflows requiring TodoWrite
- Integration with business context via project references
- Domain specialist needing continuous operation

**Use Skill When:**
- Explicit invocation preferred ("use skill [name]")
- Bundled resources needed (scripts, references, assets)
- Progressive disclosure valuable (load resources as needed)
- Specialized knowledge with reusable components
- Token efficiency through optional resource loading

**Use Command When:**
- Simple, single-step operations
- Natural language instructions sufficient
- No complex decision-making needed
- Quick user-triggered workflows

**Use Both (Agent + Skill) When:**
- Complex domain benefits from both proactive and explicit invocation
- Need business integration (agent) + reusable resources (skill)
- Want automatic monitoring + manual deep-dive capability

**Same-Named Skill/Agent Pairs** - Differentiate triggers to avoid overlap:
- **Skill triggers**: Question words (what, how, which), reference terms (format, template, best practice)
- **Agent triggers**: Action words (create, build, update, implement, review)
- **Key principle**: Skills answer "what/how" questions; Agents execute "do this" requests
- See `references/agent-vs-skill-decision-guide.md` for full patterns and examples

### Summary Table

| Feature | Agent | Skill | Command |
|---------|-------|-------|---------|
| **Auto-Trigger** | Yes (semantic + "Use PROACTIVELY") | Yes (semantic matching) | No (manual only) |
| **Autonomous Delegation** | Yes | No | No |
| **Bundled Resources** | No | Yes | No |
| **TodoWrite** | Yes | No | No |
| **Business Context** | Yes | No | No |
| **Token Efficiency** | Lower | Higher | Highest |
| **File Structure** | Single | Multi-file | Single |

**Auto-Trigger Clarification:**
- **Skills**: Auto-trigger when Claude's semantic evaluation matches the description to user intent
- **Agents**: Auto-trigger via semantic matching PLUS "Use PROACTIVELY" signals Claude to delegate autonomously
- **Commands**: Manual invocation only (user must explicitly type /command-name)

## YAML Frontmatter Quick Reference

### Agent (Required)
```yaml
---
name: agent-name
description: [Specialization]. Use PROACTIVELY for [triggers].
model: sonnet  # Use aliases (opus/sonnet/haiku) - analyze task needs
---
```

### Skill (Required)
```yaml
---
name: skill-name
description: This skill should be used when [use cases].
---
```

### Command (Optional)
```yaml
---
allowed-tools: Tool(commands)
argument-hint: [format]
description: Brief purpose
---
```

## Review Checklist

### For Agents
- [ ] YAML front matter complete (name, description, model)
- [ ] Description includes "Use PROACTIVELY" if appropriate
- [ ] Model set using aliases (opus/sonnet/haiku) based on task analysis
- [ ] TodoWrite capability for complex operations
- [ ] MCP token limit strategies defined
- [ ] Escalation criteria clear

### For Skills
- [ ] YAML front matter complete (name, description)
- [ ] Description uses third-person voice
- [ ] Description includes trigger terms
- [ ] SKILL.md uses imperative/infinitive form
- [ ] Bundled resources properly organized
- [ ] References not duplicated in SKILL.md

### For Commands
- [ ] Natural language instructions clear and actionable
- [ ] Tool usage patterns specified
- [ ] $ARGUMENTS handling described
- [ ] Output requirements defined

## MCP Token Limits

**Critical Constraint**: All MCP tool responses capped at 25000 tokens maximum.

**Mitigation Strategies**:
- Use pagination and filtering
- Divide and conquer (smaller chunks)
- Smart search over broad retrieval
- Time-based chunking
- Never use full dataset dumps

## Platform Considerations

### Claude Desktop Path Requirements

Claude Desktop requires full executable paths (runs in sandbox without PATH):

```bash
# Find full path
which npx        # Returns: /opt/homebrew/bin/npx
which uv         # Returns: /Users/username/.local/bin/uv

# Use in config
"command": "/opt/homebrew/bin/npx"   # Correct
"command": "npx"                      # Will fail
```

## When to Use Skill vs Agent

**Use this skill (instruction-creator):**
- Quick reference for templates
- Creating a single instruction file
- Agent vs skill decision guidance
- Reviewing existing files

**Use instruction-creator agent:**
- Creating multiple related instruction files
- System-wide instruction optimization
- Complex architectural decisions across files
- Team distribution preparation (sanitization)
- MCP setup guide creation

## References

Detailed guides available in `references/` subdirectory:
- **agent-vs-skill-decision-guide.md**: Complete decision matrix with examples
- **yaml-frontmatter-complete-guide.md**: All valid fields and options
- **common-instruction-patterns.md**: Proven structures and templates
