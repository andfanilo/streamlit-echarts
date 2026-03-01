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

All commands assume working directory is `streamlit-echarts/`.

```sh
# --- Setup ---
uv sync                    # installs project + dev group
cd streamlit_echarts/frontend && npm i --legacy-peer-deps

# --- Frontend build ---
cd streamlit_echarts/frontend
npm run build              # clean + typecheck + production build
npm run dev                # watch mode (auto-rebuild on save)

# --- Frontend validation ---
cd streamlit_echarts/frontend
npm test                   # vitest single run (49 tests)
npm run test:watch         # vitest watch mode
npx tsc --noEmit           # typecheck only
npx prettier --check "src/**/*.{ts,tsx}"  # format check

# --- Python validation ---
uv run pytest tests/ -v    # unit tests (15 tests)
uv run ruff check --fix .  # lint
uv run ruff format .       # format

# --- Pre-commit ---
uv run pre-commit run --all-files  # run all hooks
uv run pre-commit install          # install git hook (one-time)

# --- E2E tests ---
uv sync --group e2e
uv run python -m playwright install --with-deps
uv run pytest e2e_playwright -n auto

# --- Full validation (CI-equivalent) ---
cd streamlit_echarts/frontend && npm test && npm run build && cd ../.. && uv run pytest tests/ -v

# --- Build wheel ---
cd streamlit_echarts/frontend && npm run build   # frontend first
cd ../.. && uv build                              # then Python wheel

# --- Run demo ---
uv run streamlit run demo_app.py
```
