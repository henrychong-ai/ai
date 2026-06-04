#!/usr/bin/env python3
"""
Quick validation script for skills - minimal version.

Validates SKILL.md frontmatter AND body. The body check is a deliberate
guard: a bulk "token-optimise the description" edit that regenerates each
SKILL.md from frontmatter alone will silently delete every body. An
empty-body check here catches it. A skill with a non-trivial frontmatter
but an empty body is almost always a wipe/regression, not a valid skill.
See references/skill-edit-safety.md.
"""

import sys
import re
from pathlib import Path

# Claude skill description hard limit
DESC_MAX = 1024

def validate_skill(skill_path):
    """Basic validation of a skill. Returns (ok: bool, message: str)."""
    skill_path = Path(skill_path)

    skill_md = skill_path / 'SKILL.md'
    if not skill_md.exists():
        return False, "SKILL.md not found"

    content = skill_md.read_text()
    if not content.startswith('---'):
        return False, "No YAML frontmatter found"

    # Split frontmatter / body on the first closing fence.
    m = re.match(r'^---\n(.*?)\n---\n?(.*)$', content, re.DOTALL)
    if not m:
        return False, "Invalid frontmatter format (no closing '---')"
    frontmatter, body = m.group(1), m.group(2)

    # Required fields
    if 'name:' not in frontmatter:
        return False, "Missing 'name' in frontmatter"
    if 'description:' not in frontmatter:
        return False, "Missing 'description' in frontmatter"

    # name: hyphen-case
    name_match = re.search(r'name:\s*(.+)', frontmatter)
    if name_match:
        name = name_match.group(1).strip().strip('"\'')
        if not re.match(r'^[a-z0-9.-]+$', name):
            return False, f"Name '{name}' should be lowercase letters, digits, dots, and hyphens only"
        if name.startswith('-') or name.endswith('-') or '--' in name:
            return False, f"Name '{name}' cannot start/end with hyphen or contain consecutive hyphens"

    # description: no angle brackets, length <= DESC_MAX
    desc_match = re.search(r'description:\s*(.+)', frontmatter)
    if desc_match:
        description = desc_match.group(1).strip().strip('"\'')
        if '<' in description or '>' in description:
            return False, "Description cannot contain angle brackets (< or >)"
        if len(description) > DESC_MAX:
            return False, f"Description is {len(description)} chars (limit {DESC_MAX}) — trim it"

    # Optional strict YAML parse (catches e.g. unquoted colons) when pyyaml is present.
    try:
        import yaml  # noqa
        try:
            fm = yaml.safe_load(frontmatter)
            if not isinstance(fm, dict) or not fm.get('name') or not fm.get('description'):
                return False, "Frontmatter does not parse to a mapping with name + description (quote values containing ':')"
        except yaml.YAMLError as e:
            return False, f"Frontmatter is not valid YAML ({e}) — values containing ':' must be quoted"
    except ImportError:
        pass  # yaml not installed; skip strict parse

    # BODY GUARD — the wipe catcher. An empty body on a real skill = regression.
    if not body.strip():
        return False, ("SKILL.md body is EMPTY (frontmatter-only). A skill must have body "
                       "content. If you just edited the frontmatter, the body was likely "
                       "wiped — restore it before committing. See the 2026-06-04 body-wipe "
                       "post-mortem in references/skill-edit-safety.md.")

    return True, "Skill is valid!"

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python quick_validate.py <skill_directory>")
        sys.exit(1)
    valid, message = validate_skill(sys.argv[1])
    print(message)
    sys.exit(0 if valid else 1)
