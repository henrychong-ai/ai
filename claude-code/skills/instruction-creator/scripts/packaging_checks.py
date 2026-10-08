#!/usr/bin/env python3
"""
Shared packaging enforcement for skill zips (Layer 2 — added 2026-07-20).

Imported by both package_skill.py (verbatim) and convert_to_claudeai.py
(sanitiser) so every zip build enforces the same gates locally, instead of
failing at Claude Desktop upload time or silently shipping content that
each rebuild previously had to re-sanitise by hand.

Checks (run on the FINAL staged file set, after exclusions):

  ALWAYS ON
  0. SKILL.md frontmatter literal (no \\u/\\x escapes, no escaped line breaks)
  1. Filename charset — Claude Desktop rejects any zip path with characters
     outside [A-Za-z0-9._-/] ("Zip file contains path with invalid
     characters"). Spaces, apostrophes (smart AND ascii), em-dashes,
     parentheses, non-ASCII all fail. ERROR.
  2. Redundant binary — a bundled PDF whose same-stem .md companion is also
     bundled duplicates content in a form Claude can't read; policy is
     extract-to-text + archive the original outside the skill. ERROR.
  3. Large binary — any bundled binary (pdf/media/office) over 1 MB. WARNING
     (review whether it belongs in a skill at all).

  TEAM MODE ONLY (--team; for zips shared with a team or organisation)
  4. Secret / personal-content scan over text files:
       - real 1Password secret references (op:// URIs whose vault segment
         looks like a real vault — contains spaces; placeholders such as
         op://<vault>/... and single-word teaching examples pass)
       - absolute personal home paths (/Users/<name>/, /home/<name>/)
       - private key material (BEGIN ... PRIVATE KEY)
       - AWS access key ids (AKIA...)
     Plus any extra regexes from an optional MAINTAINER-LOCAL deny file:
     the path in the SKILL_PACKAGING_DENY_FILE environment variable, else
     ~/.claude/packaging-deny-patterns.txt (one regex per line, # comments).
     The local file carries maintainer-specific strings (personal repo
     names, account ids, known account numbers) so this distributed
     script stays generic. All hits are ERRORs.

  POST-ZIP (call check_zip_size / check_archive_layout after the zip is written)
  5. 30 MB hard cap — Claude Desktop rejects larger uploads. ERROR.
  6. Archive layout — every member must sit inside ONE top-level folder
     named for the skill. A single bare root-level file (e.g. a
     manifest.json appended without the folder prefix) makes Claude.ai
     reject the whole upload with "All files must be inside the top-level
     folder"; so do a second top-level folder, a __MACOSX/ tree, or a
     root-level .DS_Store. ERROR per violation.

Usage from a packaging script:

    from packaging_checks import run_checks, check_zip_size, check_archive_layout
    errors, warnings = run_checks(files, team=args.team)
    # files = list of (absolute Path, arcname str) actually being zipped
    if errors: abort
    ...
    err = check_zip_size(zip_path)
    errors = check_archive_layout(zf.namelist(), expected_wrapper=skill_name)

  BUILD-THEN-SWAP (StagedZip)
  The post-zip checks need a written archive, so the archive is written to a
  temporary sibling of the output path and only moved over the output path
  once every check has passed:

    with StagedZip(output_dir / f"{skill_name}.zip") as staged:
        ...write the archive to staged.tmp_path, run the post-zip checks on it...
        staged.commit()          # atomic os.replace onto the output path

  Leaving the block without commit() — a failed check, an exception, Ctrl-C —
  discards the temporary file and leaves any zip already at the output path
  byte-for-byte untouched. (Previously both packagers wrote straight to the
  output path and deleted the file when a post-zip check failed, so an
  oversized rebuild destroyed the last good zip.)
"""

from __future__ import annotations

import os
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

# Shared service-account home directories on managed hosts are team
# infrastructure documented for any admin, not a maintainer's personal home, so
# they are exempt from the personal-home-path deny pattern below. The account
# names are site-specific, so they live in a maintainer-local allow file (one
# bare account name per line) and never in this distributed script.
LOCAL_SERVICE_ACCOUNT_FILE = (
    Path.home() / ".claude" / "packaging-service-accounts.txt"
)


