"""Self-bootstrap for skill scripts that need third-party packages.

Each entry script declares its packages in a PEP 723 header
(`# /// script` ... `# ///`). When it runs under an interpreter that lacks
them — plain `python3`, `sys.executable` from a parent script, or a
background agent limited to `python3` — `ensure_modules()` re-runs the
script once via `uv run --script`, which reads that header and supplies the
packages from a cached, isolated environment. Nothing is installed globally.

No uv and no package → exit with one actionable message. An environment
guard stops the re-run from looping if uv's environment still lacks it.
"""

import importlib
import os
import shutil
import subprocess
import sys

_GUARD = "SKILL_SCRIPT_UV_BOOTSTRAPPED"


def _importable(module: str) -> bool:
    try:
        importlib.import_module(module)
        return True
    except ImportError:
        return False


def ensure_modules(script: str, any_of: tuple, pip_name: str) -> None:
    """Return if any module in `any_of` imports; otherwise re-run `script` under uv."""
    if any(_importable(m) for m in any_of):
        return
    uv = shutil.which("uv")
    if uv and not os.environ.get(_GUARD):
        env = dict(os.environ, **{_GUARD: "1"})
        cmd = [uv, "run", "--quiet", "--script", os.path.abspath(script), *sys.argv[1:]]
        if os.name == "nt":  # execve does not replace the process cleanly on Windows
            sys.exit(subprocess.call(cmd, env=env))
        os.execve(uv, cmd, env)
    name = os.path.basename(script)
    sys.exit(
        f"Error: {name} needs the Python package '{pip_name}', which is not available.\n"
        f"  Recommended: install uv (https://docs.astral.sh/uv/), then run: uv run {name} ...\n"
        f"  Alternative: inside a virtual environment, pip install {pip_name}"
    )
