# Streamlit - ECharts

A Streamlit component to display ECharts.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/andfanilo/streamlit-echarts-demo/master/app.py)

![](./img/demo.gif)

---

## Requirements

- Python >= 3.10

## Installation instructions

```sh
uv pip install streamlit-echarts
```

To also use PyECharts charts with `st_pyecharts`:

```sh
uv pip install streamlit-echarts[pyecharts]
```

## Usage instructions

```python
import streamlit as st
from streamlit_echarts import st_echarts

options = {
    "xAxis": {
        "type": "category",
        "data": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
    },
    "yAxis": {"type": "value"},
    "series": [{"data": [820, 932, 901, 934, 1290, 1330, 1320], "type": "bar"}],
}

st_echarts(options=options, height="400px")
```

## API Reference

### `st_echarts(options, ...)`

| Parameter | Type | Default | Description |
|---|---|---|---|
| `options` | `dict` | **required** | ECharts [option object](https://echarts.apache.org/en/option.html) |
| `theme` | `str \| dict` | `""` | `"streamlit"`, `"dark"`, or a custom theme dict |
| `events` | `dict[str, str]` | `None` | Map of ECharts event names to JS handler strings; return value becomes the component return value |
| `height` | `str` | `"300px"` | Any valid CSS height (e.g. `"500px"`, `"50vh"`) |
| `width` | `str` | `"100%"` | Any valid CSS width (e.g. `"100%"`, `"600px"`) |
| `renderer` | `"canvas" \| "svg"` | `"canvas"` | ECharts renderer; `"svg"` is better for print/accessibility |
| `map` | `Map \| None` | `None` | GeoJSON map to register, created via `Map(map_name=..., geo_json=...)` |
| `key` | `str \| None` | `None` | Stable widget key; prevents remount and animation replay on rerun |
| `on_change` | `callable \| None` | `None` | Python callback invoked when the component fires a chart event |
| `on_select` | `"ignore" \| "rerun" \| callable` | `"ignore"` | Selection behavior: `"rerun"` triggers a Streamlit rerun; a callable is invoked on selection change |
| `selection_mode` | `str \| tuple[str]` | `("points","box","lasso")` | Which interactions to enable: `"points"` (click), `"box"` (rect brush), `"lasso"` (polygon brush) |

### `st_pyecharts(chart, ...)`

Convenience wrapper that converts a PyECharts chart instance to a dict and calls `st_echarts`. Requires `pip install streamlit-echarts[pyecharts]`. Accepts the same parameters as `st_echarts` (replacing `options` with `chart`).

### `JsCode(js_string)`

Wraps a JavaScript string so the frontend evaluates it as a live function rather than a plain string. Use wherever ECharts expects a callback (formatters, symbol sizes, color functions, …).

```python
JsCode("function(params){ return params.value * 2 }")
```

### `Map(map_name, geo_json, special_areas=None)`

Registers a GeoJSON map with ECharts. Pass the returned object to `st_echarts(map=...)` and reference `map_name` in a `geo` or `map` series.

---

### Selection / Interactions

Use `on_select` to enable structured selection events, similar to `st.plotly_chart`:

```python
result = st_echarts(options=options, on_select="rerun", selection_mode="points", key="my_chart")

selected = result["selection"]
if selected["point_indices"]:
    st.write("Selected indices:", selected["point_indices"])
```

`selection_mode` accepts `"points"` (click), `"box"` (rect brush), `"lasso"` (polygon brush), or a tuple of multiple modes. See the demo app for more examples.

### Using with PyECharts

Install the optional `pyecharts` extra:

```sh
uv pip install streamlit-echarts[pyecharts]
```

Then use `st_pyecharts` to render PyECharts chart instances directly:

```python
import streamlit as st
from pyecharts import options as opts
from pyecharts.charts import Bar
from streamlit_echarts import st_pyecharts

b = (
    Bar()
    .add_xaxis(["Microsoft", "Amazon", "IBM", "Oracle", "Google", "Alibaba"])
    .add_yaxis(
        "2017-2018 Revenue in (billion $)", [21.2, 20.4, 10.3, 6.08, 4, 2.2]
    )
    .set_global_opts(
        title_opts=opts.TitleOpts(
            title="Top cloud providers 2018", subtitle="2017-2018 Revenue"
        )
    )
)

st_pyecharts(b, height="500px")
```

`st_pyecharts` accepts the same parameters as `st_echarts` (theme, events, on_select, etc.). Under the hood it calls `chart.dump_options()` and passes the result to `st_echarts`.

Alternatively, you can convert PyECharts options manually without installing the extra:

```python
import json
from streamlit_echarts import st_echarts

st_echarts(options=json.loads(b.dump_options()), height="500px")
```

## Demo Application

A comprehensive demo application containing dozens of ECharts and PyECharts examples is available in the root of the repository. You can use it as an integration test to verify the component's functionality:

Note: You will need extra dependencies installed to run all examples in the demo:

```sh
uv pip install pyecharts pandas faker
uv run streamlit run demo_app.py
```

---

## Project status

This project is in vibecoder best-effort. I consider it [unmaintained](https://www.youtube.com/watch?v=1RFJF_ETpLk) but I may here and then vibecode additional features.

Please add a thumbs up [HERE](https://github.com/streamlit/streamlit/issues/1564) if you wish to see a native implementation.

---

## Development setup

**Prerequisites:** Node.js >= 24 (LTS)

When developing locally, install in editable mode so Streamlit picks up **Python** code changes without rebuilding a wheel:

```sh
uv pip install -e . --force-reinstall
```

For **frontend** (TypeScript/React) changes, you still need to rebuild. Use Vite's watch mode for automatic rebuilds on save:

```sh
cd streamlit_echarts/frontend
npm i --legacy-peer-deps
npm run dev
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

### E2E Tests (Playwright)

Snapshot tests that start a real Streamlit app and compare screenshots. Requires the package to be installed and the frontend to be built first.

```sh
# Install test dependencies
uv pip install -r e2e_playwright/test-requirements.txt
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
   uv pip install ../streamlit-echarts/dist/streamlit_echarts-0.6.0-py3-none-any.whl --force-reinstall
   uv run streamlit run app.py
   ```

4. Publish to PyPI:

   ```sh
   uv publish
   ```

   You will need a PyPI API token. You can pass it via `--token` or set the `UV_PUBLISH_TOKEN` environment variable.

   To bump the version, edit `version` in `pyproject.toml` before building.

### Expected output

- `dist/streamlit_echarts-0.6.0-py3-none-any.whl`
- `dist/streamlit_echarts-0.6.0.tar.gz`
