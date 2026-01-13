# YAML Frontmatter Complete Guide

**Comprehensive reference for all instruction file YAML frontmatter fields**
**Updated: 2026-01-13 (Claude Code v2.1.3+)**

---

## Skills & Slash Commands Merge (v2.1.3)

As of Claude Code v2.1.3, **skills and slash commands have been merged** under a unified `Skill` tool. This simplifies the mental model with no change in actual behavior:

- Both are now handled by the same underlying mechanism
- Skills are visible in the `/` menu by default (opt-out with `user-invocable: false`)
- Both can use `context: fork` and `agent` fields for isolated execution
- The distinction is now purely organizational:
  - **Skills**: Directory structure with SKILL.md + bundled resources
  - **Slash Commands**: Single .md files for quick prompts

---

## Agent Front Matter

**Location:** `~/.claude/agents/*.md`

### Complete Field Reference

```yaml
---
name: agent-name                    # Required: kebab-case identifier
description: Brief description...   # Required: specialization + when to use
model: sonnet                       # Optional: use aliases (opus/sonnet/haiku/inherit)
tools: Read, Grep, Glob, Bash       # Optional: tools agent can use (inherits all if omitted)
disallowedTools: Write, Edit        # Optional: tools to explicitly deny
permissionMode: default             # Optional: default|acceptEdits|dontAsk|bypassPermissions|plan
skills: pr-review, security-check   # Optional: skills to auto-load into agent context
hooks:                              # Optional: lifecycle hooks scoped to agent
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./validate.sh"
  PostToolUse:
    - matcher: "Edit|Write"
      hooks:
        - type: command
          command: "./lint.sh"
  Stop:
    - hooks:
        - type: command
          command: "./cleanup.sh"
---
```

### Field Specifications

#### `name` (Required)
- **Format:** kebab-case (lowercase with hyphens)
- **Purpose:** Agent identifier, must match filename
- **Examples:** `compliance-officer`, `typescript`, `code-reviewer`
- **Rules:** No spaces, no underscores, max 64 characters

#### `description` (Required)
- **Format:** Single paragraph, 1-3 sentences
- **Purpose:** Agent capabilities and when to use
- **Pattern:** "[Specialization]. [Capabilities]. Use PROACTIVELY for [triggers]."
- **Examples:**
  - `"TypeScript specialist with advanced type system mastery. Use PROACTIVELY for fintech TypeScript optimization."`
  - `"Code review expert. Reviews for quality, security, maintainability. Use PROACTIVELY for PR reviews."`

#### `model` (Optional)
- **Format:** Model alias or full ID
- **Purpose:** Specifies Claude model for agent execution
- **Values:** `opus`, `sonnet`, `haiku`, `inherit` (from parent)
- **Default:** `sonnet` if not specified
- **Best Practice:** Use aliases for automatic version updates

**Priority Order:**
1. Task tool `model` parameter (explicit override)
2. Agent YAML `model` field
3. `inherit` from parent conversation
4. System default (sonnet)

#### `tools` (Optional)
- **Format:** Comma-separated string or YAML list
- **Purpose:** Specify which tools the agent can use
- **Default:** Inherits all tools if omitted
- **Examples:**
  ```yaml
  tools: Read, Grep, Glob, Bash
  # or YAML list:
  tools:
    - Read
    - Grep
    - Glob
    - Bash
  ```

#### `disallowedTools` (Optional)
- **Format:** Comma-separated string or YAML list
- **Purpose:** Explicitly deny specific tools (removed from inherited or specified list)
- **Examples:**
  ```yaml
  disallowedTools: Write, Edit
  # or:
  disallowedTools:
    - Write
    - Edit
  ```

#### `permissionMode` (Optional)
- **Format:** String enum
- **Purpose:** Set permission mode for agent execution
- **Values:**
  - `default` - Standard permission prompts
  - `acceptEdits` - Auto-accept file edits
  - `dontAsk` - Skip most permission prompts
  - `bypassPermissions` - Skip all permission checks
  - `plan` - Plan mode (read-only research)
- **Default:** `default`

