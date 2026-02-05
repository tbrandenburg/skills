#!/usr/bin/env python3
"""Wrapper script that ensures docling is available before running conversion.

This script prefers an isolated virtual environment (scripts/.venv) to avoid
polluting the user's global Python environment and to keep dependencies stable.
"""
import sys
import subprocess
from pathlib import Path


def ensure_docling():
    """Ensure docling is installed in the local venv.

    Returns:
        Path to the venv python executable.
    """

    script_dir = Path(__file__).parent
    setup_script = script_dir / "setup_venv.sh"
    venv_dir = script_dir / ".venv"
    venv_python = venv_dir / "bin" / "python"
    venv_pip = venv_dir / "bin" / "pip"

    def _create_venv_if_missing():
        if venv_python.exists():
            return
        print("Setting up virtual environment with docling...")
        if setup_script.exists():
            subprocess.run(["bash", str(setup_script)], check=True)
        else:
            subprocess.run([sys.executable, "-m", "venv", str(venv_dir)], check=True)

    def _ensure_docling_in_venv():
        # Check import in the venv interpreter (not in the wrapper interpreter).
        proc = subprocess.run([str(venv_python), "-c", "import docling"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if proc.returncode == 0:
            return
        print("Installing docling in virtual environment...")
        if setup_script.exists():
            subprocess.run(["bash", str(setup_script)], check=True)
        else:
            subprocess.run([str(venv_pip), "install", "docling"], check=True)
            subprocess.run([str(venv_python), "-c", "import docling"], check=True)

    _create_venv_if_missing()
    if not venv_python.exists():
        raise RuntimeError(f"Virtual environment python not found at: {venv_python}")

    _ensure_docling_in_venv()
    return venv_python


def run_with_venv(script_name, args):
    """Run a conversion script, using venv if needed."""
    script_dir = Path(__file__).parent
    script_path = script_dir / script_name

    venv_python = ensure_docling()
    cmd = [str(venv_python), str(script_path)] + args
    return subprocess.run(cmd).returncode


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: run_conversion.py [full|chapters] <pdf_path> [options]")
        sys.exit(1)
    
    mode = sys.argv[1]
    if mode == "full":
        script = "convert_full.py"
        args = sys.argv[2:]
    elif mode == "chapters":
        script = "convert_by_chapters.py"
        args = sys.argv[2:]
    else:
        print(f"ERROR: Unknown mode '{mode}'. Use 'full' or 'chapters'")
        sys.exit(1)
    
    # Ensure docling is available
    # Run conversion
    sys.exit(run_with_venv(script, args))
