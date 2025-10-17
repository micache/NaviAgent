# Development Setup Guide

This guide will help you set up the development environment for NaviAgent with all the necessary tools for code style checking and testing.

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- git

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/micache/NaviAgent.git
cd NaviAgent
```

### 2. Create a Virtual Environment (Recommended)

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Development Dependencies

```bash
pip install -r requirements-dev.txt
```

Or install from pyproject.toml:

```bash
pip install -e ".[dev]"
```

## Pre-commit Hooks Setup

Pre-commit hooks automatically check your code before each commit to ensure it follows the project's style guidelines.

### Install Pre-commit Hooks

```bash
pre-commit install
```

### Run Pre-commit Hooks Manually

To run all pre-commit hooks on all files:

```bash
pre-commit run --all-files
```

To run a specific hook:

```bash
pre-commit run black --all-files
pre-commit run flake8 --all-files
```

## Code Style Tools

This project follows Google's Python Style Guide and uses the following tools:

### Black (Code Formatter)

Black automatically formats your code to be PEP 8 compliant.

```bash
# Check formatting (doesn't modify files)
black --check --line-length 100 .

# Format all files
black --line-length 100 .
```

### isort (Import Sorter)

isort organizes your imports according to best practices.

```bash
# Check import sorting
isort --check-only --profile black --line-length 100 .

# Sort imports
isort --profile black --line-length 100 .
```

### Flake8 (Linter)

Flake8 checks your code for style issues and potential errors.

```bash
flake8 . --count --max-line-length=100 --extend-ignore=E203,E501,W503 --statistics
```

### autoflake (Unused Import Remover)

autoflake removes unused imports and variables.

```bash
# Check for unused imports (doesn't modify files)
autoflake --check --recursive --remove-all-unused-imports --remove-unused-variables .

# Remove unused imports
autoflake --in-place --recursive --remove-all-unused-imports --remove-unused-variables .
```

### mypy (Type Checker)

mypy performs static type checking.

```bash
mypy --ignore-missing-imports .
```

### pydocstyle (Docstring Checker)

pydocstyle checks docstring conventions (Google style).

```bash
pydocstyle --convention=google --add-ignore=D100,D104,D105,D107 .
```

### bandit (Security Checker)

bandit checks for common security issues.

```bash
bandit -r .
```

## Running Tests

### Run All Tests

```bash
pytest
```

### Run Tests with Coverage

```bash
pytest --cov=. --cov-report=term-missing --cov-report=html
```

### Run Specific Tests

```bash
# Run tests in a specific file
pytest tests/test_example.py

# Run a specific test class
pytest tests/test_example.py::TestCalculator

# Run a specific test method
pytest tests/test_example.py::TestCalculator::test_calculator_add
```

## Continuous Integration

This project uses GitHub Actions for CI/CD. The workflow runs automatically on:

- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches
- Manual trigger via GitHub Actions UI

The CI pipeline includes:

1. **Style Check** - Runs on Python 3.8-3.12
   - Black formatting check
   - isort import sorting check
   - Flake8 linting
   - autoflake unused imports check
   - mypy type checking (informational)
   - bandit security scanning (informational)
   - pydocstyle docstring checking (informational)

2. **Unit Tests** - Runs on Python 3.8-3.12
   - pytest with coverage reporting
   - Uploads coverage to Codecov (on Python 3.11)

3. **Pre-commit Hooks** - Runs all pre-commit hooks

## Configuration Files

- **pyproject.toml** - Central configuration for all tools
- **.pre-commit-config.yaml** - Pre-commit hooks configuration
- **requirements-dev.txt** - Development dependencies
- **.github/workflows/ci.yml** - GitHub Actions CI/CD workflow

## Code Style Guidelines

This project follows the Google Python Style Guide with some modifications:

- **Line Length**: 100 characters (instead of 80)
- **Docstrings**: Google style docstrings are required for all public modules, classes, and functions
- **Type Hints**: Use type hints for function parameters and return values
- **Import Order**: Standard library, third-party, local application (managed by isort)
- **Formatting**: Handled by Black (PEP 8 compliant)

## Troubleshooting

### Pre-commit Hook Failures

If a pre-commit hook fails:

1. Read the error message to understand what needs to be fixed
2. Run the specific tool manually to see more details
3. Fix the issues or let the auto-fixing tools (like Black) fix them
4. Stage the fixed files and commit again

### Test Failures

If tests fail:

1. Run the specific failing test with `-v` for verbose output
2. Check the test output for assertion errors
3. Use `pytest --pdb` to drop into a debugger on failure
4. Fix the code or update the test as appropriate

## Additional Resources

- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [Black Documentation](https://black.readthedocs.io/)
- [Flake8 Documentation](https://flake8.pycqa.org/)
- [pytest Documentation](https://docs.pytest.org/)
- [pre-commit Documentation](https://pre-commit.com/)
