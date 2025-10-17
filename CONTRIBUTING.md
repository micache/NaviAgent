# Contributing to NaviAgent

Thank you for your interest in contributing to NaviAgent! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

Please be respectful and constructive in all interactions with the project and its community.

## Development Setup

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/NaviAgent.git
   cd NaviAgent
   ```
3. Set up the development environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements-dev.txt
   pre-commit install
   ```

## Coding Standards

This project follows the **Google Python Style Guide** with these tools:

### Required Tools

- **Black**: Code formatter (line length: 100)
- **isort**: Import sorter
- **Flake8**: Linter with multiple plugins
- **autoflake**: Removes unused imports/variables
- **mypy**: Static type checker
- **pydocstyle**: Docstring checker (Google convention)
- **bandit**: Security checker

### Style Requirements

1. **Code Formatting**
   - All code must be formatted with Black (100 char line length)
   - Imports must be sorted with isort (Black profile)

2. **Type Hints**
   - Use type hints for all function parameters and return values
   - Example:
     ```python
     def calculate(x: int, y: int) -> int:
         """Calculate sum of two numbers."""
         return x + y
     ```

3. **Docstrings**
   - Use Google-style docstrings for all public modules, classes, and functions
   - Example:
     ```python
     def greet(name: str) -> str:
         """Greet a person by name.

         Args:
             name: The name of the person to greet.

         Returns:
             A greeting message string.

         Raises:
             ValueError: If name is empty.
         """
         if not name:
             raise ValueError("Name cannot be empty")
         return f"Hello, {name}!"
     ```

4. **Imports**
   - Standard library imports first
   - Third-party library imports second
   - Local application imports last
   - Each group separated by a blank line

5. **Line Length**
   - Maximum 100 characters per line
   - Break long lines appropriately

## Testing Requirements

1. **Unit Tests**
   - Write tests for all new functionality
   - Use pytest for testing
   - Follow the pattern: `tests/test_<module_name>.py`
   - Test class names should start with `Test`
   - Test method names should start with `test_`

2. **Test Coverage**
   - Aim for 100% code coverage
   - Run tests with coverage: `pytest --cov=. --cov-report=term-missing`
   - Coverage reports are generated in `htmlcov/` directory

3. **Test Structure**
   ```python
   import pytest
   from src.naviagent.module import function_to_test

   class TestFunctionToTest:
       """Test cases for function_to_test."""

       def test_normal_case(self):
           """Test normal operation."""
           result = function_to_test(valid_input)
           assert result == expected_output

       def test_edge_case(self):
           """Test edge case."""
           result = function_to_test(edge_input)
           assert result == expected_edge_output

       def test_error_case(self):
           """Test error handling."""
           with pytest.raises(ValueError):
               function_to_test(invalid_input)
   ```

## Workflow

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### 2. Make Changes

- Write your code following the style guidelines
- Add/update tests for your changes
- Update documentation if needed

### 3. Run Pre-commit Hooks

Pre-commit hooks will run automatically on `git commit`, but you can run them manually:

```bash
pre-commit run --all-files
```

### 4. Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=term-missing

# Run specific tests
pytest tests/test_example.py
```

### 5. Commit Changes

```bash
git add .
git commit -m "feat: add new feature"
```

**Commit Message Format:**
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting, etc.)
- `refactor:` - Code refactoring
- `test:` - Adding or updating tests
- `chore:` - Maintenance tasks

### 6. Push Changes

```bash
git push origin feature/your-feature-name
```

### 7. Create Pull Request

1. Go to GitHub and create a pull request
2. Fill in the PR template
3. Wait for CI checks to pass
4. Address any review comments

## Pre-commit Hooks

The following hooks run automatically before each commit:

1. **trailing-whitespace** - Removes trailing whitespace
2. **end-of-file-fixer** - Ensures files end with a newline
3. **check-yaml** - Validates YAML files
4. **check-json** - Validates JSON files
5. **check-toml** - Validates TOML files
6. **autoflake** - Removes unused imports and variables
7. **isort** - Sorts imports
8. **black** - Formats code
9. **flake8** - Lints code
10. **mypy** - Type checking
11. **bandit** - Security checks
12. **pydocstyle** - Docstring style checks

## Continuous Integration

All pull requests must pass CI checks:

1. **Style checks** on Python 3.8-3.12:
   - Black formatting
   - isort import sorting
   - Flake8 linting
   - autoflake unused imports check

2. **Unit tests** on Python 3.8-3.12:
   - All tests must pass
   - Coverage report generated

3. **Pre-commit hooks**:
   - All hooks must pass

## Common Issues

### Pre-commit Hook Failures

If pre-commit hooks fail:

1. Read the error message
2. Fix the issues (many are auto-fixed by the tools)
3. Stage the fixes: `git add .`
4. Commit again: `git commit -m "your message"`

### Test Failures

If tests fail:

1. Run tests locally: `pytest -v`
2. Check the failure message
3. Fix the code or test
4. Re-run tests to verify

### Import Errors

If you get import errors in tests:

1. Ensure you're in the virtual environment
2. Install the package in development mode: `pip install -e .`
3. Or add the src directory to PYTHONPATH: `export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"`

## Getting Help

- Open an issue on GitHub for bugs or feature requests
- Ask questions in pull request comments
- Check the [Development Setup Guide](SETUP.md) for detailed instructions

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
