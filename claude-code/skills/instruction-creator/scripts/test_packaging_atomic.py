#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["pyyaml>=6"]
# ///
"""Regression tests: a failed skill-zip build never touches the existing zip.

Both packagers (convert_to_claudeai.py, package_skill.py) used to write the new
archive straight to the output path and delete it when a post-zip check failed,
so an oversized rebuild destroyed the last good zip. They now build to a
temporary sibling and move it into place only when every check passes
(packaging_checks.StagedZip). These tests pin that behaviour.

stdlib unittest; every fixture lives in a temporary directory and no real skill
is packaged. convert_to_claudeai.py needs PyYAML, so run from the skill
directory with either:

    uv run --script scripts/test_packaging_atomic.py
    python3 scripts/test_packaging_atomic.py      (re-runs itself through uv)

With neither PyYAML nor uv available, a direct run exits with an install hint;
`python3 -m unittest test_packaging_atomic` (from this scripts directory) still
runs the other tests and skips the converter tests.
"""

from __future__ import annotations

import contextlib
import io
import os
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

if __name__ == "__main__":
    from _script_deps import ensure_modules
    ensure_modules(__file__, any_of=("ruamel.yaml", "yaml"), pip_name="pyyaml")

import package_skill as pkg  # noqa: E402
import packaging_checks  # noqa: E402
from packaging_checks import StagedZip  # noqa: E402

try:
    import convert_to_claudeai as conv  # noqa: E402
except SystemExit:  # no YAML library in this interpreter
    conv = None

SKILL = "demo-skill"
OLD_BYTES = b"PREVIOUS GOOD ZIP - must survive a failed build byte for byte\n" * 8
SKILL_MD = (
    "---\n"
    f"name: {SKILL}\n"
    "description: Fixture skill used only by the packaging tests.\n"
    "---\n"
    "# Demo skill\n\nBody text for the fixture.\n"
)


