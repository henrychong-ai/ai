# Instruction Creation Checklists & Frameworks

Comprehensive checklists for file type selection, integration requirements, model selection, skill directory behaviour mapping, and sanitisation.

**Updated:** 2026-09-24b (agent MUST list: contract + leaf-worker spawn bar replace TodoWrite). 2026-09-24 (Model × Effort section: Opus 5.5, harness vs recommended default, built-in agent models)

---

## File Type Selection Matrix

Detailed guidance for choosing where content belongs. Each entry shows what SHOULD and SHOULD NOT go in that file type.

### Global CLAUDE.md (`~/.claude/CLAUDE.md`)
- **DO**: Cross-session technical preferences, universal tool policies, MCP token limit strategies, agent creation standards, directory structures
- **DON'T**: Business-specific context, domain expertise, identity/philosophy (belongs in master instruction file)

### Rules (`~/.claude/rules/**/*.md`)
- **DO**: Small cross-cutting config, environment credentials, language conventions, tool-specific patterns
- **DON'T**: Large documentation (use skill references), core identity (use CLAUDE.md)

### Project Instructions (`project-instructions.md`)
- **DO**: Business-specific context, strategic priorities, company goals, revenue optimisation, platform adaptation, escalation criteria
- **DON'T**: Technical tool usage (reference global CLAUDE.md), universal identity principles

### Project Index (`project-index.md`)
- **DO**: Business intelligence routing, quick decision matrices, token-efficient access patterns, smart document routing
- **DON'T**: Comprehensive business context (belongs in project instructions), detailed technical procedures

### Agent (`~/.claude/agents/*.md`)
- **DO**: Autonomous domain specialists, specialised expertise with tool access, complex multi-step operations, proactive operation with escalation criteria
- **DON'T**: Simple command workflows (use commands), universal technical capabilities (reference CLAUDE.md)

### Skill (`~/.claude/skills/*/SKILL.md`)
- **DO**: Bundled knowledge packages with reusable resources, progressive disclosure, explicit invocation, bundled scripts/references/assets, token-efficient resource loading
- **DON'T**: Content that should auto-load every session (use rules/CLAUDE.md)

### Command (`~/.claude/commands/*.md`)
- **DO**: Clear natural language instructions, specific tool usage guidance, workflow descriptions, user experience specifications, error handling descriptions
- **DON'T**: Complex autonomous decision-making (use agents), executable code (commands are instruction prompts)

---

## Integration Requirements

### All Agents MUST:
- [ ] Reference appropriate project-instructions.md for business context
- [ ] State the operating contract: inputs, approval boundary, and the report returned to the caller
- [ ] Leaf workers: bar `Agent`/`Task` via `disallowedTools`, or list an explicit `tools:` allowlist
- [ ] Specify MCP token limit strategies
- [ ] Define escalation criteria for human review

### All Skills MUST:
- [ ] Include YAML frontmatter with `name` and `description` (required fields)
- [ ] Use third-person voice in description ("This skill should be used when...")
- [ ] Use imperative/infinitive writing style in instructions
- [ ] Keep SKILL.md body under 5k tokens for efficiency
- [ ] Organise bundled resources properly (references/, scripts/, templates/, assets/)
- [ ] Create references/ by default; other subdirs only when needed (YAGNI)
- [ ] Include specific trigger terms in description for activation
- [ ] If using `agent` field, ensure `context: fork` is also set
- [ ] No skill version numbers in SKILL.md (body or frontmatter `metadata.version`) — skills are versioned via git, not embedded strings. Tool/library versions referenced in content are fine.
- [ ] **Have a non-empty body** (the instructions/router loaded on invocation). **NEVER regenerate a SKILL.md from frontmatter alone** — editing a frontmatter field (e.g. token-optimising `description`) must preserve the body. Verify the body-line-count survives any edit; `scripts/quick_validate.py` FAILS on an empty body. Full rule + safe bulk-edit protocol: `references/skill-edit-safety.md`.

### All Skills SHOULD:
- [ ] Test with 3 scenarios: normal, edge cases, out-of-scope
- [ ] Use progressive disclosure (load resources only when needed)
- [ ] Avoid duplicating info between SKILL.md and references/
- [ ] Include concrete examples and usage patterns
- [ ] Use `context: fork` for verbose/complex operations
- [ ] Consider `user-invocable: false` for utility skills that should auto-trigger only

### All Skills MAY:
- [ ] Include `allowed-tools` to specify tools that don't require permission
- [ ] Include `model` to override the model when skill is active
- [ ] Include `context: fork` with `agent` for isolated execution
- [ ] Include `hooks` for lifecycle validation
- [ ] Include `disable-model-invocation: true` to prevent programmatic calls

