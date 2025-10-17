# NaviAgent

A navigation agent framework with comprehensive code quality tools and CI/CD.

## Features

- 🎨 **Code Style**: Automated formatting with Black and isort
- 🔍 **Linting**: Comprehensive checking with Flake8 and plugins
- ✅ **Testing**: Unit tests with pytest and coverage reporting
- 🔐 **Security**: Security scanning with Bandit
- 📝 **Documentation**: Google-style docstring enforcement
- 🔄 **CI/CD**: Automated checks with GitHub Actions
- 🪝 **Pre-commit Hooks**: Automated checks before every commit

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/micache/NaviAgent.git
cd NaviAgent

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements-dev.txt

# Set up pre-commit hooks
pre-commit install
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=term-missing
```

### Code Style

```bash
# Format code
black --line-length 100 .
isort --profile black --line-length 100 .

# Check code style
flake8 . --max-line-length=100
mypy --ignore-missing-imports .

# Run all pre-commit hooks
pre-commit run --all-files
```

## Documentation

- [Development Setup Guide](SETUP.md) - Detailed setup and usage instructions
- [Contributing Guidelines](CONTRIBUTING.md) - How to contribute to the project

## Code Quality Standards

This project adheres to:

- **Google Python Style Guide**
- **PEP 8** coding conventions
- **Type hints** for all functions
- **Google-style docstrings** for documentation
- **100% test coverage** goal

## CI/CD Pipeline

The project uses GitHub Actions for continuous integration:

- ✅ Code style checks (Black, isort, Flake8)
- ✅ Unit tests with coverage (Python 3.8-3.12)
- ✅ Type checking (mypy)
- ✅ Security scanning (Bandit)
- ✅ Documentation checks (pydocstyle)

## License

MIT License - See [LICENSE](LICENSE) file for details

## Contributing

Contributions are welcome! Please read our [Contributing Guidelines](CONTRIBUTING.md) first.