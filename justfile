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

# --- Build & publish ---

# Build frontend assets + Python wheel into dist/
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
