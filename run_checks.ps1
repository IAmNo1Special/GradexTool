Write-Host "==========================================" -ForegroundColor Gray
Write-Host "Running All Project Quality & Test Checks" -ForegroundColor Yellow
Write-Host "==========================================" -ForegroundColor Gray

Write-Host "`n1. Running Ruff Lint Checks..." -ForegroundColor Cyan
uv run --dev ruff check .
if ($LASTEXITCODE -ne 0) { Write-Host "❌ Ruff check failed!" -ForegroundColor Red; exit $LASTEXITCODE }
Write-Host "✅ Ruff check passed." -ForegroundColor Green

Write-Host "`n2. Running Ruff Format Check..." -ForegroundColor Cyan
uv run --dev ruff format --check .
if ($LASTEXITCODE -ne 0) { Write-Host "❌ Ruff format check failed!" -ForegroundColor Red; exit $LASTEXITCODE }
Write-Host "✅ Ruff format check passed." -ForegroundColor Green

Write-Host "`n3. Running Mypy Type Check..." -ForegroundColor Cyan
uv run --dev mypy .
if ($LASTEXITCODE -ne 0) { Write-Host "❌ Mypy check failed!" -ForegroundColor Red; exit $LASTEXITCODE }
Write-Host "✅ Mypy check passed." -ForegroundColor Green

Write-Host "`n4. Checking Markdown Formatting..." -ForegroundColor Cyan
uv run --python 3.13 --dev mdformat --check .
if ($LASTEXITCODE -ne 0) { Write-Host "❌ Markdown formatting check failed!" -ForegroundColor Red; exit $LASTEXITCODE }
Write-Host "✅ Markdown formatting check passed." -ForegroundColor Green

Write-Host "`n5. Running Pytest Suite..." -ForegroundColor Cyan
uv run --dev pytest tests/ --cov=. -v
if ($LASTEXITCODE -ne 0) { Write-Host "❌ Pytest failed!" -ForegroundColor Red; exit $LASTEXITCODE }
Write-Host "✅ Pytest passed." -ForegroundColor Green

Write-Host "`n==========================================" -ForegroundColor Gray
Write-Host "🎉 All checks passed successfully!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Gray