class Fixture(unittest.TestCase):
    """A throwaway skill source dir plus an output dir, both under one tempdir."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        root = Path(self._tmp.name).resolve()
        self.skill_dir = root / "src" / SKILL
        (self.skill_dir / "references").mkdir(parents=True)
        (self.skill_dir / "SKILL.md").write_text(SKILL_MD, encoding="utf-8")
        (self.skill_dir / "references" / "notes.md").write_text("notes\n", encoding="utf-8")
        self.out = root / "out"
        self.out.mkdir()
        self.zip_path = self.out / f"{SKILL}.zip"

    def seed_old_zip(self) -> None:
        self.zip_path.write_bytes(OLD_BYTES)

    def out_names(self) -> list[str]:
        return sorted(p.name for p in self.out.iterdir())

    def assert_old_zip_untouched(self) -> None:
        self.assertEqual(self.zip_path.read_bytes(), OLD_BYTES)
        self.assertEqual(self.out_names(), [f"{SKILL}.zip"],
                         "temporary build file or staging dir left behind")

    def assert_new_zip_in_place(self) -> None:
        self.assertEqual(self.out_names(), [f"{SKILL}.zip"],
                         "temporary build file or staging dir left behind")
        self.assertNotEqual(self.zip_path.read_bytes(), OLD_BYTES)
        with zipfile.ZipFile(self.zip_path) as zf:
            self.assertIsNone(zf.testzip())
            names = zf.namelist()
        self.assertIn(f"{SKILL}/SKILL.md", names)
        self.assertIn(f"{SKILL}/references/notes.md", names)

    def add_big_files(self) -> None:
        """Two incompressible 16 MB files: a zip genuinely over the 30 MB cap."""
        for i in (1, 2):
            (self.skill_dir / "references" / f"blob-{i}.bin").write_bytes(
                os.urandom(16 * 1024 * 1024))


def quiet(fn, *args, **kwargs):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        result = fn(*args, **kwargs)
    return result, buf.getvalue()


# --------------------------------------------------------------------------
# StagedZip
# --------------------------------------------------------------------------

class StagedZipTests(Fixture):
    def test_commit_replaces_final_and_removes_temp(self) -> None:
        self.seed_old_zip()
        with StagedZip(self.zip_path) as staged:
            self.assertEqual(staged.tmp_path.parent, self.out)
            self.assertFalse(staged.tmp_path.name.endswith(".zip"))
            staged.tmp_path.write_bytes(b"new")
            self.assertEqual(self.zip_path.read_bytes(), OLD_BYTES)  # not yet swapped
            staged.commit()
        self.assertEqual(self.zip_path.read_bytes(), b"new")
        self.assertEqual(self.out_names(), [f"{SKILL}.zip"])

    def test_no_commit_discards_temp_and_keeps_final(self) -> None:
        self.seed_old_zip()
        with StagedZip(self.zip_path) as staged:
            staged.tmp_path.write_bytes(b"new")
        self.assert_old_zip_untouched()

    def test_exception_discards_temp_and_propagates(self) -> None:
        self.seed_old_zip()
        for exc in (RuntimeError, KeyboardInterrupt):
            with self.subTest(exc=exc.__name__):
                with self.assertRaises(exc):
                    with StagedZip(self.zip_path) as staged:
                        staged.tmp_path.write_bytes(b"partial")
                        raise exc()
                self.assert_old_zip_untouched()

    def test_stale_temp_from_earlier_run_is_cleared(self) -> None:
        self.seed_old_zip()
        stale = StagedZip(self.zip_path).tmp_path
        stale.write_bytes(b"stale leftover")
        with StagedZip(self.zip_path) as staged:
            self.assertFalse(staged.tmp_path.exists())
        self.assert_old_zip_untouched()

    def test_no_commit_without_existing_final_leaves_nothing(self) -> None:
        with StagedZip(self.zip_path) as staged:
            staged.tmp_path.write_bytes(b"new")
        self.assertEqual(self.out_names(), [])


# --------------------------------------------------------------------------
# convert_to_claudeai.py
# --------------------------------------------------------------------------

@unittest.skipIf(conv is None, "PyYAML not available (run via uv; see module docstring)")
class ConverterTests(Fixture):
    def convert(self, **kwargs):
        converter = conv.SkillConverter(self.skill_dir, self.out, **kwargs)
        return quiet(converter.convert)

    def test_existing_zip_survives_size_cap_failure(self) -> None:
        self.seed_old_zip()
        with mock.patch.object(packaging_checks, "ZIP_HARD_CAP_BYTES", 10):
            result, output = self.convert()
        self.assertIsNone(result)
        self.assertIn("exceeds the 30 MB", output)
        self.assert_old_zip_untouched()

    def test_existing_zip_survives_layout_failure(self) -> None:
        self.seed_old_zip()
        with mock.patch.object(conv, "check_archive_layout",
                               return_value=["bare root-level file: stray.json"]):
            result, output = self.convert()
        self.assertIsNone(result)
        self.assertIn("Archive layout rejected (1 error(s))", output)
        self.assert_old_zip_untouched()

    def test_existing_zip_survives_pre_zip_check_failure(self) -> None:
        self.seed_old_zip()
        (self.skill_dir / "references" / "bad name.md").write_text("x\n", encoding="utf-8")
        result, output = self.convert()
        self.assertIsNone(result)
        self.assertIn("Packaging checks failed", output)
        self.assert_old_zip_untouched()

    def test_existing_zip_survives_exception_while_writing(self) -> None:
        self.seed_old_zip()
        with mock.patch.object(zipfile.ZipFile, "write", side_effect=OSError("disk full")):
            result, output = self.convert()
        self.assertIsNone(result)
        self.assertIn("Error during conversion: disk full", output)
        self.assert_old_zip_untouched()

    def test_passing_build_replaces_existing_zip(self) -> None:
        self.seed_old_zip()
        result, output = self.convert()
        self.assertEqual(result, self.zip_path)
        self.assertIn(f"Created zip: {SKILL}.zip", output)
        self.assertIn(f"Output: {self.zip_path}", output)
        self.assert_new_zip_in_place()

    def test_passing_build_without_existing_zip(self) -> None:
        result, _ = self.convert()
        self.assertEqual(result, self.zip_path)
        self.assert_new_zip_in_place()

    def test_failed_build_without_existing_zip_leaves_nothing(self) -> None:
        with mock.patch.object(packaging_checks, "ZIP_HARD_CAP_BYTES", 10):
            result, _ = self.convert()
        self.assertIsNone(result)
        self.assertEqual(self.out_names(), [])

    def test_dry_run_writes_nothing(self) -> None:
        self.seed_old_zip()
        result, _ = self.convert(dry_run=True)
        self.assertEqual(result, self.zip_path)
        self.assert_old_zip_untouched()

    # --- the command line: exit codes, and the real (unpatched) size cap ---

    def run_cli(self, *extra: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(HERE / "convert_to_claudeai.py"),
             str(self.skill_dir), str(self.out), *extra],
            capture_output=True, text=True, timeout=300)

    def test_cli_oversized_rebuild_exits_1_and_keeps_existing_zip(self) -> None:
        self.seed_old_zip()
        self.add_big_files()
        proc = self.run_cli()
        self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
        self.assertIn("exceeds the 30 MB", proc.stdout)
        self.assertIn("Conversion failed.", proc.stdout)
        self.assert_old_zip_untouched()

    def test_cli_passing_build_exits_0_and_replaces_existing_zip(self) -> None:
        self.seed_old_zip()
        proc = self.run_cli()
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("Conversion successful!", proc.stdout)
        self.assert_new_zip_in_place()

    def test_cli_dry_run_creates_no_output_dir(self) -> None:
        self.out.rmdir()
        proc = self.run_cli("--dry-run")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertFalse(self.out.exists())


# --------------------------------------------------------------------------
# package_skill.py
# --------------------------------------------------------------------------

class PackageSkillTests(Fixture):
    def package(self, **kwargs):
        return quiet(pkg.package_skill, self.skill_dir, self.out, **kwargs)

    def test_existing_zip_survives_size_cap_failure(self) -> None:
        self.seed_old_zip()
        with mock.patch.object(packaging_checks, "ZIP_HARD_CAP_BYTES", 10):
            result, output = self.package()
        self.assertIsNone(result)
        self.assertIn("exceeds the 30 MB", output)
        self.assert_old_zip_untouched()

    def test_existing_zip_survives_layout_failure(self) -> None:
        self.seed_old_zip()
        with mock.patch.object(pkg, "check_archive_layout",
                               return_value=["bare root-level file: stray.json"]):
            result, output = self.package()
        self.assertIsNone(result)
        self.assertIn("Archive layout rejected (1 error(s))", output)
        self.assert_old_zip_untouched()

    def test_existing_zip_survives_pre_zip_check_failure(self) -> None:
        self.seed_old_zip()
        (self.skill_dir / "references" / "bad name.md").write_text("x\n", encoding="utf-8")
        result, output = self.package()
        self.assertIsNone(result)
        self.assertIn("Packaging checks failed", output)
        self.assert_old_zip_untouched()

    def test_existing_zip_survives_exception_while_writing(self) -> None:
        self.seed_old_zip()
        with mock.patch.object(zipfile.ZipFile, "write", side_effect=OSError("disk full")):
            result, output = self.package()
        self.assertIsNone(result)
        self.assertIn("Error creating zip file: disk full", output)
        self.assert_old_zip_untouched()

    def test_passing_build_replaces_existing_zip(self) -> None:
        self.seed_old_zip()
        result, output = self.package()
        self.assertEqual(result, self.zip_path)
        self.assertIn(f"Successfully packaged skill to: {self.zip_path}", output)
        self.assert_new_zip_in_place()

    def test_passing_build_without_existing_zip(self) -> None:
        result, _ = self.package()
        self.assertEqual(result, self.zip_path)
        self.assert_new_zip_in_place()

    def test_cli_oversized_rebuild_exits_1_and_keeps_existing_zip(self) -> None:
        self.seed_old_zip()
        self.add_big_files()
        proc = subprocess.run(
            [sys.executable, str(HERE / "package_skill.py"), str(self.skill_dir), str(self.out)],
            capture_output=True, text=True, timeout=300)
        self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
        self.assertIn("exceeds the 30 MB", proc.stdout)
        self.assert_old_zip_untouched()

    def test_cli_passing_build_exits_0_and_replaces_existing_zip(self) -> None:
        self.seed_old_zip()
        proc = subprocess.run(
            [sys.executable, str(HERE / "package_skill.py"), str(self.skill_dir), str(self.out)],
            capture_output=True, text=True, timeout=300)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assert_new_zip_in_place()


if __name__ == "__main__":
    unittest.main(verbosity=2)
