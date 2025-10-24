"""Scripts for code formatting and linting."""

import subprocess
import sys


def run_cmd(cmd: str) -> int:
    """Run command and return exit code."""
    return subprocess.run(cmd, shell=True).returncode


def format_code():
    """Format code with black and isort."""
    print("🎨 Formatting code...")
    run_cmd("black --line-length 100 .")
    run_cmd("isort --profile black --line-length 100 .")
    print("✅ Formatting complete!")


def lint_code():
    """Check code style with flake8 and mypy."""
    print("🔍 Linting code...")
    exit_code = 0
    exit_code |= run_cmd("flake8 . --max-line-length=100")
    exit_code |= run_cmd("mypy --ignore-missing-imports .")
    if exit_code == 0:
        print("✅ Linting passed!")
    else:
        print("❌ Linting failed!")
        sys.exit(1)


def check_all():
    """Run all checks including pre-commit."""
    print("🚀 Running all checks...")
    format_code()
    lint_code()
    print("🔍 Running pre-commit hooks...")
    exit_code = run_cmd("pre-commit run --all-files")
    if exit_code == 0:
        print("✅ All checks passed!")
    else:
        print("❌ Some checks failed!")
        sys.exit(1)
