#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["pyyaml>=6"]
# ///
"""
Convert Claude Code skills to Claude.ai ecosystem format.

This script transforms skills from the Claude Code filesystem format
to a zip file suitable for upload to Claude.ai (Desktop, iOS, Android, Web).

Usage:
    uv run convert_to_claudeai.py <skill_path> [output_dir] [options]

Examples:
    uv run convert_to_claudeai.py path/to/skills/cooking
    uv run convert_to_claudeai.py path/to/skills/cooking ~/Desktop/
    uv run convert_to_claudeai.py path/to/skills/cooking ~/Desktop/ --verbose

Output:
    Creates a zip file ready for upload to Claude.ai Settings > Capabilities

Dependencies:
    - pyyaml, declared in the PEP 723 header above. `uv run` supplies it; a plain
      `python3` run without it re-runs itself via uv (see _script_deps.py).
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
import zipfile
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))
from packaging_checks import run_checks, check_zip_size, check_archive_layout, StagedZip, report as checks_report

if __name__ == "__main__":
    from _script_deps import ensure_modules
    ensure_modules(__file__, any_of=("ruamel.yaml", "yaml"), pip_name="pyyaml")

# YAML handling - try ruamel.yaml first (preserves formatting), fall back to PyYAML
try:
    from ruamel.yaml import YAML
    yaml = YAML()
    yaml.preserve_quotes = True
    USE_RUAMEL = True
except ImportError:
    try:
        import yaml as pyyaml
        USE_RUAMEL = False
    except ImportError:
        print("Error: No YAML library found. Run via `uv run convert_to_claudeai.py ...`")
        sys.exit(1)


class SkillConverter:
    """Converts Claude Code skills to Claude.ai format."""

    # YAML fields to remove (Claude Code specific)
    REMOVE_YAML_FIELDS = [
        'allowed-tools',
    ]

    # Patterns to remove from content
    CC_PATTERNS = [
        # MCP tool calls
        (r'`mcp__\w+__\w+\([^)]*\)`', '[MCP tool reference removed]'),
        (r'mcp__\w+__\w+\([^)]*\)', '[MCP tool reference removed]'),
        (r'mcp__\w+__\w+', '[MCP tool]'),

        # Bash tool patterns
        (r'Bash\([^)]+\)', '[CLI command]'),

        # Claude Code specific paths (but keep as documentation)
        # (r'~/\.claude/', '[Claude config]/'),
        # (r'\$HOME/\.claude/', '[Claude config]/'),
    ]

    # Patterns to flag but not remove (for manual review)
    WARNING_PATTERNS = [
        (r'scripts/\w+\.py', 'Python script reference'),
        (r'scripts/\w+\.sh', 'Shell script reference'),
        (r'```bash\n.*?```', 'Bash code block'),
        (r'```python\n.*?```', 'Python code block'),
    ]

    # Files/directories to exclude from bundle
    EXCLUDE_PATTERNS = [
        # NOTE: scripts/ is INCLUDED — Claude.ai mounts the full skill at
        # /mnt/skills/user/<skill>/ and the code execution tool can invoke them
        # (this is how Anthropic's own docx/pdf/pptx/xlsx skills function in
        # Claude.ai). The "Scripts won't execute" assumption was outdated.
        '*.pyc',
        '__pycache__/',
        # Tool-generated cache dirs. These self-ignore for git by writing their
        # own internal .gitignore containing '*', so `git status` stays clean
        # and they are invisible during review — but the packager does not read
        # .gitignore, so without an explicit rule the cache contents ship while
        # the .gitignore itself is excluded. (Caught 2026-07-22 when a
        # .ruff_cache leaked files into a freshly built zip.)
        '.ruff_cache/',
        '.mypy_cache/',
        '.pytest_cache/',
        '.venv/',
        # Database binaries — always derived/regenerable caches in skills, and
        # they carry full data even when gitignored (git-invisible ≠
        # package-invisible: the packager walks the filesystem, not the index,
        # so a gitignored database cache would otherwise ship inside the zip.)
        '*.duckdb',
        '*.sqlite',
        '*.sqlite3',
        # The per-skill exclude manifest itself never ships
        '.claudeai-exclude',
        '.DS_Store',
        '*.env',
        '*.key',
        '*.pem',
        # Browser-only dashboards (HTML/JS/JSON) — not renderable on Claude.ai
        'dashboard/',
        # Maintainer files — dev session logs, roadmaps, and repo orientation;
        # they carry maintainer-personal context and don't serve skill consumers
        # (added 2026-07-08 after a distribution-hygiene review)
        'TODO.md',
        'CHANGELOG.md',
        'README.md',
        'todo/',
        '.gitignore',
        'cd-project-recipe.md',
    ]

    # Maximum file sizes (bytes)
    MAX_SINGLE_FILE = 30 * 1024 * 1024  # 30MB
    MAX_TOTAL_SIZE = 50 * 1024 * 1024   # 50MB recommended
    WARN_TOTAL_SIZE = 10 * 1024 * 1024  # 10MB warning threshold

    def __init__(
        self,
        skill_path: Path,
        output_dir: Path,
        verbose: bool = False,
        dry_run: bool = False,
        keep_tools: bool = False,
        inline_refs: bool = False,
        team: bool = False,
    ):
        self.skill_path = Path(skill_path).resolve()
        self.output_dir = Path(output_dir).resolve()
        self.verbose = verbose
        self.dry_run = dry_run
        self.keep_tools = keep_tools
        self.inline_refs = inline_refs
        self.team = team

        self.skill_name = self.skill_path.name
        self.warnings: list[str] = []
        self.changes: list[str] = []

        # Per-skill packaging excludes: optional `.claudeai-exclude` at the
        # skill root, one pattern per line (same syntax as EXCLUDE_PATTERNS:
        # `dir/` prefix, `*` glob on filename, or exact relative path).
        # Lets a skill ship a curated subset (e.g. summary CSVs) while keeping
        # bulk data out of the zip, without hardcoding skill names here.
        self.extra_excludes: list[str] = []
        exclude_file = self.skill_path / '.claudeai-exclude'
        if exclude_file.exists():
            for line in exclude_file.read_text().splitlines():
                line = line.strip()
                if line and not line.startswith('#'):
                    self.extra_excludes.append(line)
            if self.extra_excludes:
                self.changes.append(
                    f"Applied {len(self.extra_excludes)} per-skill exclude "
                    f"pattern(s) from .claudeai-exclude"
                )

    def log(self, message: str) -> None:
        """Log message if verbose mode enabled."""
        if self.verbose:
            print(f"  {message}")

    def warn(self, message: str) -> None:
        """Record a warning."""
        self.warnings.append(message)
        if self.verbose:
            print(f"  WARNING: {message}")

    def convert(self) -> Optional[Path]:
        """
        Main conversion process.

        Returns:
            Path to created zip file, or None if failed.
        """
        print(f"Converting skill: {self.skill_name}")

        # Validate input
        if not self.validate_skill():
            return None

        # Create temp directory for conversion
        temp_dir = self.output_dir / f".{self.skill_name}_temp"
        converted_dir = temp_dir / self.skill_name

        try:
            # Clean up any previous temp (a dry run touches nothing on disk)
            if not self.dry_run:
                if temp_dir.exists():
                    shutil.rmtree(temp_dir)
                converted_dir.mkdir(parents=True)

            # Convert SKILL.md
            self.convert_skill_md(converted_dir)

            # Bundle references
            self.bundle_references(converted_dir)

            # Packaging checks on the FINAL staged tree (post-exclusions):
            # charset + redundant-binary always; secret scan in --team mode
            if not self.dry_run:
                staged = [
                    (p, str(p.relative_to(temp_dir)))
                    for p in sorted(converted_dir.rglob("*"))
                    if p.is_file()
                ]
                print("  Running packaging checks" + (" (team mode)" if self.team else "") + "...")
                errors, check_warnings = run_checks(staged, team=self.team)
                checks_report(errors, check_warnings)
                self.warnings.extend(check_warnings)
                if errors:
                    print(f"Packaging checks failed ({len(errors)} error(s)) — zip not created.")
                    return None

            # Create zip. The archive is built to a temporary sibling of the
            # output path and moved into place only after every post-zip check
            # passes, so a failed build never touches a zip that is already
            # there (a rebuild that failed the size cap used to delete it).
            zip_path = self.output_dir / f"{self.skill_name}.zip"
            if self.dry_run:
                self.create_zip(temp_dir, zip_path)
            else:
                with StagedZip(zip_path) as staged_zip:
                    self.create_zip(temp_dir, staged_zip.tmp_path)

                    # 30 MB Claude Desktop upload cap
                    size_err = check_zip_size(staged_zip.tmp_path)
                    if size_err:
                        print(f"Error: {size_err}")
                        return None

                    # Archive layout: one top-level folder named for the skill,
                    # nothing at the root ("All files must be inside the
                    # top-level folder")
                    with zipfile.ZipFile(staged_zip.tmp_path) as zf:
                        layout_errors = check_archive_layout(zf.namelist(), expected_wrapper=self.skill_name)
                    if layout_errors:
                        checks_report(layout_errors, [])
                        print(f"Archive layout rejected ({len(layout_errors)} error(s)) — zip not created; any existing zip is unchanged.")
                        return None

                    staged_zip.commit()

            # Report
            self.report()

            return zip_path

        except Exception as e:
            print(f"Error during conversion: {e}")
            return None

        finally:
            # Cleanup temp directory
            if temp_dir.exists() and not self.dry_run:
                shutil.rmtree(temp_dir)

    def validate_skill(self) -> bool:
        """Validate the source skill directory."""
        if not self.skill_path.exists():
            print(f"Error: Skill path does not exist: {self.skill_path}")
            return False

        if not self.skill_path.is_dir():
            print(f"Error: Skill path is not a directory: {self.skill_path}")
            return False

        skill_md = self.skill_path / "SKILL.md"
        if not skill_md.exists():
            print(f"Error: SKILL.md not found in: {self.skill_path}")
            return False

        return True

    def convert_skill_md(self, output_dir: Path) -> None:
        """Convert and write the SKILL.md file.

        The frontmatter is NEVER re-serialised through a YAML dumper. Fields
        are removed textually and the remaining frontmatter text is written
        back byte-for-byte. A dump round-trip (PyYAML without allow_unicode,
        default 80-col width) turns an em-dash into "\u2014" and folds a long
        description with "\" line continuations — Claude Desktop's skill
        validator rejects that ("hex/unicode escape or an escaped line break
        in its SKILL.md frontmatter ... Write the text literally", observed
        2026-09-10). packaging_checks enforces this.
        """
        skill_md = self.skill_path / "SKILL.md"
        content = skill_md.read_text(encoding='utf-8')

        # Parse frontmatter (raw text + parsed dict for logging) and body
        frontmatter_text, frontmatter, body = self.parse_frontmatter(content)

        # Clean frontmatter TEXTUALLY — the surviving lines stay verbatim
        cleaned_frontmatter_text = self.clean_frontmatter_text(frontmatter_text, frontmatter)

        # Clean body content
        cleaned_body = self.clean_content(body)

        # Reconstruct (no YAML dump — literal text only)
        if cleaned_frontmatter_text.strip():
            new_content = f"---\n{cleaned_frontmatter_text.rstrip()}\n---\n{cleaned_body}"
        else:
            new_content = cleaned_body

        # Write
        output_file = output_dir / "SKILL.md"
        if not self.dry_run:
            output_file.write_text(new_content, encoding='utf-8')
        self.log(f"Converted SKILL.md")

    def parse_frontmatter(self, content: str) -> tuple[str, dict, str]:
        """Split content into (raw frontmatter text, parsed dict, body).

        The raw text is what gets written back; the dict is only used to
        decide which fields to drop and to report their values.
        """
        pattern = r'^---\n(.*?)\n---\n(.*)$'
        match = re.match(pattern, content, re.DOTALL)

        if match:
            frontmatter_str = match.group(1)
            body = match.group(2)

            if USE_RUAMEL:
                import io
                frontmatter = yaml.load(io.StringIO(frontmatter_str))
            else:
                frontmatter = pyyaml.safe_load(frontmatter_str)

            return frontmatter_str, frontmatter or {}, body
        else:
            # No frontmatter
            return "", {}, content

    def clean_frontmatter_text(self, frontmatter_text: str, frontmatter: dict) -> str:
        """Remove Claude Code specific fields from the RAW frontmatter text.

        A top-level field is the `key:` line plus any following indented or
        list-item continuation lines. Everything else is returned untouched,
        so non-ASCII characters, quoting, and line breaks ship exactly as the
        author wrote them.
        """
        if self.keep_tools:
            return frontmatter_text

        lines = frontmatter_text.split("\n")
        out: list[str] = []
        skipping = False
        for line in lines:
            m = re.match(r'^([A-Za-z0-9_-]+):', line)
            if m:
                key = m.group(1)
                if key in self.REMOVE_YAML_FIELDS:
                    skipping = True
                    self.changes.append(
                        f"Removed YAML field: {key}={frontmatter.get(key)!r}")
                    self.log(f"Removed field: {key}")
                    continue
                skipping = False
            elif skipping and (line.startswith((" ", "\t")) or line.strip() == ""):
                # continuation line of the field being removed
                if line.strip() == "" and not skipping:
                    out.append(line)
                continue
            else:
                skipping = False
            out.append(line)
        return "\n".join(out)

    def clean_content(self, content: str) -> str:
        """Clean body content of CC-specific patterns.

        Fenced code blocks (``` ... ```) are preserved verbatim — they hold
        examples and templates, and scrubbing a documented literal such as
        `allowed-tools: Bash(git:*)` silently corrupts the skill's own docs
        (the 2026-06-13 instruction-creator zip bug). Only prose / inline tool
        references outside code fences are scrubbed, and every scrub is reported
        so a scrub can never corrupt content unseen.
        """
        # Split into fenced-code segments and prose; re.split keeps the fences
        # as their own list items (they start with ```), prose sits between.
        segments = re.split(r'(```.*?```)', content, flags=re.DOTALL)
        scrubs: list[tuple[str, str]] = []

        for i, seg in enumerate(segments):
            if seg.startswith('```'):
                continue  # preserve code fences verbatim
            for pattern, replacement in self.CC_PATTERNS:
                def _record(m, _r=replacement):
                    scrubs.append((m.group(0), _r))
                    return _r
                seg = re.sub(pattern, _record, seg, flags=re.DOTALL)
            segments[i] = seg
        cleaned = ''.join(segments)

        # Report every scrub ALWAYS (not just --verbose) — silent scrubs corrupt docs.
        if scrubs:
            self.changes.append(
                f"Scrubbed {len(scrubs)} CC tool reference(s) from prose (code fences preserved)"
            )
            print(f"  Scrubbed {len(scrubs)} prose tool reference(s) (code fences preserved):")
            for orig, repl in scrubs:
                print(f"    {orig!r} -> {repl}")

        # Check for warning patterns (run on full content, fences included)
        for pattern, description in self.WARNING_PATTERNS:
            matches = re.findall(pattern, cleaned, re.DOTALL)
            if matches:
                self.warn(f"Found {len(matches)} {description} - may need manual review")

        return cleaned

    def bundle_references(self, output_dir: Path) -> None:
        """Copy all skill files except SKILL.md (handled separately) to output dir.

        Walks the entire skill tree (not just references/) so scripts/, top-level
        .md files (e.g. pdf/forms.md, pptx/editing.md), and LICENSE.txt are
        included. Claude.ai mounts the full tree at /mnt/skills/user/<skill>/.
        """
        total_size = 0
        files_copied = 0

        for src_file in self.skill_path.rglob("*"):
            if not src_file.is_file():
                continue
            rel_path = src_file.relative_to(self.skill_path)
            if str(rel_path) == "SKILL.md":
                continue  # written separately by write_skill_md()
            if self.should_exclude(rel_path):
                self.log(f"Excluded: {rel_path}")
                continue

            file_size = src_file.stat().st_size
            if file_size > self.MAX_SINGLE_FILE:
                self.warn(f"File too large ({file_size / 1024 / 1024:.1f}MB): {rel_path}")
                continue

            total_size += file_size

            dest = output_dir / rel_path
            if not self.dry_run:
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src_file, dest)
            files_copied += 1
            self.log(f"Bundled: {rel_path}")

        if total_size > self.WARN_TOTAL_SIZE:
            self.warn(f"Total size ({total_size / 1024 / 1024:.1f}MB) exceeds recommended 10MB")

        self.changes.append(f"Bundled {files_copied} files ({total_size / 1024:.1f}KB)")

    def should_exclude(self, path: Path) -> bool:
        """Check if path should be excluded from bundle."""
        path_str = str(path)

        for pattern in list(self.EXCLUDE_PATTERNS) + self.extra_excludes:
            if pattern.endswith('/'):
                # Directory pattern
                if path_str.startswith(pattern[:-1]):
                    return True
            elif '*' in pattern:
                # Glob pattern
                import fnmatch
                if fnmatch.fnmatch(path.name, pattern):
                    return True
            else:
                # Exact match
                if path_str == pattern or path.name == pattern:
                    return True

        return False

    def create_zip(self, temp_dir: Path, target: Path) -> Path:
        """Write the archive to `target`.

        `target` is the caller's temporary build path, never the final output
        path: the caller verifies the archive and then moves it into place.
        Under --dry-run nothing is written.
        """
        zip_name = f"{self.skill_name}.zip"

        if self.dry_run:
            self.log(f"Would create: {target}")
            return target

        # Create zip with correct structure
        with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED) as zf:
            skill_dir = temp_dir / self.skill_name
            for file_path in skill_dir.rglob("*"):
                if file_path.is_file():
                    arc_name = file_path.relative_to(temp_dir)
                    zf.write(file_path, arc_name)

        zip_size = target.stat().st_size
        self.changes.append(f"Created zip: {zip_name} ({zip_size / 1024:.1f}KB)")

        return target

    def report(self) -> None:
        """Print conversion report."""
        print(f"\n  Changes made:")
        for change in self.changes:
            print(f"    - {change}")

        if self.warnings:
            print(f"\n  Warnings ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"    ! {warning}")

        if not self.dry_run:
            print(f"\n  Output: {self.output_dir / self.skill_name}.zip")
            print(f"  Upload to: Claude.ai > Settings > Capabilities > Custom Skills")


def main():
    parser = argparse.ArgumentParser(
        description="Convert Claude Code skills to Claude.ai format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    %(prog)s path/to/skills/cooking
    %(prog)s path/to/skills/cooking ~/Desktop/
    %(prog)s path/to/skills/cooking ~/Desktop/ --verbose --dry-run

The output zip can be uploaded to Claude.ai via Settings > Capabilities.
Skills uploaded to any Claude.ai platform will sync to all others automatically.
        """,
    )

    parser.add_argument(
        "skill_path",
        type=Path,
        help="Path to the Claude Code skill directory",
    )

    parser.add_argument(
        "output_dir",
        type=Path,
        nargs="?",
        default=Path.home() / "Desktop",
        help="Output directory for the zip file (default: ~/Desktop)",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed conversion steps",
    )

    parser.add_argument(
        "--keep-tools",
        action="store_true",
        help="Keep allowed-tools field (not recommended)",
    )

    parser.add_argument(
        "--inline-refs",
        action="store_true",
        help="Inline all reference content into SKILL.md (not yet implemented)",
    )

    parser.add_argument(
        "--team",
        action="store_true",
        help="Enable the team-distribution secret/personal-content scan "
             "(use for every zip shared with a team or organisation)",
    )

    args = parser.parse_args()

    # Ensure output directory exists (a dry run creates nothing)
    if not args.dry_run:
        args.output_dir.mkdir(parents=True, exist_ok=True)

    # Convert
    converter = SkillConverter(
        skill_path=args.skill_path,
        output_dir=args.output_dir,
        verbose=args.verbose,
        dry_run=args.dry_run,
        keep_tools=args.keep_tools,
        inline_refs=args.inline_refs,
        team=args.team,
    )

    result = converter.convert()

    if result:
        print(f"\nConversion successful!")
        sys.exit(0)
    else:
        print(f"\nConversion failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()
