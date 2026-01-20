# Discovery Workflow

Interactive process for creating new Gemini gems from requirements.

## Phase 1: Requirements Discovery

### Opening Approach

Start with:
> "Let's create a custom gem together. Tell me: What problem should this gem solve, or what task should it help you accomplish?"

### Discovery Questions

Ask one at a time, follow up based on answers:

**Purpose & Objective:**
- "What problem should this gem solve?"
- "What task should it help you accomplish?"
- "Can you give me 2-3 concrete examples of how you'd use this?"

**Domain & Expertise:**
- "What domain knowledge or expertise does the gem need?"
- "What specific frameworks, regulations, or standards are relevant?"
- "What industry-specific terminology should it understand?"

**Audience & Users:**
- "Who will use this gem? What's their role?"
- "What's their expertise level in this domain?"
- "How familiar are they with technical concepts?"

**Output & Deliverables:**
- "What should the output look like?"
- "Any specific format or structure requirements?"
- "What elements must be included in every response?"
- "Are there word limits or length requirements?"

**Context & Constraints:**
- "What business context does the gem need to understand?"
- "Are there regulatory requirements or compliance considerations?"
- "Any brand guidelines or communication standards?"
- "What constraints should I know about?"

**Quality & Success:**
- "How will you know if the gem is working well?"
- "What makes a good output for this task?"
- "Are there examples of desired output you can share?"

### Discovery Principles

- Ask follow-up questions based on answers
- Seek concrete examples over abstract descriptions
- Push for specificity when answers are vague
- Confirm understanding before proceeding to building

---

## Phase 2: Component Construction

Build each component systematically using discovery information.

### PERSONA Construction Sequence

1. **Define Role**: Extract from domain and expertise needs
2. **List Expertise**: Compile specific knowledge areas mentioned
3. **Set Tone**: Determine from audience and use cases
4. **Specify Audience**: Clarify from user requirements
5. **Validate**: Ensure role is specific, expertise clear, tone appropriate

### TASK Construction Sequence

1. **State Objective**: Convert problem/need to primary objective
2. **List Actions**: Extract specific actions as numbered list
3. **Define Success**: Establish criteria from quality requirements
4. **Set Standards**: Specify performance expectations
5. **Validate**: Ensure actions are specific, deliverables clear, success measurable

### CONTEXT Construction Sequence

1. **Business Background**: Incorporate company context (Fusang/Portcullis if applicable)
2. **Regulatory Framework**: Include relevant regulations and standards
3. **Audience Details**: Specify user characteristics and needs
4. **Constraints**: Define limits and requirements
5. **Validate**: Ensure sufficient context for independent gem operation

### FORMAT Construction Sequence

1. **Define Structure**: Establish sections and organization
2. **Set Length**: Specify word counts or page limits
3. **List Elements**: Identify required components
4. **Style Guidelines**: Detail tone, voice, language level
5. **Validate**: Ensure format supports task, is specific, enables consistency

### Presentation

Present draft to user:

> "Here's a draft of your gem instructions. Review this and let me know what needs adjustment:"

```
---BEGIN GEM INSTRUCTIONS---

PERSONA:
[Complete persona section]

TASK:
[Complete task section with numbered actions]

CONTEXT:
[Complete context section]

FORMAT:
[Complete format section]

---END GEM INSTRUCTIONS---
```

---

## Phase 3: Refinement & Iteration

### Refinement Questions

Ask:
> "What would you like to change or improve? Consider:
> - Is the persona's expertise and tone right for your users?
> - Are the tasks specific enough? Too broad? Too narrow?
> - Is there missing context that would make responses more relevant?
> - Does the format match what you need?"

### Common Refinement Areas

1. **Persona Adjustments**: Tone too formal/casual, expertise too broad/narrow
2. **Task Clarification**: Actions need more specificity, scope too wide
3. **Context Additions**: Missing regulatory frameworks, insufficient business background
4. **Format Tweaks**: Structure modifications, length adjustments, style changes

### Iteration Process

1. User identifies what needs improvement
2. Make targeted adjustments to specific component
3. Present refined version
4. Repeat until user satisfied

---

## Phase 4: Quality Validation

### Apply 5-Quality-Test Framework

**1. Specificity Test**
- Question: "Could someone else read these instructions and know exactly what this gem should do?"
- Assessment: Pass if all components have clear, unambiguous instructions

**2. Consistency Test**
- Question: "If you use this gem 10 times, will you get consistent output structure and quality?"
- Assessment: Pass if format and standards produce predictable results

**3. Differentiation Test**
- Question: "Is this gem noticeably different from generic Gemini?"
- Assessment: Pass if domain knowledge and specialization evident

**4. Usability Test**
- Question: "Can you describe concrete scenarios where you'd use this gem right now?"
- Assessment: Pass if clear use cases exist and gem serves real need

**5. Completeness Test**
- Question: "Does the gem have all information needed to operate standalone?"
- Assessment: Pass if can function without additional context

### Validation Output

```
### Quality Assessment
✅ Specificity Test: [Pass/Needs work - explanation]
✅ Consistency Test: [Pass/Needs work - explanation]
✅ Differentiation Test: [Pass/Needs work - explanation]
✅ Usability Test: [Pass/Needs work - explanation]
✅ Completeness Test: [Pass/Needs work - explanation]
```

**Pass Criteria:** All 5 tests must pass for gem to be ready for team distribution.

---

## Completion

Present final gem with:
- Complete instructions ready to copy
- File attachment recommendations (if applicable)
- Quality assessment against 5 tests
- Usage scenarios
- Next steps for implementation

### Final Output Format

```markdown
# Gemini Custom Gem: [Name]
*Created for: [Team/Purpose]*
*Domain: [Category]*

## Gem Description
[1-2 sentences for Gemini description field]

## Quality Assessment
[5-test results table]

## Usage Scenarios
1. [Scenario with input/output]
2. [Scenario with input/output]
3. [Scenario with input/output]

## Recommended Attachments
[Files to attach, or "None needed"]

## Gem Instructions
---BEGIN GEM INSTRUCTIONS---
[Complete 4-component instructions]
---END GEM INSTRUCTIONS---

## Next Steps
1. Copy gem instructions to Gemini
2. Attach recommended files (if any)
3. Test with sample prompts
4. Use magic wand to expand if needed
5. Share with team via Google Workspace
```
