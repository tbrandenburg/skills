#!/usr/bin/env python3
"""
CodeSense Runner

Ensures virtual environment is set up and runs CodeSense commands using the isolated Python environment.
"""

import sys
import subprocess
from pathlib import Path


def get_venv_python():
    """Get the path to the virtual environment Python executable."""
    skill_dir = Path(__file__).parent
    setup_script = skill_dir / "setup.py"

    try:
        result = subprocess.run(
            [sys.executable, str(setup_script), "--python-path"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None


def ensure_setup():
    """Ensure CodeSense virtual environment is set up."""
    skill_dir = Path(__file__).parent
    setup_script = skill_dir / "setup.py"

    print("🔧 Checking CodeSense environment...")
    try:
        # Try setup with timeout to avoid hanging
        result = subprocess.run(
            [sys.executable, str(setup_script)], check=True, timeout=600
        )  # 10 minute timeout
        return True
    except subprocess.TimeoutExpired:
        print("⏰ Setup timed out (>10 minutes)")
        print("💡 This may indicate network issues or system constraints")
        print("💡 Try: python scripts/setup.py --force")
        return False
    except subprocess.CalledProcessError as e:
        print(f"❌ Setup failed with exit code {e.returncode}")
        print("💡 Run manually for more details: python scripts/setup.py --force")
        return False


def run_script(script_name, args):
    """Run a CodeSense script using the virtual environment."""
    skill_dir = Path(__file__).parent
    script_path = skill_dir / script_name

    if not script_path.exists():
        print(f"❌ Script not found: {script_name}")
        return 1

    # Get virtual environment Python
    venv_python = get_venv_python()
    if not venv_python:
        # Try to set up environment
        print("🔧 Virtual environment not ready, setting up...")
        if not ensure_setup():
            print("💡 Setup failed. You can:")
            print("  1. Run: python scripts/setup.py --force")
            print("  2. Check internet connection and disk space")
            print("  3. Report issues if problem persists")
            return 1
        venv_python = get_venv_python()
        if not venv_python:
            print("❌ Could not get virtual environment Python path")
            print("💡 Try: rm -rf scripts/.codesense_env && python scripts/setup.py")
            return 1

    # Validate venv python works before using it
    try:
        result = subprocess.run(
            [venv_python, "--version"],
            capture_output=True,
            text=True,
            check=True,
            timeout=10,
        )
        print(f"🐍 Using Python: {result.stdout.strip()}")
    except Exception as e:
        print(f"❌ Virtual environment Python not working: {e}")
        print("💡 Try: python scripts/setup.py --force")
        return 1

    # Run the script with the virtual environment Python
    try:
        result = subprocess.run([venv_python, str(script_path)] + args)
        return result.returncode
    except Exception as e:
        print(f"❌ Error running script: {e}")
        return 1


def main():
    if len(sys.argv) < 2:
        print("Usage: python run.py <script> [args...]")
        print("Available scripts: index.py, search.py")
        return 1

    script_name = sys.argv[1]
    args = sys.argv[2:]

    return run_script(script_name, args)


if __name__ == "__main__":
    sys.exit(main())