def load_service_account_homes() -> tuple[str, ...]:
    """Bare account names whose /Users/<name>/ or /home/<name>/ paths are team
    infrastructure rather than a personal home. Empty when no allow file."""
    if not LOCAL_SERVICE_ACCOUNT_FILE.exists():
        return ()
    names = []
    for line in LOCAL_SERVICE_ACCOUNT_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            names.append(line)
    return tuple(names)


SERVICE_ACCOUNT_HOMES = load_service_account_homes()
_SVC_ALT = "".join(rf"{re.escape(a)}\b|" for a in SERVICE_ACCOUNT_HOMES)

# Team-mode deny patterns (generic — maintainer-specific ones live in the
# local deny file, never in this team-distributed script).
TEAM_DENY_PATTERNS = [
    # Real op:// secret references: vault segment containing a space is a
    # real vault name ("Team Secrets"), not a placeholder/teaching example.
    # Vault segment must not cross backticks/quotes/parens — prose *about*
    # op:// (e.g. this guide) must not self-trigger; only URI-shaped refs do.
    (r"op://[^/\n<>`'\"()]*[ ][^/\n`'\"()]*/", "real 1Password op:// reference (use a prose pointer: vault -> item -> field)"),
    # Placeholder usernames (username/user/yourname/example/name) are allowed —
    # docs legitimately demonstrate absolute paths (e.g. Claude Desktop MCP
    # config requires them); only a REAL person's home path is a violation.
    (rf"/Users/(?!username\b|user\b|yourname\b|you\b|example\b|name\b|{_SVC_ALT}<)[A-Za-z][A-Za-z0-9._-]*/", "absolute personal home path (/Users/...)"),
    (rf"/home/(?!username\b|user\b|yourname\b|you\b|example\b|name\b|{_SVC_ALT}<)[A-Za-z][A-Za-z0-9._-]*/", "absolute personal home path (/home/...)"),
    (r"-----BEGIN [A-Z ]*PRIVATE KEY-----", "private key material"),
    (r"\bAKIA[0-9A-Z]{16}\b", "AWS access key id"),
]

LOCAL_DENY_FILE = Path(
    os.environ.get("SKILL_PACKAGING_DENY_FILE")
    or Path.home() / ".claude" / "packaging-deny-patterns.txt"
).expanduser()


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

    # 4. SKILL.md frontmatter must be LITERAL text (Claude Desktop validator)
    for path, arc in files:
        if path.name != "SKILL.md" or arc.count("/") != 1:
            continue  # only the wrapper-root SKILL.md carries the skill frontmatter
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        errors.extend(f"{arc}: {e}" for e in check_frontmatter_literal(text))

    # 5. Team-mode secret / personal-content scan
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


FRONTMATTER_ESCAPE_RX = re.compile(r"\\(?:u[0-9A-Fa-f]{4}|U[0-9A-Fa-f]{8}|x[0-9A-Fa-f]{2})")


def check_frontmatter_literal(skill_md_text: str) -> list[str]:
    """Return errors if the SKILL.md frontmatter is not written literally.

    Claude Desktop's skill validator (observed 2026-09-10) rejects a SKILL.md
    whose frontmatter contains a hex/unicode escape (`\\u2014`, `\\x..`,
    `\\U........`) or an escaped line break (a line ending in `\\` inside a
    double-quoted scalar) — "which can spell keys some parsers see and others
    don't. Write the text literally." Both are what a YAML dumper emits for
    non-ASCII text at the default 80-column width (PyYAML without
    allow_unicode). Also requires the `name:` and `description:` keys.
    """
    m = re.match(r"^---\n(.*?)\n---\n", skill_md_text, re.DOTALL)
    if not m:
        return ["SKILL.md has no YAML frontmatter (--- ... ---)"]
    fm = m.group(1)
    errors: list[str] = []
    for i, line in enumerate(fm.split("\n"), start=2):
        esc = FRONTMATTER_ESCAPE_RX.search(line)
        if esc:
            errors.append(
                f"frontmatter line {i} contains escape {esc.group(0)!r} — "
                "Claude Desktop rejects; write the character literally"
            )
        if line.rstrip().endswith("\\"):
            errors.append(
                f"frontmatter line {i} ends with an escaped line break — "
                "Claude Desktop rejects; keep the value on one line"
            )
    for key in ("name", "description"):
        if not re.search(rf"^{key}:", fm, re.M):
            errors.append(f"frontmatter missing required key `{key}:`")
    return errors


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


