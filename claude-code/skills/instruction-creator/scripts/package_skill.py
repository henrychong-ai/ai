#!/usr/bin/env python3
# Portions of this file are derived from the skill-creator skill in Anthropic's
# anthropics/skills repository (https://github.com/anthropics/skills/tree/main/skills/skill-creator),
# licensed under the Apache License, Version 2.0 (see LICENSE-APACHE-2.0.txt in this folder).
# Modified by Henry Chong.
"""
Skill Packager - Creates a distributable zip file of a skill folder

Usage:
    python utils/package_skill.py <path/to/skill-folder> [output-directory]

Example:
    python utils/package_skill.py skills/public/my-skill
    python utils/package_skill.py skills/public/my-skill ./dist
"""

import sys
import zipfile
from pathlib import Path
from quick_validate import validate_skill
from packaging_checks import run_checks, check_zip_size, check_archive_layout, StagedZip, report

# Build artifacts / OS cruft never shipped in a skill zip. Mirrors the
# exclusions in convert_to_claudeai.py so a verbatim package is still clean
# (a stray __pycache__/*.pyc from running a script must not bloat the zip).
EXCLUDE_NAMES = {
    ".DS_Store",
    # Maintainer files — dev logs/roadmaps/orientation; not for skill consumers
    # (aligned with convert_to_claudeai.py, 2026-07-08)
    "TODO.md",
    "CHANGELOG.md",
    "README.md",
    "cd-project-recipe.md",
    ".gitignore",
}
# .duckdb/.sqlite: derived database caches carry full data even when
# gitignored — the packager walks the filesystem, not the git index.
EXCLUDE_SUFFIXES = {".pyc", ".pyo", ".duckdb", ".sqlite", ".sqlite3"}
# Tool-generated cache dirs self-ignore for git (they write an internal
# .gitignore containing '*'), so they stay invisible to `git status` while the
# packager — which does not read .gitignore — would otherwise ship their
# contents. Excluded explicitly. (Caught 2026-07-22 via a .ruff_cache leak.)
EXCLUDE_DIRS = {"__pycache__", ".git", ".ipynb_checkpoints", "todo",
                ".ruff_cache", ".mypy_cache", ".pytest_cache", ".venv"}


def _excluded(path: Path) -> bool:
    """True if path is build junk that should never be packaged."""
    if path.name in EXCLUDE_NAMES or path.suffix in EXCLUDE_SUFFIXES:
        return True
    return any(part in EXCLUDE_DIRS for part in path.parts)


def package_skill(skill_path, output_dir=None, team=False):
    """
    Package a skill folder into a zip file.

    Args:
        skill_path: Path to the skill folder
        output_dir: Optional output directory for the zip file (defaults to current directory)
        team: Enable the team-distribution secret/personal-content scan
              (use for every zip shared with a team or organisation)

    Returns:
        Path to the created zip file, or None if error
    """
    skill_path = Path(skill_path).resolve()

    # Validate skill folder exists
    if not skill_path.exists():
        print(f"❌ Error: Skill folder not found: {skill_path}")
        return None

    if not skill_path.is_dir():
        print(f"❌ Error: Path is not a directory: {skill_path}")
        return None

    # Validate SKILL.md exists
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        print(f"❌ Error: SKILL.md not found in {skill_path}")
        return None

    # Run validation before packaging
    print("🔍 Validating skill...")
    valid, message = validate_skill(skill_path)
    if not valid:
        print(f"❌ Validation failed: {message}")
        print("   Please fix the validation errors before packaging.")
        return None
    print(f"✅ {message}\n")

    # Determine output location
    skill_name = skill_path.name
    if output_dir:
        output_path = Path(output_dir).resolve()
        output_path.mkdir(parents=True, exist_ok=True)
    else:
        output_path = Path.cwd()

    zip_filename = output_path / f"{skill_name}.zip"

    # Build the final include list, then run packaging checks BEFORE zipping
    # (charset / redundant-binary always; secret scan in --team mode)
    included = [
        (p, str(p.relative_to(skill_path.parent)))
        for p in sorted(skill_path.rglob('*'))
        if p.is_file() and not _excluded(p)
    ]
    print("🔍 Running packaging checks" + (" (team mode)" if team else "") + "...")
    errors, warnings = run_checks(included, team=team)
    report(errors, warnings)
    if errors:
        print(f"❌ Packaging checks failed ({len(errors)} error(s)) — zip not created.")
        return None

    # Create the zip file. It is built to a temporary sibling of the output
    # path and moved into place only after every post-zip check passes, so a
    # failed build never touches a zip that is already there.
    try:
        with StagedZip(zip_filename) as staged:
            with zipfile.ZipFile(staged.tmp_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path, arcname in included:
                    zipf.write(file_path, arcname)
                    print(f"  Added: {arcname}")

            size_err = check_zip_size(staged.tmp_path)
            if size_err:
                print(f"❌ {size_err}")
                return None

            # Archive layout: one top-level folder named for the skill, nothing
            # at the root (Claude.ai: "All files must be inside the top-level folder")
            with zipfile.ZipFile(staged.tmp_path) as zipf:
                layout_errors = check_archive_layout(zipf.namelist(), expected_wrapper=skill_path.name)
            if layout_errors:
                report(layout_errors, [])
                print(f"❌ Archive layout rejected ({len(layout_errors)} error(s)) — zip not created; any existing zip is unchanged.")
                return None

            staged.commit()

        print(f"\n✅ Successfully packaged skill to: {zip_filename}")
        return zip_filename

    except Exception as e:
        print(f"❌ Error creating zip file: {e}")
        return None


def main():
    args = [a for a in sys.argv[1:] if a != "--team"]
    team = "--team" in sys.argv[1:]
    if not args:
        print("Usage: python utils/package_skill.py <path/to/skill-folder> [output-directory] [--team]")
        print("\nExample:")
        print("  python utils/package_skill.py skills/public/my-skill")
        print("  python utils/package_skill.py skills/public/my-skill ./dist --team")
        print("\n--team enables the team-distribution secret/personal-content scan")
        print("(use for every zip shared with a team or organisation)")
        sys.exit(1)

    skill_path = args[0]
    output_dir = args[1] if len(args) > 1 else None

    print(f"📦 Packaging skill: {skill_path}")
    if output_dir:
        print(f"   Output directory: {output_dir}")
    print()

    result = package_skill(skill_path, output_dir, team=team)

    if result:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
