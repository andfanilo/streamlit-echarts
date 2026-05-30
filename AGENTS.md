# AGENTS.md — streamlit-echarts

## Platform & Requirements

- **Python** >= 3.10, **Node.js** >= 24, **npm** with `--legacy-peer-deps`
- `streamlit >= 1.53`, `echarts ^6.0.0`, `@streamlit/component-v2-lib ^0.2.0`
- Extensions: `echarts-gl`, `echarts-liquidfill`, `echarts-wordcloud`
- Build: Vite 7 (library mode, ES modules), TypeScript 5.8
- Test: Vitest 4 (jsdom), pytest, Playwright (E2E)
- Lint: Ruff (Python), Prettier (TypeScript)

## Component

### Python — `streamlit_echarts/__init__.py`

Module-level `st.components.v2.component()` registration with JS glob `"index-*.js"`. Exposes `st_echarts()` which serializes options (replacing `JsCode` instances with `--x_x--0_0--` placeholders), validates `on_select`/`selection_mode` params, and returns component state. Also exports `JsCode` (JS string wrapper) and `Map` (GeoJSON registration).

### Frontend renderer — `frontend/src/index.ts`

`EchartsRenderer` receives `{ data, parentElement, setStateValue, setTriggerValue }`. Uses a `WeakMap<parentElement, ComponentState>` for multi-instance safety. Each instance holds the chart plus four memoized generators:

1. **`getOptionsGenerator`** — deep-maps options through `evalStringToFunction`; skips if JSON unchanged
2. **`setThemeGenerator`** — reads `--st-*` CSS vars, registers ECharts theme; disposes chart on theme change
3. **`setEventsGenerator`** — unbinds/rebinds `chart.on()` handlers when `events` dict changes
4. **`setSelectionGenerator`** — wires click/brushselected listeners per `selectionMode`

Lifecycle: size container → register map → resolve theme → init chart → apply options (`notMerge:true`) → wire events → wire selection + brush toolbox (`notMerge:false`) → setup ResizeObserver + IntersectionObserver → return cleanup.

### Selection API — `frontend/src/selection.ts`

Unified `SelectionData` type: `{ points, point_indices, box, lasso }`.

- **`transformClickToSelection`** — maps ECharts click to single-point selection; returns `EMPTY_SELECTION` on background click (`dataIndex == null`)
- **`transformBrushToSelection`** — reads `batch[].areas` for coordinates, `batch[].selected` for indices, looks up `chart.getOption().series[i].data[idx]` for value/name
- **`buildBrushOption`** — returns ECharts brush + toolbox config for active modes (or empty arrays to clear)

### JS code injection — `frontend/src/parsers.ts`

`evalStringToFunction` detects `--x_x--0_0--` markers and evaluates via `new Function()`. Supports arrow functions and classic syntax.

### Utilities — `frontend/src/utils.ts`

`deepMap(obj, iterator, context)` — recursively applies a function to all leaf values in nested objects/arrays.

## Build & Validation Commands

All commands assume working directory is `streamlit-echarts/`. Workflows are wrapped in a [`justfile`](./justfile) — run `just` (or `just --list`) to see every recipe.

### Common pipelines

```sh
# --- First-time setup + run the demo ---
just setup        # uv sync + npm install + pre-commit hook
just demo         # streamlit run demo_app.py

# --- Inner loop: frontend changes ---
just dev          # Vite watch mode (auto-rebuild on save)
just test         # Python + frontend unit tests
just lint         # ruff check + prettier check

# --- Pre-push validation (CI-equivalent) ---
just lint && just test && just build

# --- Full E2E flow (one-time setup, then run) ---
just e2e-setup    # uv sync --group e2e + playwright install --with-deps
just build        # E2E needs built frontend
just e2e          # uv run pytest e2e_playwright -n auto

# --- Build ---
just build              # frontend assets + Python wheel into dist/

# --- Release (cut a new version) ---
# 1. On develop: bump `version` in pyproject.toml, commit, PR → main, merge.
# 2. From main:
just tag-release 0.7.0  # ff-merge develop → main, annotated tag v0.7.0, push
just publish-test       # guarded build + uv publish --index testpypi
just publish            # guarded build + uv publish (PyPI)
```

Publish recipes are guarded: they refuse to run unless HEAD is on `main`, the tree is clean, and HEAD is tagged matching `pyproject.toml`'s version.

### Recipe reference

| Recipe | What it does |
|---|---|
| `setup` / `setup-py` / `setup-frontend` | Install deps (full / Python only / frontend only) |
| `dev` | Vite watch mode for frontend |
| `demo` | `uv run streamlit run demo_app.py` |
| `lint` / `lint-py` / `lint-frontend` | ruff check + prettier check (combined / split) |
| `format` / `format-py` / `format-frontend` | ruff format + prettier write |
| `pre-commit` | `uv run pre-commit run --all-files` |
| `test` / `test-py` / `test-frontend` | Unit tests (Python + Vitest) |
| `test-frontend-watch` | Vitest watch mode |
| `e2e-setup` / `e2e` / `e2e-clean` | Playwright deps install / run tests / uninstall browsers |
| `build` / `build-frontend` / `build-wheel` | Build frontend bundle + Python wheel |
| `tag-release X.Y.Z` | Ff-merge develop → main, annotated tag `vX.Y.Z`, push both |
| `publish-test` / `publish` | Guarded build + publish to Test PyPI / PyPI |
| `merge-dependabot` | Squash-merge every green, conflict-free Dependabot PR + delete branch, then sync develop (needs `gh`) |

### Raw commands (when bypassing `just`)

```sh
# Typecheck only (no recipe — use directly)
cd streamlit_echarts/frontend && npx tsc --noEmit

# Re-install the pre-commit hook (one-time, part of `just setup`)
uv run pre-commit install
```
