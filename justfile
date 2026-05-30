# streamlit-echarts — task runner
# Usage: `just <recipe>`  |  list recipes: `just --list`

set windows-shell := ["powershell.exe", "-NoLogo", "-Command"]

frontend := "streamlit_echarts/frontend"

# Default: show available recipes
default:
    @just --list

# --- Development setup ---

# Full local dev setup (Python + frontend + git hook)
setup: setup-py setup-frontend
    uv run pre-commit install

# Install Python deps in editable mode
setup-py:
    uv sync

# Install frontend deps
setup-frontend:
    cd {{frontend}} && npm i --legacy-peer-deps

# Vite watch mode — auto-rebuild frontend on save
dev:
    cd {{frontend}} && npm run dev

# Run the demo app
demo:
    uv run streamlit run demo_app.py

# --- Lint & format ---

# Lint everything (Python + frontend)
lint: lint-py lint-frontend

lint-py:
    uv run ruff check --fix .

lint-frontend:
    cd {{frontend}} && npx prettier --check "src/**/*.ts"

# Format everything (Python + frontend)
format: format-py format-frontend

format-py:
    uv run ruff format .

format-frontend:
    cd {{frontend}} && npx prettier --write "src/**/*.ts"

# Run all pre-commit hooks
pre-commit:
    uv run pre-commit run --all-files

# --- Testing ---

# Run all unit tests (Python + frontend)
test: test-py test-frontend

# Python unit tests
test-py:
    uv run pytest tests/ -v

# Frontend unit tests (Vitest)
test-frontend:
    cd {{frontend}} && npm test

# Frontend unit tests in watch mode
test-frontend-watch:
    cd {{frontend}} && npm run test:watch

# --- E2E (Playwright) ---

# Install Playwright deps + browsers (one-time)
e2e-setup:
    uv sync --group e2e
    uv run python -m playwright install --with-deps

# Run E2E tests
e2e:
    uv run pytest e2e_playwright -n auto

# Free ~500MB by uninstalling Playwright browser binaries
e2e-clean:
    uv run python -m playwright uninstall --all

# --- Build & publish ---

# Build frontend assets + Python wheel into dist/ (assumes `just setup` has run)
build: build-frontend build-wheel

build-frontend:
    cd {{frontend}} && npm run build

build-wheel:
    uv build

# Publish to Test PyPI (set UV_PUBLISH_TOKEN or pass --token)
publish-test: build
    uv publish --index testpypi

# Publish to PyPI (set UV_PUBLISH_TOKEN or pass --token)
publish: build
    uv publish
