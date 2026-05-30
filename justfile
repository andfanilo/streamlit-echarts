# streamlit-echarts — task runner
# Usage: `just <recipe>`  |  list recipes: `just --list`

set windows-shell := ["pwsh.exe", "-NoLogo", "-Command"]

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

# Vite watch-rebuild on save (no dev server) — run alongside `just demo` to iterate on frontend
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

# Build frontend assets + Python wheel into dist/ (assumes deps are installed)
build: build-frontend build-wheel

build-frontend:
    cd {{frontend}} && npm run build

build-wheel:
    uv build

# Full from-scratch wheel: wipe deps + artifacts, reinstall (reconciles package.json + dedupes), rebuild
build-clean: clean setup-frontend build

# Remove build outputs + installed frontend deps (Windows/pwsh)
clean:
    -Remove-Item -Recurse -Force dist, build, *.egg-info -ErrorAction Ignore
    -Remove-Item -Recurse -Force {{frontend}}/node_modules, {{frontend}}/build -ErrorAction Ignore

# Publish to Test PyPI (set UV_PUBLISH_TOKEN or pass --token)
publish-test: _verify-release-state build
    uv publish --index testpypi

# Publish to PyPI (set UV_PUBLISH_TOKEN or pass --token)
publish: _verify-release-state build
    uv publish

# --- Release ---

# Cut a release: ff-merge develop into main, annotated tag vX.Y.Z, push both
tag-release version:
    @if (git status --porcelain) { Write-Host -ForegroundColor Red "Working tree not clean. Commit or stash first."; exit 1 }
    @if (git tag --list "v{{version}}") { Write-Host -ForegroundColor Red "Tag v{{version}} already exists"; exit 1 }
    git fetch origin
    git checkout main
    git pull --ff-only origin main
    git merge --ff-only develop
    @$pyver = (Select-String -Path pyproject.toml -Pattern '^version = "(.+)"$').Matches.Groups[1].Value; \
    if ($pyver -ne "{{version}}") { \
        Write-Host -ForegroundColor Red "pyproject.toml version ($pyver) does not match {{version}}. Bump it on develop first."; \
        exit 1 \
    }
    git tag -a "v{{version}}" -m "Release {{version}}"
    git push origin main
    git push origin "v{{version}}"

# Guard for publish: must be on main, clean tree, HEAD tagged matching pyproject version
_verify-release-state:
    @if ((git rev-parse --abbrev-ref HEAD) -ne "main") { Write-Host -ForegroundColor Red "Must be on main branch to publish"; exit 1 }
    @if (git status --porcelain) { Write-Host -ForegroundColor Red "Working tree not clean"; exit 1 }
    @$pyver = (Select-String -Path pyproject.toml -Pattern '^version = "(.+)"$').Matches.Groups[1].Value; \
    $tags = @(git tag --points-at HEAD); \
    if ("v$pyver" -notin $tags) { \
        Write-Host -ForegroundColor Red "HEAD is not tagged v$pyver. Run just tag-release first."; \
        exit 1 \
    }

# --- Dependency maintenance ---

# Squash-merge every open Dependabot PR that is mergeable and green (skips conflicting/pending/failing), delete its branch, then sync develop. Requires `gh`.
merge-dependabot:
    @$prs = gh pr list --author "app/dependabot" --state open \
        --json number,title,mergeable,statusCheckRollup | ConvertFrom-Json; \
    if (-not $prs) { Write-Host -ForegroundColor Green "No open Dependabot PRs."; exit 0 }; \
    foreach ($pr in $prs) { \
        $green = @($pr.statusCheckRollup | Where-Object { $_.status -ne 'COMPLETED' -or $_.conclusion -notin @('SUCCESS','NEUTRAL','SKIPPED') }).Count -eq 0; \
        if ($pr.mergeable -ne 'MERGEABLE') { Write-Host -ForegroundColor Yellow "skip #$($pr.number) [$($pr.mergeable)] - $($pr.title)"; continue }; \
        if (-not $green)                  { Write-Host -ForegroundColor Yellow "skip #$($pr.number) [checks not green] - $($pr.title)"; continue }; \
        Write-Host -ForegroundColor Cyan "merging #$($pr.number) - $($pr.title)"; \
        gh pr merge $pr.number --squash --delete-branch; \
    }
    git checkout develop
    git pull --rebase --autostash
