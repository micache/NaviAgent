"""Run all checks."""

import os
import sys

print("🎨 Formatting...")
os.system("black --line-length 100 .")
os.system("isort --profile black --line-length 100 .")
print("🔍 Linting...")
exit_code = os.system("flake8 . --max-line-length=100")
exit_code |= os.system("mypy --ignore-missing-imports .")
print("🔍 Pre-commit...")
exit_code |= os.system("pre-commit run --all-files")
sys.exit(exit_code)
