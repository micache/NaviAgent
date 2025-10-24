.PHONY: format lint typecheck precommit all

format:
	uv run black --line-length 100 .
	uv run isort --profile black --line-length 100 .

lint:
	uv run flake8 . --max-line-length=100

typecheck:
	uv run mypy --ignore-missing-imports .

precommit:
	uv run pre-commit run --all-files

all: format lint typecheck

check: lint typecheck precommit
