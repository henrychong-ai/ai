# Creating Fillable PDF Forms from Scratch

This guide covers creating interactive PDF forms with clickable checkboxes and typeable text fields using reportlab's AcroForm module.

## Prerequisites

```bash
# Install reportlab
uv tool run --with reportlab python3 script.py
# OR
pip install reportlab
```

## Basic Setup

```python
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import black, white
from reportlab.pdfgen import canvas

def create_fillable_form(filename):
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    form = c.acroForm  # Access AcroForm for interactive fields

    # Your form code here

    c.save()
```

## Interactive Checkboxes

```python
form.checkbox(
    name='checkbox_name',      # Unique identifier
    x=100,                     # X position (points from left)
    y=700,                     # Y position (points from bottom)
    size=12,                   # Checkbox size in points
    buttonStyle='check',       # Style: 'check', 'cross', 'circle', 'star', 'diamond'
    borderColor=black,
    fillColor=white,
    textColor=black,
    forceBorder=True           # Always show border
)
```

### Checkbox Tips
- Position checkbox slightly below text baseline: `y=y_pos - 1`
- Common size: 12 points
- Place label text after checkbox: `c.drawString(checkbox_x + 15, y_pos, "Label")`

## Interactive Text Fields

### Inline Text Fields (Single Line)

```python
form.textfield(
    name='field_name',         # Unique identifier
    x=left_margin + 100,       # X position after label
    y=y_pos - 4,               # Slightly below baseline for alignment
    width=200,                 # Field width in points
    height=16,                 # Standard single-line height
    borderStyle='underlined',  # Shows underline only
    borderColor=black,
    fillColor=white,
    textColor=black,
    forceBorder=True
)
```

### Multi-line Text Fields (Text Areas)

```python
form.textfield(
    name='multiline_field',
    x=left_margin,
    y=y_pos - box_height,      # Position is BOTTOM of field
    width=515,
    height=60,                 # Taller for multiple lines
    borderStyle='inset',       # Box with inset border
    borderColor=black,
    fillColor=white,
    textColor=black,
    forceBorder=True,
    fieldFlags='multiline'     # Enable multi-line input
)
```

### borderStyle Options

| Style | Use Case |
|-------|----------|
| `'underlined'` | Inline fields next to labels (Name: _______) |
| `'inset'` | Multi-line text boxes with visible boundaries |
| `'bevelled'` | 3D raised appearance |
| `'solid'` | Simple solid border |

## Y-Coordinate Management

**Critical**: PDF coordinates have y=0 at the BOTTOM of the page.

```python
# Start from top
top_margin = height - 0.5 * inch
y_pos = top_margin

# Move DOWN the page by SUBTRACTING
y_pos -= line_spacing  # Move down one line

# For multi-line fields, position is the BOTTOM of the field
form.textfield(
    y=y_pos - field_height,  # Bottom of field
    height=field_height
)
y_pos -= field_height + gap  # Update position after field
```

### Common Spacing Values

```python
line_spacing = 0.28 * inch    # Standard line height (~20 points)
section_spacing = 0.28 * inch  # Full line between sections
field_height = 16              # Single-line field height
checkbox_size = 12             # Standard checkbox size
```

## Dynamic Space Calculation

Fill available page space with proportionally-sized boxes:

```python
# Calculate available space
bottom_margin = 0.5 * inch
available_space = y_pos - bottom_margin

# Account for labels, gaps, and section spacing
label_overhead = 14  # Label text height
gap_after_label = 4
section_spacing = 0.28 * inch
num_sections = 4

total_overhead = num_sections * (section_spacing + label_overhead + gap_after_label)
total_overhead += (num_sections - 1) * inter_section_gap  # Gaps between boxes

# Calculate box heights
field_space = available_space - total_overhead
box_height = field_space / num_sections  # Equal distribution

# Or proportional distribution
box1_height = field_space * 0.25
box2_height = field_space * 0.35  # Larger box
box3_height = field_space * 0.20
box4_height = field_space * 0.20
```

## Complete Example: Form with Mixed Fields

