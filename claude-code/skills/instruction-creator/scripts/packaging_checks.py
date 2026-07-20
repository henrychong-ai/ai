#!/usr/bin/env python3
"""
Shared packaging enforcement for skill zips (Layer 2 — added 2026-07-20).

Imported by both package_skill.py (verbatim) and convert_to_claudeai.py
(sanitiser) so every zip build enforces the same gates locally, instead of
failing at Claude Desktop upload time or silently shipping content that
each rebuild previously had to re-sanitise by hand.

Checks (run on the FINAL staged file set, after exclusions):

  ALWAYS ON
  1. Filename charset — Claude Desktop rejects any zip path with characters
     outside [A-Za-z0-9._-/] ("Zip file contains path with invalid
     characters"). Spaces, apostrophes (smart AND ascii), em-dashes,
     parentheses, non-ASCII all fail. ERROR.
  2. Redundant binary — a bundled PDF whose same-stem .md companion is also
     bundled duplicates content in a form Claude can't read; policy is
     extract-to-text + archive the original outside the skill. ERROR.
  3. Large binary — any bundled binary (pdf/media/office) over 1 MB. WARNING
     (review whether it belongs in a skill at all).

  TEAM MODE ONLY (--team; for zips published to the org Skills folder)
  4. Secret / personal-content scan over text files:
       - real 1Password secret references (op:// URIs whose vault segment
         looks like a real vault — contains spaces; placeholders such as
         op://<vault>/... and single-word teaching examples pass)
       - absolute personal home paths (/Users/<name>/, /home/<name>/)
       - private key material (BEGIN ... PRIVATE KEY)
       - AWS access key ids (AKIA...)
     Plus any extra regexes from a MAINTAINER-LOCAL deny file at
     ~/.claude/packaging-deny-patterns.txt (one regex per line, # comments).
     The local file carries maintainer-specific landmines (personal repo
     names, account ids, known account numbers) so this team-distributed
     script stays generic. All hits are ERRORs.

  POST-ZIP (call check_zip_size after the zip is written)
  5. 30 MB hard cap — Claude Desktop rejects larger uploads. ERROR.

Usage from a packaging script:

    from packaging_checks import run_checks, check_zip_size
    errors, warnings = run_checks(files, team=args.team)
    # files = list of (absolute Path, arcname str) actually being zipped
    if errors: abort
    ...
    err = check_zip_size(zip_path)
"""

import re
from pathlib import Path

ALLOWED_CHARS = set(
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-/"
)

BINARY_SUFFIXES = {
    ".pdf", ".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg",
    ".mp3", ".mp4", ".mov", ".wav", ".m4a",
    ".docx", ".pptx", ".xlsx", ".zip", ".woff", ".woff2", ".ttf", ".otf",
    ".ico",
}

TEXT_SUFFIXES = {
    ".md", ".txt", ".yaml", ".yml", ".json", ".jsonl", ".csv", ".tsv",
    ".py", ".sh", ".js", ".ts", ".html", ".css", ".toml", ".xml", ".mmd",
}

LARGE_BINARY_BYTES = 1 * 1024 * 1024      # 1 MB warning threshold
ZIP_HARD_CAP_BYTES = 30 * 1024 * 1024     # Claude Desktop upload limit

# Team-mode deny patterns (generic — maintainer-specific ones live in the
# local deny file, never in this team-distributed script).
TEAM_DENY_PATTERNS = [
    # Real op:// secret references: vault segment containing a space is a
    # real vault name ("TEC - Dev"), not a placeholder/teaching example.
    # Vault segment must not cross backticks/quotes/parens — prose *about*
    # op:// (e.g. this guide) must not self-trigger; only URI-shaped refs do.
    (r"op://[^/\n<>`'\"()]*[ ][^/\n`'\"()]*/", "real 1Password op:// reference (use a prose pointer: vault -> item -> field)"),
    # Placeholder usernames (username/user/yourname/example/name) are allowed —
    # docs legitimately demonstrate absolute paths (e.g. Claude Desktop MCP
    # config requires them); only a REAL person's home path is a violation.
    (r"/Users/(?!username\b|user\b|yourname\b|you\b|example\b|name\b|<)[A-Za-z][A-Za-z0-9._-]*/", "absolute personal home path (/Users/...)"),
    (r"/home/(?!username\b|user\b|yourname\b|you\b|example\b|name\b|<)[A-Za-z][A-Za-z0-9._-]*/", "absolute personal home path (/home/...)"),
    (r"-----BEGIN [A-Z ]*PRIVATE KEY-----", "private key material"),
    (r"\bAKIA[0-9A-Z]{16}\b", "AWS access key id"),
]

