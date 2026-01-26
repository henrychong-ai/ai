# Renaming PDF Form Fields for Programmatic Filling

## Overview

PDF forms often have non-descriptive field names like "Text Field 20242" or "Check Box 16" which make programmatic filling difficult. This guide covers how to rename generic field names to semantic names (like `participant_name`, `cb_married`) using pikepdf, enabling easy programmatic form filling.

## When to Use This Guide

Use this technique when:
- You have a PDF form with generic/auto-generated field names
- You need to fill the form programmatically multiple times
- You want human-readable field names for maintainability
- You're building automation pipelines for form filling

## Prerequisites

```bash
uv pip install pikepdf
```

## The 4-Step Process

### Step 1: Extract Field Positions

First, extract all field names and their positions to understand what fields exist:

```python
import pikepdf

pdf = pikepdf.open("form.pdf")
for page_num, page in enumerate(pdf.pages, 1):
    if "/Annots" in page:
        for annot in page.Annots:
            field_type = str(annot.get("/FT", ""))  # /Tx = text, /Btn = checkbox
            field_name = str(annot.get("/T", ""))
            rect = annot.get("/Rect", None)  # [x1, y1, x2, y2] coordinates
            if rect:
                coords = [float(x) for x in rect]
                # y coordinate helps identify vertical position on page
                print(f"Page {page_num}: {field_name} ({field_type}): y={coords[3]:.1f}, x={coords[0]:.1f}")
```

**Output example:**
```
Page 1: Text Field 20242 (/Tx): y=720.5, x=150.0
Page 1: Text Field 20243 (/Tx): y=680.2, x=150.0
Page 1: Check Box 16 (/Btn): y=640.0, x=50.0
```

### Step 2: Create Verification PDF

Fill each field with its ID (or a portion of it) to visually identify which field is which:

```python
import pikepdf

pdf = pikepdf.open("form.pdf")
for page in pdf.pages:
    if "/Annots" in page:
        for annot in page.Annots:
            field_name = str(annot.get("/T", ""))
            field_type = str(annot.get("/FT", ""))

            if field_type == "/Tx":  # Text field
                # Show last 5 chars of field name (fits in most fields)
                annot["/V"] = pikepdf.String(field_name[-5:])
                # Force PDF viewer to redraw the field with new value
                if "/AP" in annot:
                    del annot["/AP"]
            elif field_type == "/Btn":  # Checkbox
                annot["/V"] = pikepdf.Name("/Yes")
                annot["/AS"] = pikepdf.Name("/Yes")

pdf.save("test_mapping.pdf")
```

**Result:** Open `test_mapping.pdf` to see each text field displaying its ID fragment (e.g., "20242") and all checkboxes checked. Cross-reference with the form layout to create your mapping.

### Step 3: Create Mapping and Rename Fields

Create a mapping dictionary and apply the renames:

```python
import pikepdf

# Map old generic names to semantic names
field_mapping = {
    # Text fields - use snake_case
    "Text Field 20242": "participant_name",
    "Text Field 20243": "date_of_birth",
    "Text Field 20244": "annual_income",

    # Checkboxes - use cb_ prefix
    "Check Box 16": "cb_single",
    "Check Box 17": "cb_married",
    "Check Box 18": "cb_divorced",

    # Grouped fields - use common prefix
    "Text Field 30001": "contact_email",
    "Text Field 30002": "contact_phone",
    "Text Field 30003": "contact_address",
}

pdf = pikepdf.open("form.pdf")
renamed_count = 0

for page in pdf.pages:
    if "/Annots" in page:
        for annot in page.Annots:
            old_name = str(annot.get("/T", ""))
            if old_name in field_mapping:
                new_name = field_mapping[old_name]
                annot["/T"] = pikepdf.String(new_name)
                print(f"Renamed: {old_name} -> {new_name}")
                renamed_count += 1

pdf.save("form_semantic.pdf")
print(f"\nTotal fields renamed: {renamed_count}")
```

### Step 4: Validate Renamed PDF

Verify all fields were renamed correctly:

```python
import pikepdf

pdf = pikepdf.open("form_semantic.pdf")
print("Field inventory after renaming:\n")

for page_num, page in enumerate(pdf.pages, 1):
    if "/Annots" in page:
        for annot in page.Annots:
            field_type = str(annot.get("/FT", ""))
            field_name = str(annot.get("/T", ""))
            type_label = "TEXT" if field_type == "/Tx" else "CHECKBOX" if field_type == "/Btn" else field_type
            print(f"Page {page_num}: [{type_label}] {field_name}")
```