#### `skills` (Optional)
- **Format:** Comma-separated string or YAML list
- **Purpose:** Skills to load into agent context at startup (full content injected)
- **Note:** Different from tools - these are skills whose instructions become part of agent context
- **Examples:**
  ```yaml
  skills: pr-review, security-check
  # or:
  skills:
    - pr-review
    - security-check
  ```

#### `hooks` (Optional)
- **Format:** YAML object with hook events
- **Purpose:** Define lifecycle hooks scoped to agent
- **Supported Events:** `PreToolUse`, `PostToolUse`, `Stop`
- **Note:** `Stop` hooks are automatically converted to `SubagentStop` events for agents
- **See:** Hooks Reference section below

---

## Skill Front Matter

**Location:** `~/.claude/skills/*/SKILL.md`

### Complete Field Reference

```yaml
---
name: skill-name                    # Required: kebab-case identifier
description: This skill should...   # Required: third-person usage description
allowed-tools: Read, Grep, Glob     # Optional: tools Claude can use without permission
model: sonnet                       # Optional: model override for skill execution
context: fork                       # Optional: run in isolated sub-agent context
agent: Explore                      # Optional: agent type when context: fork (requires context: fork)
user-invocable: true                # Optional: show in /menu (default: true)
disable-model-invocation: false     # Optional: prevent Skill tool from calling (default: false)
hooks:                              # Optional: lifecycle hooks scoped to skill
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./validate.sh"
          once: true
---
```

### Field Specifications

#### `name` (Required)
- **Format:** kebab-case (lowercase with hyphens)
- **Purpose:** Skill identifier, matches parent directory name
- **Examples:** `pdf`, `xlsx`, `travel`, `instruction-creator`
- **Rules:** No spaces, no underscores, max 64 characters

#### `description` (Required)
- **Format:** Third-person voice, 1-3 sentences, max 1024 chars
- **Purpose:** What skill does and when to use it (Claude uses this for auto-discovery)
- **Pattern:** "This skill should be used when [use cases]. [Capabilities]. [Special triggers]."
- **Voice:** Always third-person ("This skill should be used when...")

#### `allowed-tools` (Optional)
- **Format:** Comma-separated string or YAML list
- **Purpose:** Tools Claude can use without asking permission when skill is active
- **Examples:**
  ```yaml
  allowed-tools: Read, Grep, Glob
  # or with patterns:
  allowed-tools: Bash(python:*), Bash(git:*)
  # or YAML list:
  allowed-tools:
    - Read
    - Grep
    - Glob
    - Bash(python:*)
  ```

#### `model` (Optional)
- **Format:** Model alias or full ID
- **Purpose:** Override model when skill is active
- **Values:** `opus`, `sonnet`, `haiku`

#### `context` (Optional)
- **Format:** String
- **Purpose:** Set to `fork` to run skill in isolated sub-agent context
- **Value:** `fork` (only valid value)
- **Benefits:**
  - Keeps verbose output in separate context
  - Enables complex workflows without cluttering main conversation
  - Only summary/result returned to main conversation

#### `agent` (Optional)
- **Format:** Agent type identifier
- **Purpose:** Specify which agent type to use when `context: fork` is set
- **Requirement:** Only works when `context: fork` is also set
- **Values:**
  - `Explore` - Fast read-only analysis (Haiku)
  - `Plan` - Research and planning (Sonnet)
  - `general-purpose` - Full capability (Sonnet)
  - Custom agent name from `~/.claude/agents/`
- **Default:** `general-purpose` if not specified

#### `user-invocable` (Optional)
- **Format:** Boolean
- **Purpose:** Controls whether skill appears in `/` slash command menu
- **Values:** `true` (default) or `false`
- **Note:** Setting to `false` hides from menu but still allows:
  - Automatic discovery based on description
  - Programmatic invocation via `Skill` tool

#### `disable-model-invocation` (Optional)
- **Format:** Boolean
- **Purpose:** Prevents the `Skill` tool from calling this skill programmatically
- **Values:** `true` or `false` (default)
- **Use Case:** Skills that should only be manually invoked