LOCAL_DENY_FILE = Path.home() / ".claude" / "packaging-deny-patterns.txt"


def load_local_deny_patterns() -> list[tuple[str, str]]:
    """Extra regexes from the maintainer-local deny file (optional)."""
    patterns: list[tuple[str, str]] = []
    if LOCAL_DENY_FILE.exists():
        for line in LOCAL_DENY_FILE.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            patterns.append((line, f"local deny pattern ({LOCAL_DENY_FILE.name})"))
    return patterns


def run_checks(files: list[tuple[Path, str]], team: bool = False):
    """Run pre-zip checks over the final staged file set.

    Args:
        files: (absolute path, arcname) pairs for every file that will be
               written to the zip, AFTER exclusions.
        team:  enable the team-distribution secret/personal-content scan.

    Returns:
        (errors, warnings) — lists of human-readable strings. Any error
        should abort the build.
    """
    errors: list[str] = []
    warnings: list[str] = []

    arcnames = {arc for _, arc in files}

    # 1. Filename charset
    for _, arc in files:
        bad = set(arc) - ALLOWED_CHARS
        if bad:
            errors.append(
                f"invalid characters {sorted(bad)!r} in path: {arc} "
                "(Claude Desktop rejects; rename to kebab-case)"
            )

    for path, arc in files:
        suffix = path.suffix.lower()

        # 2. Redundant binary (PDF with bundled .md companion)
        if suffix == ".pdf":
            companion = arc[: -len(".pdf")] + ".md"
            if companion in arcnames:
                errors.append(
                    f"redundant binary: {arc} has a bundled .md companion "
                    f"({companion}) — archive the PDF outside the skill "
                    "(see skill-content-formats-guide.md) and ship the .md"
                )

        # 3. Large binary warning
        if suffix in BINARY_SUFFIXES:
            size = path.stat().st_size
            if size > LARGE_BINARY_BYTES:
                warnings.append(
                    f"large binary ({size / 1024 / 1024:.1f} MB): {arc} — "
                    "confirm it belongs in a skill zip"
                )

    # 4. Team-mode secret / personal-content scan
    if team:
        patterns = TEAM_DENY_PATTERNS + load_local_deny_patterns()
        compiled = [(re.compile(p), desc) for p, desc in patterns]
        for path, arc in files:
            if path.suffix.lower() not in TEXT_SUFFIXES:
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            for rx, desc in compiled:
                for m in rx.finditer(text):
                    line_no = text.count("\n", 0, m.start()) + 1
                    snippet = m.group(0)
                    if len(snippet) > 60:
                        snippet = snippet[:57] + "..."
                    errors.append(
                        f"team-distribution violation [{desc}] in {arc}:{line_no}: {snippet!r}"
                    )

    return errors, warnings


def check_zip_size(zip_path: Path):
    """Post-zip 30 MB hard-cap check. Returns an error string or None."""
    size = zip_path.stat().st_size
    if size > ZIP_HARD_CAP_BYTES:
        return (
            f"zip is {size / 1024 / 1024:.1f} MB — exceeds the 30 MB Claude "
            "Desktop upload cap; reduce the skill (strip/archive binaries) "
            "and rebuild"
        )
    return None


def report(errors: list[str], warnings: list[str]) -> None:
    """Print check results in a consistent format."""
    for w in warnings:
        print(f"  ! WARNING: {w}")
    for e in errors:
        print(f"  X ERROR: {e}")