**Expected output:**
```
Field inventory after renaming:

Page 1: [TEXT] participant_name
Page 1: [TEXT] date_of_birth
Page 1: [TEXT] annual_income
Page 1: [CHECKBOX] cb_single
Page 1: [CHECKBOX] cb_married
Page 1: [CHECKBOX] cb_divorced
```

## Naming Conventions

### Recommended Patterns

| Field Type | Convention | Examples |
|------------|------------|----------|
| Checkboxes | `cb_` prefix | `cb_married`, `cb_us_citizen`, `cb_agree_terms` |
| Text fields | snake_case | `participant_name`, `annual_income`, `email_address` |
| Date fields | `_date` suffix | `birth_date`, `submission_date` |
| Grouped fields | common prefix | `address_line1`, `address_line2`, `address_city` |
| Section fields | section prefix | `section1_name`, `section2_total` |

### Naming Tips

1. **Be descriptive but concise**: `participant_name` not `the_name_of_the_participant`
2. **Use consistent casing**: Always snake_case for readability
3. **Group related fields**: Use common prefixes for fields that belong together
4. **Indicate field purpose**: `cb_` for checkboxes makes type immediately clear
5. **Match form layout**: Name fields in order they appear (top-to-bottom, left-to-right)

## Key pikepdf Operations Reference

### Reading Field Properties

```python
annot.get("/T")      # Field name (e.g., "/T" = Title)
annot.get("/FT")     # Field type: /Tx (text), /Btn (checkbox/radio)
annot.get("/V")      # Current value
annot.get("/Rect")   # Position: [x1, y1, x2, y2]
annot.get("/AP")     # Appearance stream (visual rendering)
```

### Writing Field Properties

```python
# Set field name
annot["/T"] = pikepdf.String("new_field_name")

# Fill text field
annot["/V"] = pikepdf.String("field value")
if "/AP" in annot:
    del annot["/AP"]  # Force redraw

# Check checkbox
annot["/V"] = pikepdf.Name("/Yes")
annot["/AS"] = pikepdf.Name("/Yes")  # Appearance state

# Uncheck checkbox
annot["/V"] = pikepdf.Name("/Off")
annot["/AS"] = pikepdf.Name("/Off")
```

### Field Type Reference

| `/FT` Value | Type | Notes |
|-------------|------|-------|
| `/Tx` | Text field | Single or multi-line text input |
| `/Btn` | Button | Checkboxes, radio buttons, push buttons |
| `/Ch` | Choice | Dropdown or list selection |
| `/Sig` | Signature | Digital signature field |

## Complete Workflow Example

Here's a complete script that combines all steps:

```python
#!/usr/bin/env python3
"""
Rename PDF form fields from generic names to semantic names.
Usage: python rename_fields.py input.pdf output.pdf
"""

import pikepdf
import sys

def extract_fields(pdf_path):
    """Extract all form field information."""
    pdf = pikepdf.open(pdf_path)
    fields = []

    for page_num, page in enumerate(pdf.pages, 1):
        if "/Annots" not in page:
            continue
        for annot in page.Annots:
            field_type = str(annot.get("/FT", ""))
            field_name = str(annot.get("/T", ""))
            rect = annot.get("/Rect", None)

            if field_name and rect:
                coords = [float(x) for x in rect]
                fields.append({
                    "page": page_num,
                    "name": field_name,
                    "type": "text" if field_type == "/Tx" else "checkbox" if field_type == "/Btn" else field_type,
                    "y": coords[3],
                    "x": coords[0]
                })

    # Sort by page, then y (descending for top-to-bottom), then x
    fields.sort(key=lambda f: (f["page"], -f["y"], f["x"]))
    return fields

def create_test_pdf(input_path, output_path):
    """Create a PDF with field IDs visible for mapping."""
    pdf = pikepdf.open(input_path)

    for page in pdf.pages:
        if "/Annots" not in page:
            continue
        for annot in page.Annots:
            field_type = str(annot.get("/FT", ""))
            field_name = str(annot.get("/T", ""))

            if field_type == "/Tx":
                annot["/V"] = pikepdf.String(field_name[-5:])
                if "/AP" in annot:
                    del annot["/AP"]
            elif field_type == "/Btn":
                annot["/V"] = pikepdf.Name("/Yes")
                annot["/AS"] = pikepdf.Name("/Yes")

    pdf.save(output_path)

def rename_fields(input_path, output_path, mapping):
    """Rename fields according to mapping dictionary."""
    pdf = pikepdf.open(input_path)
    renamed = 0

    for page in pdf.pages:
        if "/Annots" not in page:
            continue
        for annot in page.Annots:
            old_name = str(annot.get("/T", ""))
            if old_name in mapping:
                annot["/T"] = pikepdf.String(mapping[old_name])
                renamed += 1

    pdf.save(output_path)
    return renamed

def validate_fields(pdf_path):
    """Print all field names in the PDF."""
    pdf = pikepdf.open(pdf_path)

    for page_num, page in enumerate(pdf.pages, 1):
        if "/Annots" not in page:
            continue
        for annot in page.Annots:
            field_type = str(annot.get("/FT", ""))
            field_name = str(annot.get("/T", ""))
            type_label = "TEXT" if field_type == "/Tx" else "CB" if field_type == "/Btn" else field_type
            print(f"Page {page_num}: [{type_label}] {field_name}")

if __name__ == "__main__":
    # Example usage - customize the mapping for your form
    mapping = {
        "Text Field 20242": "participant_name",
        "Check Box 16": "cb_single",
        # Add your mappings here
    }

    if len(sys.argv) >= 3:
        input_pdf = sys.argv[1]
        output_pdf = sys.argv[2]

        print("Extracting fields...")
        fields = extract_fields(input_pdf)
        for f in fields:
            print(f"  {f['name']} ({f['type']}) - Page {f['page']}")

        print(f"\nRenaming {len(mapping)} fields...")
        count = rename_fields(input_pdf, output_pdf, mapping)
        print(f"Renamed {count} fields")

        print("\nValidating output...")
        validate_fields(output_pdf)
    else:
        print("Usage: python rename_fields.py input.pdf output.pdf")
```

## Troubleshooting

### Field Not Being Renamed

**Problem:** A field exists but isn't being renamed.

**Solution:** Check the exact field name including any whitespace or special characters:
```python
field_name = str(annot.get("/T", ""))
print(repr(field_name))  # Shows exact string including hidden chars
```

### Changes Not Visible in PDF Viewer

**Problem:** Renamed field values don't appear.

**Solution:** Delete the appearance stream to force regeneration:
```python
if "/AP" in annot:
    del annot["/AP"]
```

### Checkbox Won't Check

**Problem:** Setting `/V` to `/Yes` doesn't visually check the box.

**Solution:** Also set the appearance state:
```python
annot["/V"] = pikepdf.Name("/Yes")
annot["/AS"] = pikepdf.Name("/Yes")  # Required for visual update
```

### Field Names with Hierarchy

**Problem:** Some PDFs have hierarchical field names like `form1[0].page1[0].field[0]`.

**Solution:** These are fully qualified names. You can rename them the same way:
```python
field_mapping = {
    "form1[0].page1[0].Name[0]": "participant_name",
}
```

## Integration with Form Filling

After renaming fields, you can fill them programmatically:

```python
import pikepdf

def fill_form(pdf_path, output_path, field_values):
    """Fill a form with semantic field names."""
    pdf = pikepdf.open(pdf_path)

    for page in pdf.pages:
        if "/Annots" not in page:
            continue
        for annot in page.Annots:
            field_name = str(annot.get("/T", ""))
            field_type = str(annot.get("/FT", ""))

            if field_name in field_values:
                value = field_values[field_name]

                if field_type == "/Tx":
                    annot["/V"] = pikepdf.String(value)
                    if "/AP" in annot:
                        del annot["/AP"]
                elif field_type == "/Btn":
                    check_value = pikepdf.Name("/Yes" if value else "/Off")
                    annot["/V"] = check_value
                    annot["/AS"] = check_value

    pdf.save(output_path)

# Now you can fill forms with readable field names
fill_form("form_semantic.pdf", "filled_form.pdf", {
    "participant_name": "John Smith",
    "date_of_birth": "1985-03-15",
    "annual_income": "75000",
    "cb_married": True,
    "cb_us_citizen": True,
})
```

## See Also

- `references/forms.md` - Complete guide to filling PDF forms
- `references/creating-fillable-pdfs.md` - Creating fillable PDFs from scratch
- `scripts/extract_form_field_info.py` - Extract field info to JSON
- `scripts/fill_fillable_fields.py` - Fill forms from JSON field values
