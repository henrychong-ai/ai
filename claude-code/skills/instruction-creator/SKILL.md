---
name: instruction-creator
description: This skill should be used for quick reference and guidance about instruction files (CLAUDE.md, rules, agents, skills, slash commands). Use for questions about YAML frontmatter format, agent-vs-skill decisions, content placement (where should this go?), rules vs CLAUDE.md, token budgets, model configuration, templates, best practices, hooks, and cross-platform conversion. Provides loading hierarchy, decision matrices, 5-step skill workflow, and placement guidance. Triggers: "YAML frontmatter", "agent vs skill", "where should I put", "rules vs CLAUDE.md", "content placement", "token budget", "auto-loading", "instruction template", "context fork", "hooks", "team sharing", "sanitization". For actual creation/implementation, use the instruction-creator agent instead.
---

# Instruction Creator Skill

This skill provides complete guidance for creating and reviewing Claude instruction files across the entire instruction ecosystem.

**Updated:** 2026-01-20 (Claude Code v2.1.3+)

## Skills & Slash Commands Merge (v2.1.3)

As of Claude Code v2.1.3, **skills and slash commands have been merged** under a unified `Skill` tool:

- Both handled by the same underlying mechanism
- Skills visible in `/` menu by default (opt-out with `user-invocable: false`)
- Both can use `context: fork` and `agent` fields for isolated execution
- **Distinction is now purely organizational:**
  - **Skills**: Directory structure (SKILL.md + bundled resources)
  - **Commands**: Single .md files for quick prompts

## Instruction File Types

| Type | Location | Purpose | Loading |
|------|----------|---------|---------|
| **CLAUDE.md** | `~/.claude/` or `./` | User preferences, identity | Always (auto) |
| **Rules** | `~/.claude/rules/` or `./.claude/rules/` | Focused config, patterns | Always (auto) |
| **Agents** | `~/.claude/agents/*.md` | Autonomous domain specialists | On trigger/Task tool |
| **Skills** | `~/.claude/skills/*/SKILL.md` | Bundled knowledge packages | On `/skill-name` or Skill tool |
| **Commands** | `~/.claude/commands/*.md` | Natural language prompts | On `/command-name` |

**Key Distinction:**
- **Auto-loading** (CLAUDE.md, Rules): Always load every session - keep lean
- **On-demand** (Skills, Agents, Commands): Load when invoked - can be larger

## CLAUDE.md and Rules

### Auto-Loading Behavior

**Critical:** CLAUDE.md and rules files **always fully load** every session. There is no lazy loading or incremental loading for these files.

**Loading Order:**
1. Global CLAUDE.md (`~/.claude/CLAUDE.md`)
2. Global rules (`~/.claude/rules/**/*.md`)
3. Project CLAUDE.md (`./CLAUDE.md`)
4. Project rules (`./.claude/rules/**/*.md`)
5. CLAUDE.local.md (`./CLAUDE.local.md`) - gitignored
6. Nested subdirectory CLAUDE.md - only loads when navigated to that dir

**Token Budget Guidelines:**
| File Type | Recommended | Maximum |
|-----------|-------------|---------|
| Global CLAUDE.md | 800-1200 lines | ~1500 lines |
| Each rules file | 50-200 lines | ~300 lines |
| Project CLAUDE.md | 100-300 lines | ~500 lines |

### Rules Directory Patterns

```
~/.claude/rules/
├── environments/       # Cloud accounts, credentials, paths
│   ├── cloudflare.md
│   └── 1password.md
├── languages/          # Language conventions
└── tools/              # Tool-specific configs
```

**Benefits of Rules:**
- Organization by category
- Reusable across projects
- Selective team sharing
- Independent maintenance
- Override hierarchy (project > global)

### Content Placement Quick Guide

| Content | Location |
|---------|----------|
| Core identity/preferences | Global CLAUDE.md |
| Small cross-cutting config | `rules/environments/` |
| Large documentation | Skill `references/` |
| Project context | Project CLAUDE.md |
| Personal overrides | CLAUDE.local.md |

See `references/rules-and-content-placement-guide.md` for comprehensive guidance.

## Creating Agents

Agents are autonomous domain specialists with proactive operation capabilities.

### Agent YAML Frontmatter

**Required fields:**
```yaml
---
name: agent-name                    # Required: kebab-case identifier
description: Brief description...   # Required: include "Use PROACTIVELY" for auto-trigger
---
```

**Optional fields:**
```yaml
---
model: sonnet                       # opus/sonnet/haiku/inherit (default: sonnet)
tools: Read, Grep, Glob, Bash       # Tools agent can use (inherits all if omitted)
disallowedTools: Write, Edit        # Tools to explicitly deny
permissionMode: default             # default|acceptEdits|dontAsk|bypassPermissions|plan
skills: pr-review, security-check   # Skills to auto-load into agent context
hooks:                              # Lifecycle hooks (see Hooks section)
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./validate.sh"
---
```

