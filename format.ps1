Write-Host "Formatting code..." -ForegroundColor Green
uv run black --line-length 100 .
uv run isort --profile black --line-length 100 .

Write-Host "Checking code style..." -ForegroundColor Yellow
uv run flake8 . --max-line-length=100
uv run mypy --ignore-missing-imports .

Write-Host "Running pre-commit hooks..." -ForegroundColor Cyan
uv run pre-commit run --all-files

Write-Host "Done!" -ForegroundColor Green