```python
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import black, white
from reportlab.pdfgen import canvas

def create_sample_form(filename):
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    form = c.acroForm

    left_margin = 0.5 * inch
    top_margin = height - 0.5 * inch
    y_pos = top_margin
    line_spacing = 0.28 * inch
    field_height = 16
    checkbox_size = 12

    # Title
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(width / 2, y_pos, "SAMPLE FORM")
    y_pos -= 0.5 * inch

    # Inline text field
    c.setFont("Helvetica", 10)
    c.drawString(left_margin, y_pos, "Name:")
    form.textfield(name='name', x=left_margin + 45, y=y_pos - 4,
                   width=200, height=field_height, borderStyle='underlined',
                   borderColor=black, fillColor=white, textColor=black,
                   forceBorder=True)
    y_pos -= line_spacing

    # Checkboxes
    c.drawString(left_margin, y_pos, "Status:")
    checkbox_x = left_margin + 50
    for label, name in [('Active', 'cb_active'), ('Inactive', 'cb_inactive')]:
        form.checkbox(name=name, x=checkbox_x, y=y_pos - 1,
                      size=checkbox_size, buttonStyle='check',
                      borderColor=black, fillColor=white, textColor=black,
                      forceBorder=True)
        c.drawString(checkbox_x + 15, y_pos, label)
        checkbox_x += 80
    y_pos -= line_spacing * 1.5

    # Multi-line field with label above
    c.setFont("Helvetica-Bold", 10)
    c.drawString(left_margin, y_pos, "Comments:")
    y_pos -= 0.05 * inch
    multiline_height = 80
    form.textfield(name='comments', x=left_margin, y=y_pos - multiline_height,
                   width=515, height=multiline_height, borderStyle='inset',
                   borderColor=black, fillColor=white, textColor=black,
                   forceBorder=True, fieldFlags='multiline')

    c.save()
    print(f"Created: {filename}")

if __name__ == "__main__":
    create_sample_form("/tmp/sample-fillable-form.pdf")
```

## Best Practices

### Field Naming
- Use unique, descriptive names: `participant_name`, `cb_married`, `comments_section`
- Prefix checkboxes with `cb_` for clarity

### Layout
- Keep consistent margins (typically 0.5 inch)
- Use consistent line spacing throughout
- Add section spacing (full line) between logical groups
- Label multi-line fields ABOVE the field, inline fields BESIDE the field

### Alignment
- Inline fields: `y=y_pos - 4` aligns field baseline with text
- Checkboxes: `y=y_pos - 1` centers checkbox with text
- Multi-line: Position is bottom of field, so `y=y_pos - field_height`

### Space Optimization
- Calculate available space dynamically to fill pages
- Use proportional sizing for variable content areas
- Keep footer margin (~0.5 inch) for page numbers

## Troubleshooting

### Checkboxes not clickable
- Ensure using `acroForm.checkbox()`, not `canvas.rect()`
- `canvas.rect()` draws static graphics only

### Field appears in wrong position
- Remember y=0 is at BOTTOM of page
- Multi-line field y position is the BOTTOM of the field

### Text overlaps with field
- Adjust y offset: `y=y_pos - 4` for text fields
- Add gap after label before field: `y_pos -= 0.05 * inch`

### Fields run off page
- Calculate available space before placing fields
- Use dynamic height calculation based on remaining space

## Creating Blank Templates from Filled-In Examples

This workflow covers how to create a new blank fillable PDF form when you only have filled-in examples as reference.

### When to Use This Workflow

- You have filled-in PDF samples but no blank template
- The original blank form is unavailable or doesn't exist
- You need to create an interactive version of a static filled form
- Converting paper forms to digital fillable formats

### Overview: Reverse-Engineering Process

```
Filled PDF Examples → Analysis → Design → Implementation → Validation
```

### Phase 1: Analyze the Filled Examples

#### Visual Analysis
1. **Open filled PDFs** using native PDF reader or pdfplumber
2. **Identify form structure**:
   - Headers and titles (static text)
   - Labels for fields (static text)
   - Filled-in content (will become interactive fields)
   - Checkboxes (may appear as filled squares, X marks, or checkmarks)
   - Sections and logical groupings

#### Extract Text for Structure Mapping
```python
import pdfplumber

with pdfplumber.open("filled_example.pdf") as pdf:
    for i, page in enumerate(pdf.pages):
        print(f"=== Page {i+1} ===")
        text = page.extract_text()
        print(text)
```

#### Key Questions to Answer
- What are the static labels? (Keep as `c.drawString()`)
- What is filled-in content? (Convert to `acroForm.textfield()`)
- Where are checkboxes? (Convert to `acroForm.checkbox()`)
- What's the page layout? (Margins, columns, spacing)
- How many pages? (Plan multi-page structure)

### Phase 2: Design the Form Structure

#### Map Content Types

