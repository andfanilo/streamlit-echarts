# Streamlit - ECharts

A Streamlit component to display ECharts.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://echarts.streamlit.app/)

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

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup, testing, building, and publishing.
