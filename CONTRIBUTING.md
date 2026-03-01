# Contributing to streamlit-echarts

## AI-Assisted Development

This project includes configuration for AI coding agents in `.claude/` and `.gemini/`. Claude Code is the primary coding agent (implementation, reviews, CI fixes). Gemini acts as an adversarial architect and reviewer — a second pair of eyes to challenge assumptions and catch issues before committing.

### Claude Code

| Command | Description |
|---|---|
| `/reviewing-current-branch` | Review the current branch's changes (vs base) for code quality, security, and best practices |
| `/simplifying-current-branch` | Simplify and refine the current branch's changes (vs base) for clarity and maintainability |
| `/fixing-pr` | Fix CI failures and address PR review comments for the current branch |
| `/criticizing-local-changes` | Critically review uncommitted changes (`git diff`) for bugs, style issues, and improvements |

| Skill | Description |
|---|---|
| `developing-with-streamlit` | Router skill for Streamlit development — routes to sub-skills covering CCv2 components, layouts, theming, performance, data display, and more |

### Gemini Code Assist

| Command | Description |
|---|---|
| `/criticizing-local-changes` | Critically review uncommitted changes (`git diff`) for bugs, style issues, and improvements |

## Development setup

**Prerequisites:** Node.js >= 24 (LTS)

When developing locally, install in editable mode so Streamlit picks up **Python** code changes without rebuilding a wheel:

```sh
uv sync
uv run pre-commit install  # install git hook (one-time)
```

For **frontend** (TypeScript/React) changes, you still need to rebuild. Use Vite's watch mode for automatic rebuilds on save:

```sh
cd streamlit_echarts/frontend
npm i --legacy-peer-deps
npm run dev
```

## Linting & Formatting

```sh
uv run ruff check --fix .         # lint
uv run ruff format .              # format
uv run pre-commit run --all-files # run all pre-commit hooks
```

## Testing

### Unit Tests (TypeScript)

Fast, dependency-free tests for the JavaScript parsing logic:

```sh
cd streamlit_echarts/frontend
npm test
```

Run in watch mode during development:

```sh
npm run test:watch
```

### Unit Tests (Python)

```sh
uv run pytest tests/ -v
```

### E2E Tests (Playwright)

Snapshot tests that start a real Streamlit app and compare screenshots. Requires the package to be installed and the frontend to be built first.

```sh
# Install test dependencies
uv sync --group e2e
uv run python -m playwright install --with-deps

# Run the tests
uv run pytest e2e_playwright -n auto
```

> On first run, missing snapshots are created automatically. Commit them as the new baseline. Re-run to verify.

To **update existing snapshots** (e.g. after intentional UI changes), delete the relevant files from `e2e_playwright/__snapshots__/` and re-run the tests — they will be regenerated automatically. Updated snapshots also appear in `e2e_playwright/test-results/snapshot-updates/` after each run for easy review.

#### Managing CI snapshot baselines

Snapshots are stored per-platform under `e2e_playwright/__snapshots__/{platform}/` (e.g. `win32`, `linux`). Local snapshots generated on Windows **won't match** the Linux CI runner, so you need to bootstrap Linux baselines separately:

1. Push your branch and let the Playwright CI workflow run — it will **fail** with `"Missing snapshot"` (this is expected)
2. Download the `playwright-results-*` artifact from the GitHub Actions run page
3. Inside it, find the generated snapshots under `snapshot-updates/linux/basic_chart/`
4. Copy them to `e2e_playwright/__snapshots__/linux/basic_chart/` in your repo
5. Commit and push — the next CI run will compare against these baselines and pass

> Repeat this process whenever you intentionally change the chart's appearance: delete the old Linux baselines, let CI regenerate them, download and commit.

To **clean up Playwright's browser binaries** (freeing up ~500MB+ in `%USERPROFILE%\AppData\Local\ms-playwright`), run:

```sh
uv run python -m playwright uninstall --all
```

## Build and Publish

To package this component for distribution:

1. Build the frontend assets (from `streamlit_echarts/frontend`):

   ```sh
   npm i --legacy-peer-deps
   npm run build
   ```

2. Build the Python package (from the project root):

   ```sh
   uv build
   ```

3. Test install the built wheel in another project (e.g. `streamlit-echarts-demo`):

   ```sh
   uv pip install ../streamlit-echarts/dist/streamlit_echarts-<version>-py3-none-any.whl --force-reinstall
   uv run streamlit run app.py
   ```

4. Publish to Test PyPI (dry-run):

   ```sh
   uv publish --index testpypi
   ```

   You will need a [Test PyPI API token](https://test.pypi.org/manage/account/#api-tokens). Pass it via `--token` or set `UV_PUBLISH_TOKEN`.

   Verify the package at `https://test.pypi.org/project/streamlit-echarts/` and test install it:

   ```sh
   uv pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ streamlit-echarts
   ```

5. Publish to PyPI:

   ```sh
   uv publish
   ```

   You will need a PyPI API token. You can pass it via `--token` or set the `UV_PUBLISH_TOKEN` environment variable.

   To bump the version, edit `version` in `pyproject.toml` before building.

### Expected output

- `dist/streamlit_echarts-<version>-py3-none-any.whl`
- `dist/streamlit_echarts-<version>.tar.gz`