### Model Configuration

- **Use aliases**: `opus`, `sonnet`, `haiku` (automatically use latest version)
- **`inherit`**: Inherit model from parent conversation
- **Priority order**: Task tool override → Agent YAML → Inherit → System default
- **Model capabilities**:
  - `opus`: Complex reasoning, strategic analysis, multi-step workflows
  - `sonnet`: General-purpose, balanced performance, technical tasks
  - `haiku`: Fast responses, simple patterns, high-volume tasks

### Agent Template Structure

```markdown
---
name: agent-name
description: [Specialization]. [Capabilities]. Use PROACTIVELY for [triggers].
model: sonnet
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
```

## Creating Skills

Skills are specialized knowledge packages with bundled resources using progressive disclosure.

### 5-Step Skill Creation Process

1. **Understand**: Clarify problem, triggers, success criteria, edge cases
2. **Name**: kebab-case, max 64 characters
3. **Description**: Third-person voice, concrete verbs, trigger terms (CRITICAL)
4. **Instructions**: Clear hierarchy with examples and error handling
5. **Package/Test**: Use validation scripts

### Skill YAML Frontmatter

**Required fields:**
```yaml
---
name: skill-name                    # Required: kebab-case, max 64 chars
description: This skill should...   # Required: third-person voice, max 1024 chars
---
```

**Optional fields:**
```yaml
---
allowed-tools: Read, Grep, Glob     # Tools without permission prompts
model: sonnet                       # Model override
context: fork                       # Run in isolated sub-agent context
agent: Explore                      # Agent type when context: fork is set
user-invocable: true                # Show in /menu (default: true)
disable-model-invocation: false     # Prevent Skill tool from calling (default: false)
hooks:                              # Lifecycle hooks
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./validate.sh"
          once: true                # Run once per session, then removed
---
```

### Context Fork Feature

Use `context: fork` to run skills in an **isolated sub-agent context**:

```yaml
---
name: code-analyzer
description: Analyze code patterns and generate reports
context: fork          # Isolated execution
agent: Explore         # Use fast read-only agent
---
```

**When to use `context: fork`:**
- Verbose output (test runs, large file analysis)
- Multi-step operations that would clutter context
- Complex workflows where only the summary matters

**Agent options for `context: fork`:**
| Agent | Model | Tools | Use Case |
|-------|-------|-------|----------|
| `Explore` | Haiku | Read-only | Fast analysis, file discovery |
| `Plan` | Sonnet | Read-only | Research before planning |
| `general-purpose` | Sonnet | All | Complex tasks with edits |
| Custom agent | Per config | Per config | Domain-specific work |

### Skill Directory Structure

```
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter (name, description - required)
│   └── Markdown instructions
└── Bundled Resources (optional)
    ├── references/ - Documentation loaded as needed (DEFAULT)
    ├── scripts/    - Executable code
    ├── templates/  - Variable substitution files
    └── assets/     - Static files
```

### Visibility Controls

| Field | Effect |
|-------|--------|
| `user-invocable: false` | Hide from /menu, still allows auto-discovery and Skill tool |
| `disable-model-invocation: true` | Block programmatic invocation via Skill tool |

## Creating Slash Commands

Slash commands are natural language instruction prompts (NOT executable code).

### Command YAML Frontmatter (All Optional)

```yaml
---
description: Brief command purpose
allowed-tools: Bash(git:*), Read
argument-hint: [pr-number] [priority]
model: sonnet
context: fork                       # Run in forked sub-agent context
agent: Explore                      # Agent type when context: fork
disable-model-invocation: false     # Prevent Skill tool from calling
hooks:                              # Lifecycle hooks
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./validate.sh"
---
```

### Command Template

```markdown
---
allowed-tools: Tool(specific-commands)
argument-hint: [format]
description: Brief command purpose
---

# Natural Language Instructions for Claude

[Specific behavior description]

## Input Processing
- $ARGUMENTS represents user input (substituted by Claude Code)
- Process $ARGUMENTS as [expected format/type]

## Tool Usage
- Use [specific tools] to [accomplish task]
- Load documentation from [paths] before execution

## Output Requirements
- Provide [specific format] as response
```

## Hooks in Frontmatter

Skills, Agents, and Commands all support lifecycle hooks:

### Supported Events

| Event | Purpose |
|-------|---------|
| `PreToolUse` | Before tool execution, can block or modify |
| `PostToolUse` | After tool completes successfully |
| `Stop` | When component finishes |

**Note:** For agents, `Stop` hooks become `SubagentStop` events.

### Hook Syntax

