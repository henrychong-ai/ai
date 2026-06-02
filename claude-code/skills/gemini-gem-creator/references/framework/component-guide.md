# Component Construction Guide

Detailed guidance for building each of the 4 Gemini gem components.

## Component 1: PERSONA

**Definition:** Defines how Gemini responds - the "character" and expertise of the gem.

**Why Critical:** Sets tone, expertise level, and communication style. Without clear persona, responses become generic and inconsistent.

### Construction Elements

1. **Expert Role**: Specific professional identity
   - Example: "Shariah compliance expert specializing in sukuk structures"

2. **Expertise Domains**: Precise knowledge areas
   - Example: "deep knowledge of AAOIFI standards and Malaysian sukuk market practices"

3. **Communication Style**: Tone specification
   - Example: "formal and technical" vs "accessible and educational"

4. **Perspective**: Viewpoint definition
   - Example: "regulatory compliance viewpoint" vs "client advisory perspective"

5. **Target Audience**: Who gem communicates with
   - Example: "high-net-worth clients", "operations teams"

### Quality Criteria

- [ ] Specific role with clear expertise boundaries
- [ ] Defined communication style appropriate for audience
- [ ] Domain knowledge clearly articulated
- [ ] Professional tone established
- [ ] Audience-appropriate language level

### Excellent Examples

```
You are a Singapore-licensed trust professional specializing in family office succession planning, communicating with high-net-worth clients in a professional yet approachable manner.
```

```
You are a digital securities compliance analyst expert in Labuan FSA, Hong Kong SFC, and Singapore MAS regulations, providing technical guidance to operations teams.
```

```
You are an Islamic finance content strategist with expertise in sukuk tokenization and Shariah compliance, creating accessible educational content for institutional investors.
```

### Common Mistakes

- Vague personas: "You are a helpful assistant"
- Missing expertise domains
- Undefined communication style
- No audience specification

---

## Component 2: TASK

**Definition:** The specific objective the gem helps users accomplish.

**Why Critical:** Guides what Gemini produces. Vague tasks produce vague results.

### Construction Elements

1. **Primary Objective**: Clear statement of main purpose
2. **Specific Actions**: Numbered list of concrete actions (not vague "help with")
3. **Scope Definition**: What to include and exclude
4. **Success Criteria**: What makes a good output
5. **Quality Standards**: Performance expectations
6. **Step-by-Step Workflow**: Process when applicable

### Quality Criteria

- [ ] Extremely specific about actions (analyze, draft, review, synthesize, compare, structure)
- [ ] Clear boundaries and scope
- [ ] Measurable success criteria
- [ ] Actionable deliverables defined
- [ ] Single focused purpose (not multiple unrelated tasks)

### Excellent Examples

```
TASK:
Analyze regulatory announcements from MAS, SFC, or Labuan FSA and produce a structured impact assessment identifying:
1. Regulatory changes and effective dates
2. Business impact on exchange operations, custody services, and tokenization platform
3. Required compliance actions with deadlines
4. Implementation timeline and resource requirements
5. Strategic implications and competitive effects

Provide actionable recommendations with prioritized action items.
```

```
TASK:
Draft client-facing newsletters about trust services and estate planning that:
1. Connect current events to wealth planning opportunities
2. Explain complex concepts through concrete examples
3. Provide three actionable insights families can discuss with advisors
4. Maintain Portcullis brand voice (trusted expert, relationship-focused)
5. End with clear call-to-action

Target 500-600 words, accessible to non-experts, professional yet warm tone.
```

### Common Mistakes

- Generic tasks: "help with work" or "answer questions"
- No clear deliverables
- Trying to do multiple unrelated things
- Vague action verbs without specificity

---

## Component 3: CONTEXT

**Definition:** Background information helping gem understand environment, constraints, and expectations.

**Why Critical:** Provides domain knowledge and situational awareness making responses relevant and accurate.

### Construction Elements

1. **Industry-Specific Knowledge**: Domain frameworks, principles, regulations
2. **Company-Specific Context**: Brand voice, strategic priorities, compliance requirements
3. **Audience Characteristics**: Expertise level, role, information needs
4. **Constraints and Requirements**: Word limits, regulatory considerations, confidentiality
5. **Operating Environment**: Multi-jurisdiction, regulatory landscape, business model
6. **Strategic Positioning**: Market position, competitive advantages, brand values

