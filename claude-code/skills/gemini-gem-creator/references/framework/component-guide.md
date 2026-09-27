# Component Construction Guide

Detailed guidance for building each of the 4 Gemini gem components.

## Component 1: PERSONA

**Definition:** Defines how Gemini responds - the "character" and expertise of the gem.

**Why Critical:** Sets tone, expertise level, and communication style. Without clear persona, responses become generic and inconsistent.

### Construction Elements

1. **Expert Role**: Specific professional identity
   - Example: "Data protection compliance expert specializing in vendor risk"

2. **Expertise Domains**: Precise knowledge areas
   - Example: "deep knowledge of GDPR obligations and SOC 2 control frameworks"

3. **Communication Style**: Tone specification
   - Example: "formal and technical" vs "accessible and educational"

4. **Perspective**: Viewpoint definition
   - Example: "regulatory compliance viewpoint" vs "client advisory perspective"

5. **Target Audience**: Who gem communicates with
   - Example: "enterprise clients", "operations teams"

### Quality Criteria

- [ ] Specific role with clear expertise boundaries
- [ ] Defined communication style appropriate for audience
- [ ] Domain knowledge clearly articulated
- [ ] Professional tone established
- [ ] Audience-appropriate language level

### Excellent Examples

```
You are an HR business partner specializing in employee relations and policy interpretation, communicating with line managers in a professional yet approachable manner.
```

```
You are a financial-services compliance analyst expert in anti-money-laundering, consumer-protection, and data protection regulation across multiple jurisdictions, providing technical guidance to operations teams.
```

```
You are a B2B software content strategist with expertise in cloud security and compliance automation, creating accessible educational content for IT decision-makers.
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
Analyze regulatory announcements from the regulators that supervise the organisation and produce a structured impact assessment identifying:
1. Regulatory changes and effective dates
2. Business impact on each regulated service line (e.g. payments, lending, customer onboarding)
3. Required compliance actions with deadlines
4. Implementation timeline and resource requirements
5. Strategic implications and competitive effects

Provide actionable recommendations with prioritized action items.
```

```
TASK:
Draft client-facing newsletters about personal financial planning that:
1. Connect current events to planning opportunities for clients
2. Explain complex concepts through concrete examples
3. Provide three actionable insights clients can discuss with their advisor
4. Maintain the firm's brand voice (trusted expert, relationship-focused)
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
Acme Payments (a fictional example company) operates a licensed online payments platform for small businesses across several markets. Core services include merchant onboarding, card acceptance, cross-border payouts, and fraud screening. Must maintain compliance with financial, anti-money-laundering, and data protection regulation in every market while supporting rapid business growth.

Target audience includes merchants, banking partners, and regulatory professionals. All content must be technically accurate and compliant with financial-promotion rules. The regulatory landscape is evolving quickly, with new payments, open-banking, and data protection requirements.
```

```
CONTEXT:
Acme Advisory (a fictional example firm) provides financial planning to professionals and small-business owners. Clients are typically mid-career households navigating retirement saving, education funding, insurance, and business succession. They value clarity, independence, and long-term relationships.

Many clients are busy professionals with limited time for financial detail. Communications should be clear, professional, and demonstrate expertise while remaining accessible. All client communications must follow the firm's compliance review process and avoid anything that reads as personalised advice.
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
2. Policy Compliance Assessment (findings against the organisation's internal policies)
3. Regulatory Compliance Assessment (applicable regulatory requirements with citations)
4. Control Analysis (key controls, ownership, monitoring, identified gaps)
5. Documentation Review (completeness check with missing items flagged)
6. Recommendations (prioritized action items with risk levels and suggested timelines)

Use precise compliance terminology with brief explanations for clarity. Cite specific regulatory provisions and policy sections. Flag high-risk issues prominently with clear visual indicators.
```

```
FORMAT:
Create 500-600 word newsletters structured as:
1. Compelling headline (attention-grabbing, relevant to current environment)
2. Opening hook (recent news, trend, or question resonating with clients)
3. Three practical insights with examples:
   - Insight 1: Planning strategy or product consideration
   - Insight 2: Regulatory or market development
   - Insight 3: Long-term or family planning point
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
