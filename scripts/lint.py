"""Lint code."""

import os
import sys

exit_code = 0
exit_code |= os.system("flake8 . --max-line-length=100")
exit_code |= os.system("mypy --ignore-missing-imports .")
sys.exit(exit_code)
