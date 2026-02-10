#!/usr/bin/env python3
"""
CodeSense Setup Script

Manages virtual environment and dependencies for CodeSense skill.
Creates an isolated environment to avoid system Python conflicts.
"""

import os
import sys
import subprocess
import venv
from pathlib import Path


class CodeSenseSetup:
    def __init__(self):
        self.skill_dir = Path(__file__).parent
        self.venv_dir = self.skill_dir / ".codesense_env"
        self.python_exe = self._get_venv_python()

    def _get_venv_python(self):
        """Get the Python executable path for the virtual environment."""
        if sys.platform == "win32":
            return self.venv_dir / "Scripts" / "python.exe"
        else:
            return self.venv_dir / "bin" / "python"

    def venv_exists(self):
        """Check if the virtual environment already exists."""
        return self.venv_dir.exists() and self.python_exe.exists()

    def create_venv(self):
        """Create a new virtual environment."""
        print(f"🔧 Creating virtual environment at {self.venv_dir}")
        try:
            venv.create(self.venv_dir, with_pip=True, clear=True)

            # Validate that the Python executable was created and works
            if not self.python_exe.exists():
                raise Exception(f"Python executable not found at {self.python_exe}")

            # Test that the Python executable actually works
            result = subprocess.run(
                [str(self.python_exe), "--version"],
                capture_output=True,
                text=True,
                check=True,
            )
            print(
                f"✅ Virtual environment created successfully (Python {result.stdout.strip()})"
            )
            return True

        except Exception as e:
            print(f"❌ Failed to create virtual environment: {e}")
            return False

    def install_dependencies(self):
        """Install required dependencies in the virtual environment."""
        dependencies = [
            "sentence-transformers",
            "torch",
            "tree-sitter-languages",
            "numpy",
        ]

        print("📦 Installing dependencies in virtual environment...")
        print("    This may take 2-5 minutes for first-time setup...")

        try:
            # Validate Python executable works before starting
            result = subprocess.run(
                [str(self.python_exe), "--version"],
                capture_output=True,
                text=True,
                check=True,
            )

            # Upgrade pip first
            print("  Upgrading pip...")
            subprocess.run(
                [str(self.python_exe), "-m", "pip", "install", "--upgrade", "pip"],
                check=True,
                capture_output=True,
                text=True,
            )

            # Install dependencies one by one with progress
            for i, dep in enumerate(dependencies, 1):
                print(f"  [{i}/{len(dependencies)}] Installing {dep}...")
                result = subprocess.run(
                    [str(self.python_exe), "-m", "pip", "install", dep],
                    check=True,
                    capture_output=True,
                    text=True,
                )

            print("✅ All dependencies installed successfully")

            # Immediate validation after installation
            if not self.verify_installation():
                print("❌ Post-installation verification failed")
                return False

            return True

        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            if e.stdout:
                print("STDOUT:", e.stdout[-500:])  # Show last 500 chars
            if e.stderr:
                print("STDERR:", e.stderr[-500:])  # Show last 500 chars
            return False
        except Exception as e:
            print(f"❌ Unexpected error during installation: {e}")
            return False

    def verify_installation(self):
        """Verify that all dependencies are correctly installed."""
        print("🔍 Verifying installation...")

        # First check if Python executable works
        try:
            result = subprocess.run(
                [str(self.python_exe), "--version"],
                capture_output=True,
                text=True,
                check=True,
            )
            print(f"  ✓ Python executable working: {result.stdout.strip()}")
        except Exception as e:
            print(f"  ❌ Python executable failed: {e}")
            return False

        # Test imports one by one for better error reporting
        test_imports = [
            ("torch", "import torch"),
            (
                "sentence_transformers",
                "from sentence_transformers import SentenceTransformer",
            ),
            ("tree_sitter_languages", "from tree_sitter_languages import get_parser"),
            ("numpy", "import numpy as np"),
        ]

        failed_imports = []
        for package_name, import_stmt in test_imports:
            try:
                result = subprocess.run(
                    [str(self.python_exe), "-c", import_stmt],
                    check=True,
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                print(f"  ✓ {package_name} import successful")
            except subprocess.TimeoutExpired:
                print(f"  ❌ {package_name} import timed out (>30s)")
                failed_imports.append(package_name)
            except subprocess.CalledProcessError as e:
                print(
                    f"  ❌ {package_name} import failed: {e.stderr.strip() if e.stderr else 'Unknown error'}"
                )
                failed_imports.append(package_name)

        if failed_imports:
            print(f"❌ Failed to import: {', '.join(failed_imports)}")
            print("💡 Try running setup again with --force to reinstall")
            return False

        print("✅ All dependencies verified successfully")
        return True

    def setup(self, force=False):
        """Complete setup process."""
        print("🚀 CodeSense Setup")
        print("=" * 30)

        # Check if already set up and working
        if self.venv_exists() and not force:
            print("📋 Virtual environment already exists")
            print("🔍 Testing existing installation...")
            if self.verify_installation():
                print("✅ CodeSense is ready to use!")
                return True
            else:
                print("⚠️  Dependencies verification failed")
                print("💡 Suggestion: Run with --force to reinstall dependencies")
                return False

        # Clean start if forced or doesn't exist
        if force and self.venv_dir.exists():
            print("🧹 Removing existing virtual environment...")
            import shutil

            shutil.rmtree(self.venv_dir)

        # Create virtual environment
        if not self.create_venv():
            print("💡 Troubleshooting tips:")
            print("  - Ensure you have Python 3.8+ available")
            print("  - Check disk space and permissions")
            print("  - Try running as: python scripts/setup.py --force")
            return False

        # Install dependencies with progress tracking
        if not self.install_dependencies():
            print("💡 Installation failed. Possible solutions:")
            print("  - Check internet connection")
            print("  - Try again later (PyTorch servers may be busy)")
            print("  - Run: python scripts/setup.py --force")
            print("  - Check available disk space (needs ~2GB)")
            return False

        # Final verification
        print("🔍 Performing final verification...")
        if not self.verify_installation():
            print("💡 Setup completed but verification failed:")
            print("  - Dependencies installed but may not be working")
            print("  - Try restarting your terminal")
            print("  - Or run: python scripts/setup.py --force")
            return False

        print(f"\n✅ CodeSense setup completed successfully!")
        print(f"   Virtual environment: {self.venv_dir}")
        print(f"   Python executable: {self.python_exe}")
        print("   Ready to index and search code!")

        return True

    def get_python_path(self):
        """Get the path to the virtual environment Python executable."""
        return str(self.python_exe)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Setup CodeSense virtual environment")
    parser.add_argument(
        "--force", action="store_true", help="Force recreation of virtual environment"
    )
    parser.add_argument(
        "--python-path",
        action="store_true",
        help="Print the virtual environment Python path",
    )

    args = parser.parse_args()

    setup = CodeSenseSetup()

    if args.python_path:
        if setup.venv_exists():
            print(setup.get_python_path())
            return 0
        else:
            print("Virtual environment not found. Run setup first.", file=sys.stderr)
            return 1

    success = setup.setup(force=args.force)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
