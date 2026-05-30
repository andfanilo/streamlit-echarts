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

> Common workflows are wrapped in a [`justfile`](./justfile). Run `just` (or `just --list`) to see all recipes. Each section below shows both the `just` shortcut and the raw commands.

When developing locally, install in editable mode so Streamlit picks up **Python** code changes without rebuilding a wheel:

```sh
just setup     # uv sync + npm install + pre-commit install
```

<details><summary>Raw commands</summary>

```sh
uv sync
uv run pre-commit install  # install git hook (one-time)
```

</details>

For **frontend** (TypeScript/React) changes, you still need to rebuild. Use Vite's watch mode for automatic rebuilds on save:

```sh
just dev
```

<details><summary>Raw commands</summary>

```sh
cd streamlit_echarts/frontend
npm i --legacy-peer-deps
npm run dev
```

</details>

## Linting & Formatting

```sh
just lint          # ruff check (Python) + prettier check (frontend)
just format        # ruff format + prettier write
just pre-commit    # run all pre-commit hooks
```

<details><summary>Raw commands</summary>

```sh
uv run ruff check --fix .         # lint Python
uv run ruff format .              # format Python
cd streamlit_echarts/frontend && npx prettier --check "src/**/*.ts"   # lint frontend
cd streamlit_echarts/frontend && npx prettier --write "src/**/*.ts"   # format frontend
uv run pre-commit run --all-files # run all pre-commit hooks
```

</details>

> Per-language recipes are also available: `just lint-py`, `just lint-frontend`, `just format-py`, `just format-frontend`.

## Testing

### Unit Tests (TypeScript)

Fast, dependency-free tests for the JavaScript parsing logic:

```sh
just test-frontend             # single run
just test-frontend-watch       # watch mode
```

<details><summary>Raw commands</summary>

```sh
cd streamlit_echarts/frontend
npm test
npm run test:watch
```

</details>

### Unit Tests (Python)

```sh
just test-py
```

<details><summary>Raw command</summary>

```sh
uv run pytest tests/ -v
```

</details>

> `just test` runs both Python and frontend unit tests in sequence.

### E2E Tests (Playwright)

Snapshot tests that start a real Streamlit app and compare screenshots. Requires the package to be installed and the frontend to be built first.

```sh
just e2e-setup   # one-time: install deps + browsers
just e2e         # run the tests
```

<details><summary>Raw commands</summary>

```sh
uv sync --group e2e
uv run python -m playwright install --with-deps
uv run pytest e2e_playwright -n auto
```

</details>

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
just e2e-clean
```

<details><summary>Raw command</summary>

```sh
uv run python -m playwright uninstall --all
```

</details>

## Build and Publish

### Release flow

Releases live as annotated tags on `main`. The pyproject version is bumped on `develop` first so the tagged commit on `main` is self-consistent (tag `vX.Y.Z` ↔ `version = "X.Y.Z"`).

1. On `develop`, bump `version` in `pyproject.toml`, commit, push, and open a PR into `main`. Merge it.
2. Cut the tag from a clean working tree:

   ```sh
   just tag-release 0.7.0
   ```

   This fast-forwards `main` from `develop`, creates an annotated `v0.7.0` tag, and pushes both.

   <details><summary>Raw commands</summary>

   ```sh
   git checkout main && git pull --ff-only
   git merge --ff-only develop
   git tag -a v0.7.0 -m "Release 0.7.0"
   git push origin main
   git push origin v0.7.0
   ```

   </details>

3. Build, test install, and publish (see below).

> `just publish-test` and `just publish` are **guarded** — they refuse to run unless HEAD is on `main`, the tree is clean, and HEAD is tagged matching the pyproject version.

### Build and publish

1. Build the frontend assets and Python wheel:

   ```sh
   just build
   ```

   <details><summary>Raw commands</summary>

   ```sh
   # from streamlit_echarts/frontend
   npm i --legacy-peer-deps
   npm run build

   # from the project root
   uv build
   ```

   </details>

2. Test install the built wheel in another project (e.g. `streamlit-echarts-demo`):

   ```sh
   uv pip install ../streamlit-echarts/dist/streamlit_echarts-<version>-py3-none-any.whl --force-reinstall
   uv run streamlit run app.py
   ```

3. Publish to Test PyPI (dry-run):

   ```sh
   just publish-test
   ```

   <details><summary>Raw command</summary>

   ```sh
   uv publish --index testpypi
   ```

   </details>

   You will need a [Test PyPI API token](https://test.pypi.org/manage/account/#api-tokens). Pass it via `--token` or set `UV_PUBLISH_TOKEN`.

   Verify the package at `https://test.pypi.org/project/streamlit-echarts/` and test install it:

   ```sh
   uv pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ streamlit-echarts
   ```

4. Publish to PyPI:

   ```sh
   just publish
   ```

   <details><summary>Raw command</summary>

   ```sh
   uv publish
   ```

   </details>

   You will need a PyPI API token. You can pass it via `--token` or set the `UV_PUBLISH_TOKEN` environment variable.

### Expected output

- `dist/streamlit_echarts-<version>-py3-none-any.whl`
- `dist/streamlit_echarts-<version>.tar.gz`
