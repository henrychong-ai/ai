# Skill-Edit Safety — Never Wipe the Body

A rule for any **bulk** or **frontmatter-only** edit to `SKILL.md` files.

## The failure mode

A bulk operation meant to change only the `description:` frontmatter field can, if it regenerates each `SKILL.md` from the frontmatter alone, **silently delete the entire body** — every line after the closing `---`. The commit looks like a description change but is actually a mass body-deletion. Because an "empty SKILL.md body" can be mistaken for a deliberate thin-skill design, this can go unnoticed across many skills at once. Bodies are recoverable from git (the parent of the offending commit), but prevention beats recovery.

## The rule

1. **Edit the field, not the file.** To change `description` (or any frontmatter field), modify *that line* in place. **Never regenerate or overwrite a whole `SKILL.md` from frontmatter alone.** The body is the skill's loaded-on-invocation instructions/router — it is content, not boilerplate.

## Mandatory verification (single or bulk)

Before committing any `SKILL.md` edit, assert the body survived:

```bash
body() { awk 'BEGIN{d=0}/^---$/{d++;next}d>=2&&NF{print}' "$1" | wc -l; }
# body count before == body count after
```

For a **bulk** edit, `git diff --stat` is the tripwire: a description-only change is roughly `+1/-1` per file. **Any `SKILL.md` showing large deletions (e.g. `+1/-200`) means its body was wiped — abort, do not commit.**

## Automated guard

`scripts/quick_validate.py` **fails on an empty body**. Run it on every edited skill; a "body is EMPTY (frontmatter-only)" failure means a wipe. It also enforces `description ≤ 1024 chars` and a strict YAML parse that catches unquoted-colon descriptions. Run from the command line, it always has PyYAML: it declares it in a PEP 723 header and re-runs itself through uv when started without it (imported as a library, the strict parse still runs only if PyYAML is present).

```bash
uv run <ic>/scripts/quick_validate.py <skill-dir>   # <ic> = this skill's base directory
```

## Bulk-edit protocol (the safe way to touch many skills)

1. Script the change to operate on **one field**, preserving everything else (read → replace only the target line → write).
2. After writing, **re-read and assert the body-line-count is unchanged** per file; collect any file where it dropped.
3. `git diff --stat` review gate — eyeball for outsized deletions.
4. Run `quick_validate.py` across the batch; **zero failures** before staging.
5. Only then commit. If recovery is ever needed, the body is in git at `<wipe-commit>~1`.