| Filled Content | Interactive Replacement |
|----------------|------------------------|
| Handwritten text on lines | `textfield(borderStyle='underlined')` |
| Text in boxes | `textfield(borderStyle='inset')` |
| Checked/filled squares | `checkbox(buttonStyle='check')` |
| Circled options | `checkbox()` or radio buttons |
| Multi-line paragraphs | `textfield(fieldFlags='multiline')` |

#### Sketch the Layout
1. Note approximate positions of each element
2. Identify consistent margins and spacing
3. Group related fields into sections
4. Plan y-coordinate progression (top to bottom)

### Phase 3: Implementation

#### Basic Template Structure
```python
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import black, white
from reportlab.pdfgen import canvas

def create_blank_form(filename):
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    form = c.acroForm

    # Margins
    left_margin = 0.5 * inch
    right_margin = width - 0.5 * inch
    top_margin = height - 0.5 * inch

    # Start position
    y_pos = top_margin
    line_spacing = 0.28 * inch

    # --- Replicate structure from filled example ---

    # Static header (copy exact text from filled example)
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(width / 2, y_pos, "FORM TITLE")
    y_pos -= 0.5 * inch

    # Inline field (where filled example had handwritten text)
    c.setFont("Helvetica", 10)
    c.drawString(left_margin, y_pos, "Name:")
    form.textfield(
        name='name',
        x=left_margin + 45,
        y=y_pos - 4,
        width=200,
        height=16,
        borderStyle='underlined',
        borderColor=black,
        fillColor=white,
        textColor=black,
        forceBorder=True
    )
    y_pos -= line_spacing

    # Checkboxes (where filled example had checked boxes)
    c.drawString(left_margin, y_pos, "Status:")
    checkbox_x = left_margin + 50
    for label, name in [('Option A', 'cb_a'), ('Option B', 'cb_b')]:
        form.checkbox(
            name=name,
            x=checkbox_x,
            y=y_pos - 1,
            size=12,
            buttonStyle='check',
            borderColor=black,
            fillColor=white,
            textColor=black,
            forceBorder=True
        )
        c.drawString(checkbox_x + 15, y_pos, label)
        checkbox_x += 80
    y_pos -= line_spacing

    # Multi-line box (where filled example had paragraph text)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(left_margin, y_pos, "Comments:")
    y_pos -= 0.05 * inch
    box_height = 60
    form.textfield(
        name='comments',
        x=left_margin,
        y=y_pos - box_height,
        width=515,
        height=box_height,
        borderStyle='inset',
        borderColor=black,
        fillColor=white,
        textColor=black,
        forceBorder=True,
        fieldFlags='multiline'
    )

    c.save()
    print(f"Created: {filename}")
```

### Phase 4: Validation

#### Compare Against Original
1. **Visual comparison**: Open side-by-side with filled example
2. **Field positioning**: Check alignment matches original layout
3. **Interactive testing**: Click all checkboxes, type in all fields
4. **Print test**: Ensure printed output matches original format

#### Common Adjustments
- **Spacing too tight/loose**: Adjust `line_spacing` and `section_spacing`
- **Fields misaligned**: Fine-tune y-offsets (`y=y_pos - 4` for text fields)
- **Checkboxes wrong size**: Adjust `size` parameter (standard: 12 points)
- **Text boxes too small**: Increase `height` for multiline fields

### Real-World Example: DWD Summary Form

This workflow was used to create a blank fillable "Date With Destiny Participant Summary" form from filled-in examples:

1. **Analysis**: Two filled examples showed different participant archetypes
2. **Structure identified**:
   - 2-page form with headers, footers, page numbers
   - Mix of inline fields (Name, Team Number)
   - Multiple checkbox groups (Relationship Status, R/A, K/P)
   - Large multi-line sections (Outcomes, Key Leverage, Wounds)
   - Three-column Triad section
3. **Implementation**:
   - Used `acroForm.textfield(borderStyle='underlined')` for inline fields
   - Used `acroForm.textfield(borderStyle='inset', fieldFlags='multiline')` for boxes
   - Used `acroForm.checkbox()` for all checkbox groups
   - Dynamic space calculation to fill each page optimally
4. **Result**: Fully interactive blank template matching original layout

### Key Insights

1. **Static vs Interactive**: `canvas.rect()` draws static graphics; `acroForm.checkbox()` creates clickable fields
2. **Position from filled content**: Use filled-in text positions to place interactive fields
3. **Preserve exact labels**: Copy static text verbatim from filled examples
4. **Match visual appearance**: Aim for printed blank to look identical to original format
5. **Test interactivity**: Verify all fields work in standard PDF readers (Preview, Adobe, browsers)