```yaml
hooks:
  PreToolUse:
    - matcher: "Bash"           # Tool pattern (regex supported)
      hooks:
        - type: command
          command: "./script.sh"
          once: true            # Skills/Commands only, not Agents
  PostToolUse:
    - matcher: "Edit|Write"
      hooks:
        - type: command
          command: "./lint.sh"
```

## Agent vs Skill Decision Matrix

### Quick Decision Framework

**Use Agent When:**
- Proactive operation with auto-triggering needed
- Complex autonomous decision-making required
- Multi-step workflows requiring TodoWrite
- Domain specialist needing continuous operation

**Use Skill When:**
- Explicit invocation preferred (`/skill-name`)
- Bundled resources needed (references, scripts)
- Progressive disclosure valuable
- Token efficiency through optional resource loading

**Use Command When:**
- Simple, single-step operations
- Natural language instructions sufficient
- Quick user-triggered workflows

**Use `context: fork` When:**
- Skill/command produces verbose output
- Complex multi-step operations
- Want isolated context for cleaner main conversation

### Summary Table

| Feature | Agent | Skill | Command |
|---------|-------|-------|---------|
| **Auto-Trigger** | Yes | Yes | No |
| **Bundled Resources** | No | Yes | No |
| **TodoWrite** | Yes | No | No |
| **context: fork** | N/A | Yes | Yes |
| **Token Efficiency** | Lower | Higher | Highest |
| **File Structure** | Single | Multi-file | Single |

## YAML Frontmatter Quick Reference

### Agent (Required: name, description)
```yaml
---
name: agent-name
description: [Specialization]. Use PROACTIVELY for [triggers].
model: sonnet
tools: Read, Grep, Glob, Bash
disallowedTools: Write, Edit
permissionMode: default
skills: skill-a, skill-b
hooks: {...}
---
```

### Skill (Required: name, description)
```yaml
---
name: skill-name
description: This skill should be used when [use cases].
allowed-tools: Read, Grep
model: sonnet
context: fork
agent: Explore
user-invocable: true
disable-model-invocation: false
hooks: {...}
---
```

### Command (All Optional)
```yaml
---
description: Brief purpose
allowed-tools: Tool(commands)
argument-hint: [format]
model: sonnet
context: fork
agent: general-purpose
disable-model-invocation: false
hooks: {...}
---
```

## Review Checklist

### For Agents
- [ ] YAML: name, description (model optional but recommended)
- [ ] Description includes "Use PROACTIVELY" if appropriate
- [ ] Model uses aliases (opus/sonnet/haiku)
- [ ] TodoWrite capability for complex operations
- [ ] MCP token limit strategies defined

### For Skills
- [ ] YAML: name, description (required)
- [ ] Description uses third-person voice
- [ ] Description includes trigger terms
- [ ] If using `agent` field, ensure `context: fork` is set
- [ ] Bundled resources properly organized

### For Commands
- [ ] Natural language instructions clear
- [ ] Tool usage patterns specified
- [ ] If using `agent` field, ensure `context: fork` is set

## MCP Token Limits

**Critical Constraint**: All MCP tool responses capped at 25000 tokens maximum.

**Mitigation Strategies**:
- Use pagination and filtering
- Divide and conquer (smaller chunks)
- Smart search over broad retrieval
- Never use full dataset dumps

## Platform Considerations

### Claude Desktop Path Requirements

Claude Desktop requires full executable paths (runs in sandbox):

```bash
which npx        # Returns: /opt/homebrew/bin/npx

# Use in config
"command": "/opt/homebrew/bin/npx"   # Correct
"command": "npx"                      # Will fail
```

## When to Use Skill vs Agent

**Use this skill (instruction-creator):**
- Quick reference for templates and frontmatter
- Creating a single instruction file
- Agent vs skill decision guidance
- Reviewing existing files

**Use instruction-creator agent:**
- Creating multiple related instruction files
- System-wide instruction optimization
- Complex architectural decisions
- Team distribution preparation (sanitization)
- MCP setup guide creation

## References

Detailed guides in `references/` subdirectory:
- **yaml-frontmatter-complete-guide.md**: All valid fields and options (COMPREHENSIVE)
- **agent-vs-skill-decision-guide.md**: Complete decision matrix for agents vs skills
- **rules-and-content-placement-guide.md**: CLAUDE.md, rules, skills placement decisions (NEW)
- **common-instruction-patterns.md**: Proven structures and templates
- **cross-platform-conversion-guide.md**: Claude Code → Claude.ai conversion

## Scripts

Utility scripts in `scripts/` subdirectory:
- **init_skill.py**: Initialize a new skill directory structure
- **package_skill.py**: Package skill for distribution
- **quick_validate.py**: Validate skill structure and YAML
- **convert_to_claudeai.py**: Convert Claude Code skill to Claude.ai format
