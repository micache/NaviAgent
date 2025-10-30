"""Format code."""

import os

os.system("black --line-length 100 .")
os.system("isort --profile black --line-length 100 .")
