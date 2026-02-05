#!/usr/bin/env python3
"""
Wrapper script that ensures docling is available before running conversion.
This handles virtual environment setup automatically.
"""
import sys
import subprocess
from pathlib import Path


def ensure_docling():
    """Check if docling is available, install if needed."""
    try:
        import docling
        return True
    except ImportError:
        pass
    
    # Try to setup venv
    script_dir = Path(__file__).parent
    setup_script = script_dir / "setup_venv.sh"
    venv_dir = script_dir / ".venv"
    
    if not venv_dir.exists():
        print("Setting up virtual environment with docling...")
        if setup_script.exists():
            subprocess.run(["bash", str(setup_script)], check=True)
        else:
            # Fallback: create venv and install directly
            subprocess.run([sys.executable, "-m", "venv", str(venv_dir)], check=True)
            pip = venv_dir / "bin" / "pip"
            subprocess.run([str(pip), "install", "docling"], check=True)
    
    # Try importing again
    venv_python = venv_dir / "bin" / "python"
    return venv_python if venv_python.exists() else None


def run_with_venv(script_name, args):
    """Run a conversion script, using venv if needed."""
    script_dir = Path(__file__).parent
    venv_python = script_dir / ".venv" / "bin" / "python"
    script_path = script_dir / script_name
    
    if venv_python.exists():
        # Use venv python
        cmd = [str(venv_python), str(script_path)] + args
    else:
        # Use system python
        cmd = [sys.executable, str(script_path)] + args
    
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
    ensure_docling()
    
    # Run conversion
    sys.exit(run_with_venv(script, args))