def check_archive_layout(names: list[str], expected_wrapper: str | None = None) -> list[str]:
    """Return errors if the zip member names do not form ONE top-level folder.

    Pure function over archive member names (e.g. ZipFile.namelist()) — no
    I/O. Claude.ai's skill uploader (observed 2026-09-21) rejects the whole
    archive with "All files must be inside the top-level folder" when any
    member sits outside a single wrapper directory: a bare root-level file
    (a manifest.json appended without the folder prefix was the real bite),
    a second top-level folder, a Finder/ditto `__MACOSX/` tree, or a
    root-level `.DS_Store`. `expected_wrapper`, when given, must equal the
    single top-level folder name. An explicit directory entry for the
    wrapper itself (`skill/`) is tolerated — some zip writers emit one — and
    extra files inside the wrapper are fine.
    """
    errors: list[str] = []
    root_files: list[str] = []
    top_levels: set[str] = set()

    for name in names:
        if name.startswith("__MACOSX/") or name == "__MACOSX":
            errors.append(
                f"Finder/ditto artefact in zip: {name} (Claude rejects; "
                "build with zipfile, or `zip -X` without __MACOSX)"
            )
            continue
        if "/" not in name:
            if name == ".DS_Store":
                errors.append(
                    "root-level .DS_Store in zip (Finder artefact; Claude rejects)"
                )
            else:
                root_files.append(name)
            continue
        top_levels.add(name.split("/", 1)[0])

    for name in root_files:
        errors.append(
            f"bare root-level file: {name} — every member must sit inside the "
            "single top-level skill folder (Claude rejects: \"All files must "
            "be inside the top-level folder\")"
        )
    if len(top_levels) > 1:
        errors.append(
            "more than one top-level folder in zip: "
            f"{sorted(top_levels)} — a skill zip holds exactly one wrapper folder"
        )
    if expected_wrapper is not None and len(top_levels) == 1:
        (found,) = top_levels
        if found != expected_wrapper:
            errors.append(
                f"top-level folder is {found}/ but expected {expected_wrapper}/ "
                "(wrapper folder must match the skill name)"
            )
    if not top_levels and not errors:
        errors.append("zip has no members inside a top-level folder")
    return errors


class StagedZip:
    """Build-then-swap target for a skill zip: all or nothing at `final_path`.

    The caller writes the archive to `tmp_path` (a hidden sibling of
    `final_path`, so the final move never crosses a filesystem), runs every
    post-zip check against `tmp_path`, and calls `commit()` only when they all
    pass. `commit()` is one atomic `os.replace`: a reader of `final_path` sees
    either the previous complete zip or the new complete zip, never a partial
    one. Leaving the `with` block without committing (failed check, exception,
    KeyboardInterrupt) removes `tmp_path` and leaves `final_path` untouched.

    Failure paths:
      - check fails / exception / Ctrl-C  -> temp removed, final untouched
      - process killed outright (SIGKILL, power loss) before commit -> final
        untouched; a stray `.<name>.zip.<pid>.tmp` may remain in the output
        directory and is safe to delete
      - two builds of the same zip at once -> each has its own temp file (the
        name carries the process id), so neither corrupts the other; the last
        commit wins
    The temp name deliberately does not end in `.zip`, so a listing of
    `*.zip` in the output directory never picks up an unverified build.
    """

    def __init__(self, final_path):
        self.final_path = Path(final_path)
        self.tmp_path = self.final_path.parent / (
            f".{self.final_path.name}.{os.getpid()}.tmp"
        )

    def __enter__(self) -> "StagedZip":
        self._discard()  # leftover from an earlier killed run that reused this pid
        return self

    def commit(self) -> Path:
        """Atomically move the verified temp file onto the final path."""
        os.replace(self.tmp_path, self.final_path)
        return self.final_path

    def __exit__(self, exc_type, exc, tb) -> bool:
        self._discard()
        return False  # never swallow the caller's exception

    def _discard(self) -> None:
        try:
            self.tmp_path.unlink()
        except FileNotFoundError:
            pass


def report(errors: list[str], warnings: list[str]) -> None:
    """Print check results in a consistent format."""
    for w in warnings:
        print(f"  ! WARNING: {w}")
    for e in errors:
        print(f"  X ERROR: {e}")
