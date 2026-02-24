# Instruction Creation Checklists & Frameworks

Comprehensive checklists for file type selection, integration requirements, model selection, skill directory behaviour mapping, and sanitisation.

**Updated:** 2026-02-24

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
- [ ] Include TodoWrite capability for complex operations
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

## Model Selection Analysis Framework

### 5-Point Analysis
For each new agent/skill, evaluate:
1. **Complexity Level**: Simple patterns vs multi-step reasoning
2. **Decision-Making Needs**: Rule-based vs judgment-based
3. **Context Requirements**: Small focused tasks vs large context analysis
4. **Performance Needs**: Speed-critical vs quality-critical
5. **Cost Considerations**: Usage frequency and budget constraints

### Model Capabilities
| Model | Strengths | Use When |
|-------|-----------|----------|
| `opus` | Complex reasoning, strategic analysis, nuanced judgment, multi-step workflows | Compliance analysis, strategic planning, architectural decisions |
| `sonnet` | General-purpose, balanced performance, most technical tasks | Code generation, code review, general technical work |
| `haiku` | Fast responses, simple patterns, rule-based operations, high-volume | File format detection, batch processing, quick lookups |

### Model Priority Order (highest to lowest)
1. **Task tool `model` parameter** - explicit override at invocation
2. **Agent/Skill YAML `model` field** - default in file
3. **Inherit from parent** - if neither specified
4. **System default** - fallback

### Built-in Agent Defaults
| Agent | Default Model | Rationale |
|-------|---------------|-----------|
| Explore | haiku | Fast searches, read-only |
| Plan | sonnet | Capable analysis |
| general-purpose | sonnet | Complex reasoning |
| claude-code-guide | haiku | Quick lookups |

### Best Practices
- Use aliases (`opus`, `sonnet`, `haiku`) not version numbers
- Aliases automatically use latest model version
- Document model selection rationale in design notes
- Note: If agent specifies `model: opus` but user lacks Opus access, behaviour may be inconsistent

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
- Personal methodology frameworks and life area optimisation
- Personal philosophical frameworks
- Personal optimisation protocols
- Proprietary decision-making frameworks

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