### All Commands MUST:
- [ ] Provide clear, unambiguous natural language instructions
- [ ] Specify exact tool usage patterns and documentation loading requirements
- [ ] Define user experience expectations and behavioural specifications
- [ ] Include error handling descriptions and fallback strategies
- [ ] Define success criteria and output format requirements

### All Commands MAY:
- [ ] Include YAML frontmatter for organisational metadata
- [ ] Specify tool restrictions via `allowed-tools` field
- [ ] Include argument hints and enhanced UX specifications
- [ ] Include `context: fork` with `agent` for isolated execution
- [ ] Include `hooks` for lifecycle validation
- [ ] Include `model` to override the model for command execution

---

## Model × Effort Selection Analysis Framework

Model and effort are **one joint decision**, not two — effort labels are model-relative (Opus 5.5 at `medium`, its default, matches or beats Opus 5 at `high`; Fable 5.1 at `medium` scores about level with Fable 5 at `xhigh` on FrontierCode at roughly half the cost per task). **Recommended default:** `model: opus` on agents and `context: fork` skills; no `model` on main-thread skills and commands; omit `effort` unless a specific level is needed. The **harness default** when `model` is omitted is the main conversation's model (subagents) or the session model (skills), not a fixed tier.

### 5-Point Analysis
For each new agent/skill, evaluate:
1. **Complexity Level**: Simple patterns vs multi-step reasoning
2. **Decision-Making Needs**: Rule-based vs judgment-based
3. **Context Requirements**: Small focused tasks vs large context analysis
4. **Performance Needs**: Speed-critical vs quality-critical (Fable's first token can still take ~a minute on 5.1 — capability and latency trade off explicitly)
5. **Cost Considerations**: Usage frequency and budget (Opus 5.5 is $4/$20 with cache reads $0.20; Fable 5.1 is $10/$50, 2.5× Opus 5.5 per token, with cache reads $0.25. Fable 5.1 was measured cheaper per task than Opus 5 at low to high effort on coding; that comparison predates Opus 5.5, so measure cost per task, not per token)

### Model Capabilities
| Model | Strengths | Use When |
|-------|-----------|----------|
| `fable` | Frontier reasoning, hardest long-horizon/agentic work, first-shot correctness on complex problems | Genuinely hard, latency-tolerant work where capability dominates; 2.5× Opus 5.5 per token (measured cheaper per task than Opus 5 at low to high effort on coding; re-measure against Opus 5.5); cache reads $0.25/MTok on 5.1; slow first token |
| `opus` | Complex reasoning, strategic analysis, nuanced judgment, multi-step workflows, agentic coding and review (Opus 5.5 from CC 2.1.280) | **Recommended default for authored agents and forked skills**; compliance analysis, strategic planning, architectural decisions; routine traffic that still needs depth |
| `sonnet` | General-purpose, balanced performance, most technical tasks | Code generation, code review, general technical work |
| `haiku` | Fast responses, simple patterns, rule-based operations, high-volume | File format detection, batch processing, quick lookups |

### Joint Model × Effort Routing
| Dominant constraint | Pick |
|---|---|
| Capability ceiling, latency-tolerant | Fable 5.1 at `high` (default) — and note `fable` at `medium`/`low` can beat `opus` at `xhigh`, often at lower cost per task |
| Latency-sensitive / interactive | `opus` or smaller — Opus 5.5 outputs over 30% faster than Opus 5; Fable 5.1 is still slow to first token at any effort |
| Routine high-volume | `opus` / `sonnet` / `haiku` per the rows above — official routing: hard, long-horizon jobs → Fable 5.1; routine traffic → Opus-or-smaller. Opus 5.5 at `low`/`medium` is the cost-efficient workhorse point; Fable 5.1 at `low`/`medium` still belongs in the cost-per-task comparison |
| **Cache safety (mid-session)** | Pins are cache-safe only in subagent contexts — the CC cache is keyed by model and, on most models, effort, so a main-thread skill/command pin double cache-busts the session (an effort-only change keeps the cache on Opus 5.5 and Fable 5.1 on first-party auth; a model change never does). Agents: safe by construction. Pinned skills/commands: MUST set `context: fork`. Detail: `cache-and-token-efficiency.md` |

### Model Priority Order (highest to lowest)
1. **Per-invocation `model` parameter** (Agent tool) - explicit override at invocation
2. **Agent YAML `model` field** - default in file (`inherit` selects the main conversation's model)
3. **`CLAUDE_CODE_SUBAGENT_MODEL`** - operator-set default, when present
4. **Main conversation's model** - harness default when nothing else applies

### Built-in Agent Models (verified 2026-09-24 against code.claude.com/docs/en/sub-agents)
| Agent | Model | Note |
|-------|-------|------|
| Explore | Inherits main model, capped at Opus on the Claude API | Haiku before v2.1.198; define a user/project `Explore` with `model: haiku` to keep it cheap |
| Plan | Inherits main model | Read-only research in plan mode |
| general-purpose | `CLAUDE_CODE_SUBAGENT_MODEL` if set, else main model | Full tool set |
| claude | No model of its own; follows the subagent model order | Catch-all |
| statusline-setup | Sonnet | `/statusline` |
| claude-code-guide | Haiku | Claude Code feature questions |

Built-in definitions are not editable. To pin a built-in's model or effort, define a user or project agent of the same name, which overrides it (documented for Explore).

### Best Practices
- Use aliases (`opus`, `fable`, `sonnet`, `haiku`) not version numbers; `opus` is the recommended default for authored agents
- Aliases automatically use latest model version
- Document model selection rationale in design notes
- When a pin is justified, record the effort decision with it (joint decision — see routing table above)
- Note: If agent specifies `model: opus`/`model: fable` but the user lacks access to that tier, behaviour may be inconsistent

---

## Skill Directory Behavioural Mapping

Each bundled resource directory maps to a distinct Claude behaviour:

| Directory | Behaviour | Claude Action |
|-----------|----------|---------------|
| `references/` | READ | Load into context for knowledge |
| `scripts/` | EXECUTE | Run code directly |
| `templates/` | TRANSFORM | Substitute variables, then output |
| `assets/` | USE AS-IS | Copy/reference without modification |

**Default subdirectory policy:**
- `references/` - Always created by default (most skills need documentation)
- `scripts/`, `templates/`, `assets/` - Created incrementally only when needed (YAGNI)

---

## Sanitisation System

For transforming personal/proprietary instruction files into team-ready versions.

### Sanitisation Taxonomy

**Personal Identity Elements (Remove/Transform):**
- Personal names and pronouns
- Amplified personal messaging
- Identity-specific success metrics
- Personal communication styles

**Proprietary Methodology (Strip):**
- Named personal optimisation frameworks (life-area systems, identity engines, etc.)
- Personal philosophical frameworks
- Personal optimisation protocols
- Proprietary decision-making frameworks

(For concrete before/after string-substitution examples, see the Pattern Library below — those illustrate the conversion mechanics with sample phrasings.)

**Path and System (Generalise/Remove):**
- Personal directory paths → Generic examples or removal
- Local system configurations
- Cloud drive paths and proprietary storage
- Identity-specific trigger words

**Communication Style (Normalise):**
- Remove amplified enthusiasm
- Replace inspirational messaging with professional standards
- Convert personal metrics to generic business criteria
- Standardise to universal team applicability

### Sanitisation Process (4 Phases)

**Phase 1: Pre-Sanitisation Analysis**
1. Extract core technical functionality and business value
2. Catalogue all personal references, paths, and methodologies
3. Document technical capabilities that must be preserved
4. Note architectural references that need updating

**Phase 2: Content Transformation**
1. Remove personal references and amplified messaging
2. Replace proprietary frameworks with standard business practices
3. Convert personal paths to generic examples
4. Standardise tone for team use

**Phase 3: Technical Preservation**
1. Validate all technical capabilities remain intact
2. Confirm architectural compliance and reference integrity
3. Test operational protocols and tool usage patterns
4. Preserve token efficiency and execution standards

**Phase 4: Team Distribution Preparation**
1. Apply consistent business-focused messaging
2. Ensure universal applicability across team members
3. Verify all necessary operational guidance included
4. Final review for team-ready presentation

### Pattern Library

```
# Identity
"[personal] ecosystem" → "Claude instruction ecosystem"
"You are an expert [role]" → "You are an expert instruction architect"

# Paths
"/Users/username/..." → [Remove or convert to generic example]
"mb: {documentation directory}" → "mb: {project documentation directory}"

# Methodology
"Custom auto-activation sequence" → "Professional auto-activation sequence"
"Life area optimisation" → "Business area optimisation"
"Strategic objective alignment" → "Business objective alignment"

# Communication
"Energy that ignites..." → "Clear and systematic..."
"amplified intelligence" → "enhanced productivity"
```

### Sanitisation QA Checklist
- [ ] All personal references removed or generalised
- [ ] Proprietary methodologies stripped or replaced
- [ ] Professional communication tone throughout
- [ ] Core technical functionality preserved
- [ ] Business applicability confirmed
- [ ] Team distribution readiness verified