### Quality Criteria

- [ ] Rich domain knowledge provided
- [ ] Company positioning and values clear
- [ ] Audience needs and expertise level specified
- [ ] Key constraints and requirements defined
- [ ] Regulatory frameworks detailed when applicable
- [ ] Sufficient context for gem to operate independently

### Excellent Examples

```
CONTEXT:
Fusang operates a Labuan FSA-licensed digital securities exchange with specialized focus on Islamic finance and sukuk tokenization. Core services include the IILM sukuk marketplace, crypto trading, and Vault custody. Must maintain compliance across multiple jurisdictions (Labuan FSA, Hong Kong SFC, Singapore MAS) while supporting rapid business growth.

Target audience includes institutional investors, Islamic financial institutions, and regulatory professionals. All content must be technically accurate, Shariah-aware, and compliant with securities regulations. Regulatory landscape evolving quickly with new digital asset frameworks and Islamic finance guidelines.
```

```
CONTEXT:
Portcullis Group serves ultra-high-net-worth families across Singapore, Hong Kong, Malaysia, BVI, and Cook Islands. Clients are typically multi-generational families navigating cross-border wealth transfer, succession planning, asset protection, and family governance. They value discretion, expertise, and long-term relationships.

Many clients are business owners, senior executives, or inheritors managing significant family wealth. Communications should be discreet, professional, and demonstrate deep technical expertise while remaining accessible. Regulatory environment includes Singapore trust laws, Hong Kong estate planning frameworks, and offshore jurisdiction structures.
```

### Common Mistakes

- No context provided
- Generic context applying to any business
- Missing key constraints or requirements
- Insufficient domain knowledge for effective operation

---

## Component 4: FORMAT

**Definition:** How the gem should structure output and what elements to include.

**Why Critical:** Ensures consistency and makes outputs immediately usable.

### Construction Elements

1. **Structure Specification**: Sections, headers, organization
2. **Length Constraints**: Word limits, page counts, character limits
3. **Required Elements**: Headers, citations, disclaimers, specific components
4. **Style Guidelines**: Active vs passive voice, technical vs accessible language
5. **Visual Organization**: How content should be presented for readability
6. **Completeness Criteria**: What must be included for output to be complete

### Quality Criteria

- [ ] Clear structure defined
- [ ] Length constraints specified
- [ ] Required elements listed
- [ ] Style guidelines detailed
- [ ] Format supports task objectives
- [ ] Consistency across multiple uses ensured

### Excellent Examples

```
FORMAT:
Provide a structured compliance review report:
1. Executive Summary (2-3 sentences: compliance status with HIGH/MEDIUM/LOW designation)
2. Shariah Compliance Assessment (analysis of riba, gharar, halal backing with specific findings)
3. Regulatory Compliance Assessment (Labuan FSA and relevant jurisdiction requirements with citations)
4. Structural Analysis (SPV structure, asset ownership, profit distribution mechanisms, identified risks)
5. Documentation Review (completeness check with missing items flagged)
6. Recommendations (prioritized action items with risk levels and suggested timelines)

Use technical Islamic finance terminology with brief explanations for clarity. Cite specific AAOIFI standards and regulatory provisions. Flag high-risk issues prominently with clear visual indicators.
```

```
FORMAT:
Create 500-600 word newsletters structured as:
1. Compelling headline (attention-grabbing, relevant to current environment)
2. Opening hook (recent news, trend, or question resonating with families)
3. Three practical insights with examples:
   - Insight 1: Trust structure or planning strategy
   - Insight 2: Cross-border consideration or recent development
   - Insight 3: Family governance or succession planning point
4. Real-world anonymized case study or example
5. Clear call-to-action (schedule review, discuss with advisor, attend event)

Use accessible business language avoiding excessive jargon. When technical terms necessary, provide brief explanations. Maintain professional tone while being conversational. Use "you" and "your family" to personalize.
```

### Common Mistakes

- No format specification
- Vague instructions: "make it look good"
- Format conflicting with task goals
- No length constraints
- Missing required elements specification

---

## Component Integration Checklist

Before finalizing any gem:

- [ ] PERSONA has specific role, not just "assistant"
- [ ] TASK has numbered actions, not just "help with"
- [ ] CONTEXT includes company and regulatory details
- [ ] FORMAT specifies output structure
- [ ] All four components work together coherently
- [ ] No contradictions between components