#### `hooks` (Optional)
- **Format:** YAML object with hook events
- **Purpose:** Define lifecycle hooks scoped to skill
- **Supported Events:** `PreToolUse`, `PostToolUse`, `Stop`
- **Special:** Supports `once: true` option (runs hook once per session, then removed)
- **See:** Hooks Reference section below

---

## Slash Command Front Matter

**Location:** `~/.claude/commands/*.md`

### Complete Field Reference

```yaml
---
description: Brief command purpose      # Optional: command description
allowed-tools: Bash(git:*), Read        # Optional: restrict tool access
argument-hint: [pr-number] [priority]   # Optional: guide expected parameters
model: sonnet                           # Optional: specific model
context: fork                           # Optional: run in forked sub-agent context
agent: Explore                          # Optional: agent type when context: fork
disable-model-invocation: false         # Optional: prevent Skill tool from calling
hooks:                                  # Optional: lifecycle hooks
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./validate.sh"
          once: true
---
```

### Field Specifications

#### `description` (Optional)
- **Format:** Brief sentence
- **Purpose:** Organizational metadata shown in command help
- **Examples:** `"Create a git commit"`, `"Search knowledge graph"`

#### `allowed-tools` (Optional)
- **Format:** Tool name pattern string or YAML list
- **Purpose:** Restricts which tools command can use
- **Examples:**
  ```yaml
  allowed-tools: Bash(git:*), Read
  # or YAML list:
  allowed-tools:
    - Bash(git:*)
    - Read
    - Write
  ```

#### `argument-hint` (Optional)
- **Format:** Free-text hint string
- **Purpose:** Guide users on expected argument format (shown in autocomplete)
- **Examples:** `"[city]"`, `"[pr-number] [priority] [assignee]"`

#### `model` (Optional)
- **Format:** Model alias or full ID
- **Purpose:** Override default model for command
- **Values:** `opus`, `sonnet`, `haiku`

#### `context` (Optional)
- **Format:** String
- **Purpose:** Set to `fork` to run command in isolated sub-agent context
- **Value:** `fork`

#### `agent` (Optional)
- **Format:** Agent type identifier
- **Purpose:** Specify which agent type to use when `context: fork` is set
- **Requirement:** Only works when `context: fork` is also set
- **Values:** `Explore`, `Plan`, `general-purpose`, or custom agent name
- **Default:** `general-purpose`

#### `disable-model-invocation` (Optional)
- **Format:** Boolean
- **Purpose:** Prevents the `Skill` tool from calling this command programmatically
- **Values:** `true` or `false` (default)

#### `hooks` (Optional)
- **Format:** YAML object with hook events
- **Purpose:** Define lifecycle hooks scoped to command
- **Supported Events:** `PreToolUse`, `PostToolUse`, `Stop`
- **Special:** Supports `once: true` option
- **See:** Hooks Reference section below

---

## Hooks Frontmatter Reference

Skills, Agents, and Slash Commands all support hooks in frontmatter. Hooks are scoped to the component's lifecycle and auto-cleanup when the component finishes.

### Supported Events

| Event | Component Support | Purpose |
|-------|-------------------|---------|
| `PreToolUse` | Skills, Agents, Commands | Before tool execution, can block or modify |
| `PostToolUse` | Skills, Agents, Commands | After tool completes successfully |
| `Stop` | Skills, Agents, Commands | When component finishes |

**Note:** For agents, `Stop` hooks are automatically converted to `SubagentStop` events.

### Hook Syntax

```yaml
hooks:
  PreToolUse:
    - matcher: "Bash"           # Tool name pattern to match
      hooks:
        - type: command         # Hook type
          command: "./script.sh" # Command to run
          once: true            # Optional: run only once per session (Skills/Commands only)
  PostToolUse:
    - matcher: "Edit|Write"     # Regex pattern matching
      hooks:
        - type: command
          command: "./lint.sh"
  Stop:
    - hooks:
        - type: command
          command: "./cleanup.sh"
```

### Hook Options

