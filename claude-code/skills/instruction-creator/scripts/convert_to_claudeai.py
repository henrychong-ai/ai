#!/usr/bin/env python3
"""
Convert Claude Code skills to Claude.ai ecosystem format.

This script transforms skills from the Claude Code filesystem format
to a zip file suitable for upload to Claude.ai (Desktop, iOS, Android, Web).

Usage:
    uv run --with pyyaml python convert_to_claudeai.py <skill_path> [output_dir] [options]

Examples:
    uv run --with pyyaml python convert_to_claudeai.py ~/.claude/skills/cooking
    uv run --with pyyaml python convert_to_claudeai.py ~/.claude/skills/cooking ~/Desktop/
    uv run --with pyyaml python convert_to_claudeai.py ~/.claude/skills/cooking ~/Desktop/ --verbose

Output:
    Creates a zip file ready for upload to Claude.ai Settings > Capabilities

Dependencies:
    - pyyaml (provided via uv run --with pyyaml)
"""

import argparse
import re
import shutil
import sys
import zipfile
from pathlib import Path
from typing import Optional

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
        print("Error: No YAML library found. Install with: pip install pyyaml")
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
        'scripts/',       # Scripts won't execute on Claude.ai
        '*.pyc',
        '__pycache__/',
        '.DS_Store',
        '*.env',
        '*.key',
        '*.pem',
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
    ):
        self.skill_path = Path(skill_path).resolve()
        self.output_dir = Path(output_dir).resolve()
        self.verbose = verbose
        self.dry_run = dry_run
        self.keep_tools = keep_tools
        self.inline_refs = inline_refs

        self.skill_name = self.skill_path.name
        self.warnings: list[str] = []
        self.changes: list[str] = []

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
            # Clean up any previous temp
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
            converted_dir.mkdir(parents=True)

            # Convert SKILL.md
            self.convert_skill_md(converted_dir)

            # Bundle references
            self.bundle_references(converted_dir)

            # Create zip
            zip_path = self.create_zip(temp_dir)

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
        """Convert and write the SKILL.md file."""
        skill_md = self.skill_path / "SKILL.md"
        content = skill_md.read_text(encoding='utf-8')

        # Parse frontmatter and body
        frontmatter, body = self.parse_frontmatter(content)

        # Clean frontmatter
        cleaned_frontmatter = self.clean_frontmatter(frontmatter)

        # Clean body content
        cleaned_body = self.clean_content(body)

        # Reconstruct
        if USE_RUAMEL:
            import io
            stream = io.StringIO()
            yaml.dump(cleaned_frontmatter, stream)
            frontmatter_str = stream.getvalue()
        else:
            frontmatter_str = pyyaml.dump(cleaned_frontmatter, default_flow_style=False)

        new_content = f"---\n{frontmatter_str}---\n{cleaned_body}"

        # Write
        output_file = output_dir / "SKILL.md"
        if not self.dry_run:
            output_file.write_text(new_content, encoding='utf-8')
        self.log(f"Converted SKILL.md")

    def parse_frontmatter(self, content: str) -> tuple[dict, str]:
        """Parse YAML frontmatter and body from content."""
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

            return frontmatter or {}, body
        else:
            # No frontmatter
            return {}, content

    def clean_frontmatter(self, frontmatter: dict) -> dict:
        """Remove Claude Code specific YAML fields."""
        cleaned = dict(frontmatter)

        for field in self.REMOVE_YAML_FIELDS:
            if field in cleaned and not self.keep_tools:
                removed_value = cleaned.pop(field)
                self.changes.append(f"Removed YAML field: {field}={removed_value}")
                self.log(f"Removed field: {field}")

        return cleaned

    def clean_content(self, content: str) -> str:
        """Clean body content of CC-specific patterns."""
        cleaned = content

        # Apply removal patterns
        for pattern, replacement in self.CC_PATTERNS:
            matches = re.findall(pattern, cleaned, re.DOTALL)
            if matches:
                self.changes.append(f"Replaced {len(matches)} instances of pattern: {pattern[:30]}...")
                cleaned = re.sub(pattern, replacement, cleaned, flags=re.DOTALL)

        # Check for warning patterns
        for pattern, description in self.WARNING_PATTERNS:
            matches = re.findall(pattern, cleaned, re.DOTALL)
            if matches:
                self.warn(f"Found {len(matches)} {description} - may need manual review")

        return cleaned

    def bundle_references(self, output_dir: Path) -> None:
        """Copy reference files to output directory."""
        refs_dir = self.skill_path / "references"

        if not refs_dir.exists():
            self.log("No references directory found")
            return

        output_refs = output_dir / "references"
        total_size = 0
        files_copied = 0

        for ref_file in refs_dir.rglob("*"):
            if ref_file.is_file():
                # Check exclusion patterns
                rel_path = ref_file.relative_to(self.skill_path)
                if self.should_exclude(rel_path):
                    self.log(f"Excluded: {rel_path}")
                    continue

                # Check file size
                file_size = ref_file.stat().st_size
                if file_size > self.MAX_SINGLE_FILE:
                    self.warn(f"File too large ({file_size / 1024 / 1024:.1f}MB): {rel_path}")
                    continue

                total_size += file_size

                # Copy file
                dest = output_dir / rel_path
                if not self.dry_run:
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(ref_file, dest)
                files_copied += 1
                self.log(f"Bundled: {rel_path}")

        if total_size > self.WARN_TOTAL_SIZE:
            self.warn(f"Total size ({total_size / 1024 / 1024:.1f}MB) exceeds recommended 10MB")

        self.changes.append(f"Bundled {files_copied} reference files ({total_size / 1024:.1f}KB)")

    def should_exclude(self, path: Path) -> bool:
        """Check if path should be excluded from bundle."""
        path_str = str(path)

        for pattern in self.EXCLUDE_PATTERNS:
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

    def create_zip(self, temp_dir: Path) -> Path:
        """Create the final zip file."""
        zip_name = f"{self.skill_name}.zip"
        zip_path = self.output_dir / zip_name

        if self.dry_run:
            self.log(f"Would create: {zip_path}")
            return zip_path

        # Remove existing zip
        if zip_path.exists():
            zip_path.unlink()

        # Create zip with correct structure
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            skill_dir = temp_dir / self.skill_name
            for file_path in skill_dir.rglob("*"):
                if file_path.is_file():
                    arc_name = file_path.relative_to(temp_dir)
                    zf.write(file_path, arc_name)

        zip_size = zip_path.stat().st_size
        self.changes.append(f"Created zip: {zip_name} ({zip_size / 1024:.1f}KB)")

        return zip_path

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
    %(prog)s ~/.claude/skills/cooking
    %(prog)s ~/.claude/skills/cooking ~/Desktop/
    %(prog)s ~/.claude/skills/cooking ~/Desktop/ --verbose --dry-run

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

    args = parser.parse_args()

    # Ensure output directory exists
    args.output_dir.mkdir(parents=True, exist_ok=True)

    # Convert
    converter = SkillConverter(
        skill_path=args.skill_path,
        output_dir=args.output_dir,
        verbose=args.verbose,
        dry_run=args.dry_run,
        keep_tools=args.keep_tools,
        inline_refs=args.inline_refs,
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
