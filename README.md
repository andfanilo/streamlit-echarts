# streamlit-echarts

A Streamlit component to display ECharts.

## Installation instructions

```sh
uv venv
uv pip install streamlit-echarts
```

### Development install (editable)

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

### Using with PyECharts

The v2 version of `streamlit-echarts` intentionally drops the `pyecharts` and `simplejson` dependencies to keep the package lightweight. You can still easily render PyECharts figures by dumping their configuration to JSON and passing it as a dictionary:

```python
import json
import streamlit as st
from pyecharts import options as opts
from pyecharts.charts import Bar
from streamlit_echarts import st_echarts

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

# Render by converting the PyECharts instance to a JSON dictionary
st_echarts(options=json.loads(b.dump_options()), height="500px")
```

## Demo Application

A comprehensive demo application containing dozens of ECharts and PyECharts examples is available in the root of the repository. You can use it as an integration test to verify the component's functionality:

Note: You will need extra dependencies installed to run all examples in the demo:

```sh
uv pip install pyecharts pandas faker
uv run streamlit run demo_app.py
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
   uv pip install ../streamlit-echarts/dist/streamlit_echarts-0.5.0-py3-none-any.whl --force-reinstall
   uv run streamlit run app.py
   ```

4. Publish to PyPI:

   ```sh
   uv publish
   ```

   You will need a PyPI API token. You can pass it via `--token` or set the `UV_PUBLISH_TOKEN` environment variable.

   To bump the version, edit `version` in `pyproject.toml` before building.

### Requirements

- Python >= 3.10
- Node.js >= 24 (LTS)

### Expected output

- `dist/streamlit_echarts-0.5.0-py3-none-any.whl`
- `dist/streamlit_echarts-0.5.0.tar.gz`