| Option | Type | Description |
|--------|------|-------------|
| `matcher` | string | Tool name pattern (regex supported) |
| `type` | string | Hook type: `command` |
| `command` | string | Shell command to execute |
| `once` | boolean | Run hook only once per session (Skills/Commands only, not Agents) |

### Examples

**Validation before Bash commands:**
```yaml
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/validate-command.sh"
          once: true
```

**Linting after file edits:**
```yaml
hooks:
  PostToolUse:
    - matcher: "Edit|Write"
      hooks:
        - type: command
          command: "npm run lint"
```

---

## Project Instructions Front Matter

**Location:** Project root or docs directory

```yaml
---
file_type: project_instructions     # Type identifier
version: 1.0                         # Semantic version
last_updated: YYYY-MM-DD            # Last modification date
platform_compatibility: both        # desktop | code | both
business_domain: domain_name        # Business area
token_estimate: ~4000               # Approximate token count
---
```

---

## Context Fork + Agent Decision Tree

```
Is your skill/command doing complex work?
├─ YES: Use context: fork
│   ├─ Read-only analysis? → agent: Explore (fast, Haiku)
│   ├─ Complex with edits? → agent: general-purpose (full capability)
│   └─ Specialized domain? → agent: your-custom-agent
│
└─ NO: Skip context: fork (run in main conversation)
```

**When to use `context: fork`:**
- Verbose output (test runs, large file analysis)
- Multi-step operations that would clutter context
- Operations that benefit from isolated context window
- Complex workflows where only the summary matters

---

## Quick Reference Tables

### Agent Fields Summary

| Field | Required | Default | Description |
|-------|----------|---------|-------------|
| `name` | Yes | - | kebab-case identifier |
| `description` | Yes | - | Specialization + "Use PROACTIVELY" |
| `model` | No | `sonnet` | opus/sonnet/haiku/inherit |
| `tools` | No | All | Tools agent can use |
| `disallowedTools` | No | None | Tools to deny |
| `permissionMode` | No | `default` | Permission behavior |
| `skills` | No | None | Skills to auto-load |
| `hooks` | No | None | Lifecycle hooks |

### Skill Fields Summary

| Field | Required | Default | Description |
|-------|----------|---------|-------------|
| `name` | Yes | - | kebab-case identifier |
| `description` | Yes | - | Third-person usage description |
| `allowed-tools` | No | None | Tools without permission |
| `model` | No | Inherit | Model override |
| `context` | No | None | `fork` for isolation |
| `agent` | No | `general-purpose` | Agent type (requires context: fork) |
| `user-invocable` | No | `true` | Show in /menu |
| `disable-model-invocation` | No | `false` | Block programmatic invocation |
| `hooks` | No | None | Lifecycle hooks |

### Command Fields Summary

| Field | Required | Default | Description |
|-------|----------|---------|-------------|
| `description` | No | - | Command description |
| `allowed-tools` | No | All | Tool restrictions |
| `argument-hint` | No | - | Expected parameters |
| `model` | No | Inherit | Model override |
| `context` | No | None | `fork` for isolation |
| `agent` | No | `general-purpose` | Agent type (requires context: fork) |
| `disable-model-invocation` | No | `false` | Block programmatic invocation |
| `hooks` | No | None | Lifecycle hooks |

---

## Validation Checklist

**For Agents:**
- [ ] `name`: kebab-case, matches filename
- [ ] `description`: includes specialization + "Use PROACTIVELY" + triggers
- [ ] `model`: Use aliases (opus/sonnet/haiku) not version numbers

**For Skills:**
- [ ] `name`: kebab-case, matches directory name
- [ ] `description`: third-person voice, explains when to use
- [ ] If using `agent` field, ensure `context: fork` is also set

**For Commands:**
- [ ] All fields optional (YAML frontmatter is metadata only)
- [ ] If using `agent` field, ensure `context: fork` is also set

**For All:**
- [ ] Valid YAML syntax (proper indentation, quoting)
- [ ] No duplicate fields
- [ ] Proper date formats (YYYY-MM-DD)

---

**Last Updated:** 2026-01-13
**Claude Code Version:** 2.1.3+
