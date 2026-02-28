import inspect
import json
from urllib.request import urlopen

import streamlit as st

from streamlit_echarts import JsCode, Map, st_echarts, st_pyecharts

# Base bar chart options reused across pages
OPTIONS = {
    "xAxis": {"type": "category", "data": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]},
    "yAxis": {"type": "value"},
    "series": [{"data": [120, 200, 150, 80, 70, 110, 130], "type": "bar"}],
}


def _show_source(func):
    """Show the source code of a page function in an expander at the bottom."""
    with st.expander("Source code"):
        st.code(inspect.getsource(func), language="python")


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------

def page_options():
    st.header("1. `options`")
    st.markdown(
        "`options` is the only required argument. "
        "It accepts a plain Python `dict` that maps 1-to-1 to the ECharts option object."
    )
    options = {
        "xAxis": {"type": "category", "data": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]},
        "yAxis": {"type": "value"},
        "series": [{"data": [120, 200, 150, 80, 70, 110, 130], "type": "bar"}],
    }
    st_echarts(options=options, key="options_demo")
    _show_source(page_options)


def page_height_width():
    st.header("2. `height` and `width`")
    st.markdown(
        "Both accept any valid CSS size string. "
        '`height` defaults to `"300px"`; `width` defaults to `"100%"`.'
    )

    col1, col2 = st.columns(2)
    with col1:
        st.caption('height="250px"')
        st_echarts(options=OPTIONS, height="250px", key="height_small")
    with col2:
        st.caption('height="500px"')
        st_echarts(options=OPTIONS, height="500px", key="height_large")

    st.caption('width="40%"')
    st_echarts(options=OPTIONS, width="40%", key="width_half")

    st.subheader("Chart inside containers with different `width` settings")
    st.markdown(
        "The chart's `width` interacts with its parent container's `width` setting. "
        "The bordered box shows the container boundary — notice how `\"content\"` "
        "shrinks to the chart, while `\"stretch\"` always fills the available space."
    )
    col_a, col_b = st.columns(2)
    with col_a:
        st.caption('`st.container(width="content")` — shrinks to fit the chart')
        with st.container(border=True, width="content"):
            st_echarts(options=OPTIONS, width="200px", key="container_content")
    with col_b:
        st.caption('`st.container(width="stretch")` — fills the column')
        with st.container(border=True, width="stretch"):
            st_echarts(options=OPTIONS, key="container_stretch")

    _show_source(page_height_width)


def page_renderer():
    st.header("3. `renderer`")
    st.markdown(
        '`"canvas"` (default) is faster for many data points. '
        '`"svg"` produces a scalable graphic that prints crisply and is accessible to screen readers.'
    )
    renderer = st.radio("renderer", ["canvas", "svg"], horizontal=True, key="renderer_radio")
    st_echarts(options=OPTIONS, renderer=renderer, key="renderer_demo")
    _show_source(page_renderer)


def page_theme():
    st.header("4. `theme`")
    st.markdown(
        "The `theme` parameter controls how the chart is styled. "
        "It accepts a **string** or a **dict**:"
    )
    st.markdown(
        """
| Value | Behavior |
|---|---|
| `"streamlit"` (default) | Reads Streamlit's CSS variables (`--st-text-color`, `--st-background-color`, etc.), so the chart **automatically adapts to light/dark mode** and any custom Streamlit theme set in `.streamlit/config.toml`. |
| `"dark"` / `"light"` | Uses ECharts' built-in dark or light theme. No Streamlit CSS variables are read. |
| `""` (empty string) | No theme — plain ECharts default (always light). |
| `{...}` (dict) | Registered as a custom ECharts theme object via `echarts.registerTheme()`. Full control over colors, text styles, etc. |
"""
    )

    BUILTIN_THEMES = ["streamlit", "dark", "light", ""]

    tab_string, tab_dict = st.tabs(["String themes", "Custom dict theme"])

    with tab_string:
        theme_name = st.selectbox(
            "Theme",
            BUILTIN_THEMES,
            format_func=lambda t: t if t else '""  (empty string — no theme)',
            key="theme_selectbox",
        )
        st_echarts(options=OPTIONS, theme=theme_name, key=f"theme_{theme_name}")

    with tab_dict:
        st.markdown(
            "Pass a Python dict to define a fully custom ECharts theme. "
            "See the [ECharts theme builder](https://echarts.apache.org/en/theme-builder.html) for all available keys."
        )
        CUSTOM_THEME = {
            "color": ["#e06c75", "#98c379", "#61afef"],
            "backgroundColor": "#282c34",
            "textStyle": {"color": "#abb2bf"},
        }
        st_echarts(options=OPTIONS, theme=CUSTOM_THEME, key="theme_dict_demo")

    _show_source(page_theme)


def page_interactions():
    st.header("5. Interactions")
    st.markdown(
        "`on_select` is the recommended way to handle chart interactions — "
        "it returns structured selection data without writing JavaScript, similar to Plotly's selection API. "
        "For advanced use cases (e.g. `mouseover`, custom return values), use the lower-level `events` dict."
    )

    SALES_DATA = [
        {"day": "Mon", "sales": 120},
        {"day": "Tue", "sales": 200},
        {"day": "Wed", "sales": 150},
        {"day": "Thu", "sales": 80},
        {"day": "Fri", "sales": 70},
        {"day": "Sat", "sales": 110},
        {"day": "Sun", "sales": 130},
    ]

    # --- on_select: click ---
    st.subheader("`on_select` — click selection")
    st.markdown(
        'Set `on_select="rerun"` and `selection_mode="points"` to get structured click data. '
        "Use `point_indices` to filter back to your source data."
    )
    select_result = st_echarts(
        options=OPTIONS,
        key="select_points",
        on_select="rerun",
        selection_mode="points",
    )
    indices = select_result["selection"]["point_indices"]
    if indices:
        st.table([SALES_DATA[i] for i in indices if i < len(SALES_DATA)])
    else:
        st.caption("Click a bar to filter the source data.")

    # --- on_select: brush ---
    st.subheader("`on_select` — brush selection (box + lasso)")
    st.markdown(
        'Pass `selection_mode=("box", "lasso")` to enable brush tools in the toolbar. '
        "The selection includes points, indices, and coordinate ranges."
    )
    scatter_options = {
        "xAxis": {"type": "value"},
        "yAxis": {"type": "value"},
        "series": [
            {
                "type": "scatter",
                "data": [
                    [3.0, 4.5], [7.0, 2.0], [1.5, 6.0], [5.5, 5.5],
                    [9.0, 1.0], [4.0, 8.0], [6.5, 3.5], [2.0, 7.0],
                ],
            }
        ],
    }
    brush_result = st_echarts(
        options=scatter_options,
        key="select_brush",
        on_select="rerun",
        selection_mode=("box", "lasso"),
    )
    sel = brush_result["selection"]
    if sel["point_indices"]:
        st.json(sel)
    else:
        st.caption("Use the brush tool in the toolbar to select points.")

    # --- events: lower-level alternative ---
    st.divider()
    st.subheader("`events` — lower-level alternative")
    st.markdown(
        "`events` maps ECharts event names to JavaScript handler strings. "
        "The handler's **return value** becomes the component's return value in Python. "
        "Use this for events that `on_select` doesn't cover, like `mouseover`."
    )

    st.caption("click event")
    click_result = st_echarts(
        options=OPTIONS,
        events={"click": "function(p){return {name: p.name, value: p.value}}"},
        key="events_click",
    )
    if click_result:
        st.write("Last click:", click_result)
    else:
        st.info("Click a bar to fire a click event.")

    st.caption("mouseover event")
    mouseover_result = st_echarts(
        options=OPTIONS,
        events={"mouseover": "function(p){return {name: p.name, value: p.value}}"},
        key="events_mouseover",
    )
    if mouseover_result:
        st.write("Last mouseover:", mouseover_result)
    else:
        st.info("Hover over a bar to fire a mouseover event.")

    _show_source(page_interactions)


def page_key():
    st.header("6. `key`")
    st.markdown(
        "Without `key`, Streamlit may remount the component on each rerun (e.g. after a widget interaction), "
        "replaying the entry animation and losing any internal ECharts state. "
        "A stable `key` tells Streamlit to reuse the same component instance across reruns."
    )

    DATA_A = [120, 200, 150, 80, 70, 110, 130]
    DATA_B = [90, 140, 180, 60, 200, 80, 160]

    if "rerun_count" not in st.session_state:
        st.session_state.rerun_count = 0

    if st.button("Rerun"):
        st.session_state.rerun_count += 1

    st.write(f"Rerun count: {st.session_state.rerun_count}")

    data = DATA_A if st.session_state.rerun_count % 2 == 0 else DATA_B
    options = {
        "xAxis": {"type": "category", "data": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]},
        "yAxis": {"type": "value"},
        "series": [{"data": data, "type": "bar"}],
    }

    col_no_key, col_with_key = st.columns(2)
    with col_no_key:
        st.caption("No key — remounts and replays entry animation")
        st_echarts(options=options)
    with col_with_key:
        st.caption('key="stable" — smoothly animates between data sets')
        st_echarts(options=options, key="stable")

    _show_source(page_key)


def page_on_change():
    st.header("7. `on_change`")
    st.markdown(
        "`on_change` is a Python callback that runs server-side each time a chart event fires. "
        "Here, clicking any bar triggers the `click` event, which calls `on_change` — "
        "the callback randomizes the data and the chart animates to the new values."
    )

    if "on_change_data" not in st.session_state:
        st.session_state.on_change_data = [120, 200, 150, 80, 70, 110, 130]
    if "change_count" not in st.session_state:
        st.session_state.change_count = 0

    def on_chart_change():
        import random
        st.session_state.change_count += 1
        st.session_state.on_change_data = [random.randint(30, 250) for _ in range(7)]

    options = {
        "xAxis": {"type": "category", "data": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]},
        "yAxis": {"type": "value"},
        "series": [{"data": st.session_state.on_change_data, "type": "bar"}],
    }
    st_echarts(
        options=options,
        events={"click": "function(p){return p.name}"},
        on_change=on_chart_change,
        key="on_change_demo",
    )
    st.metric("Times on_change fired", st.session_state.change_count)
    _show_source(page_on_change)


def page_map():
    st.header("8. `map` and the `Map` class")
    st.markdown(
        "Register a custom GeoJSON map with `Map(map_name=..., geo_json=...)`, "
        "then reference `map_name` in a `geo` or `map` series."
    )

    WORLD_GEOJSON_URL = (
        "https://raw.githubusercontent.com/johan/world.geo.json/master/countries.geo.json"
    )

    @st.cache_data(show_spinner="Fetching world GeoJSON…")
    def load_world_geojson():
        with urlopen(WORLD_GEOJSON_URL) as r:
            return json.loads(r.read().decode())

    try:
        world_geo = load_world_geojson()
        map_obj = Map(map_name="World", geo_json=world_geo)
        map_options = {
            "title": {"text": "World Map — random data"},
            "visualMap": {
                "min": 0,
                "max": 100,
                "inRange": {"color": ["#e0f3f8", "#4575b4"]},
            },
            "series": [
                {
                    "type": "map",
                    "map": "World",
                    "data": [
                        {"name": "United States of America", "value": 80},
                        {"name": "China", "value": 95},
                        {"name": "Brazil", "value": 60},
                        {"name": "India", "value": 75},
                        {"name": "Australia", "value": 50},
                        {"name": "Germany", "value": 55},
                        {"name": "France", "value": 45},
                        {"name": "Russia", "value": 70},
                    ],
                    "emphasis": {"label": {"show": True}},
                }
            ],
        }
        result = st_echarts(
            options=map_options,
            map=map_obj,
            height="450px",
            on_select="rerun",
            selection_mode="points",
            key="map_demo",
        )
        points = result["selection"]["points"]
        if points:
            p = points[0]
            st.write(f"**{p['name']}** — value: {p['value']}")
        else:
            st.info("Click a country to see its name and value.")
    except Exception as exc:
        st.warning(f"Could not load GeoJSON (network unavailable?): {exc}")

    _show_source(page_map)


def page_jscode():
    st.header("9. `JsCode`")
    st.markdown(
        "`JsCode` wraps a JavaScript string so the frontend evaluates it as a live function "
        "rather than passing it as a plain string. Use it wherever ECharts expects a callback "
        "(formatters, symbol sizes, color functions, …)."
    )

    st.subheader("a) Custom tooltip formatter")
    tooltip_options = {
        **OPTIONS,
        "tooltip": {
            "trigger": "axis",
            "formatter": JsCode("function(p){return p[0].name + ': ' + p[0].value + ' units'}"),
        },
    }
    st_echarts(options=tooltip_options, key="jscode_tooltip")

    st.subheader("b) Dynamic symbol size in scatter")
    scatter_options = {
        "xAxis": {"type": "value"},
        "yAxis": {"type": "value"},
        "series": [
            {
                "type": "scatter",
                "symbolSize": JsCode("function(v){return v[2] * 5}"),
                "data": [
                    [3.0, 4.5, 8],
                    [7.0, 2.0, 4],
                    [1.5, 6.0, 12],
                    [5.5, 5.5, 6],
                    [9.0, 1.0, 3],
                ],
            }
        ],
    }
    st_echarts(options=scatter_options, key="jscode_scatter")
    _show_source(page_jscode)


def page_layouts():
    st.header("10. Collapsible layouts")
    st.markdown(
        "Charts inside containers that hide content initially "
        "resize correctly when revealed."
    )

    st.subheader("Tabs")
    tab_empty, tab_chart = st.tabs(["No chart here", "Chart here"])
    with tab_empty:
        st.write("Switch to the **Chart here** tab.")
    with tab_chart:
        st_echarts(options=OPTIONS, key="tab_demo")
    st.caption("Chart correctly sizes itself when its tab becomes visible.")

    st.subheader("Expander")
    with st.expander("Expand to see chart"):
        st_echarts(options=OPTIONS, key="expander_demo")
    st.caption("Chart correctly sizes itself when the expander is opened.")

    st.subheader("Popover")
    with st.popover("Show chart"):
        st_echarts(options=OPTIONS, width="400px", key="popover_demo")
    st.caption("Chart renders inside a popover when the button is clicked.")

    st.subheader("Dialog")

    @st.dialog("Chart dialog")
    def show_chart_dialog():
        st_echarts(options=OPTIONS, key="dialog_demo")

    if st.button("Open dialog"):
        show_chart_dialog()
    st.caption("Chart renders inside a modal dialog.")

    _show_source(page_layouts)


def page_pyecharts():
    st.header("11. PyECharts")
    st.markdown(
        "`st_pyecharts` accepts a PyECharts chart object directly. "
        "Install with `pip install streamlit-echarts[pyecharts]`."
    )

    try:
        from pyecharts.charts import Bar, Line, Pie
        from pyecharts import options as opts
    except ImportError:
        st.error(
            "This page requires the `pyecharts` package. "
            "Install it with: `pip install streamlit-echarts[pyecharts]`"
        )
        return

    toolbox = opts.ToolboxOpts(
        is_show=True,
        feature={
            "saveAsImage": {},
            "restore": {},
            "dataView": {"readOnly": False},
        },
    )

    st.subheader("Bar chart")
    bar = (
        Bar()
        .add_xaxis(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"])
        .add_yaxis("Sales", [120, 200, 150, 80, 70, 110, 130])
        .set_global_opts(
            title_opts=opts.TitleOpts(title="Weekly Sales"),
            toolbox_opts=toolbox,
        )
    )
    st_pyecharts(bar, key="pyecharts_bar")

    st.subheader("Line chart")
    line = (
        Line()
        .add_xaxis(["Jan", "Feb", "Mar", "Apr", "May", "Jun"])
        .add_yaxis("Revenue", [820, 932, 901, 934, 1290, 1330], is_smooth=True)
        .set_global_opts(
            title_opts=opts.TitleOpts(title="Monthly Revenue"),
            toolbox_opts=toolbox,
        )
    )
    st_pyecharts(line, key="pyecharts_line")

    st.subheader("Pie chart")
    pie = (
        Pie()
        .add(
            "",
            [("Shirts", 40), ("Cardigans", 30), ("Chiffon", 20), ("Pants", 10)],
            radius=["40%", "70%"],
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title="Product Mix"),
            toolbox_opts=toolbox,
        )
        .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {d}%"))
    )
    st_pyecharts(pie, key="pyecharts_pie")

    st.subheader("With events")
    click_result = st_pyecharts(
        bar,
        events={"click": "function(p){return {name: p.name, value: p.value}}"},
        key="pyecharts_events",
    )
    if click_result:
        st.write("Last click:", click_result)
    else:
        st.info("Click a bar to fire a click event.")

    _show_source(page_pyecharts)


# ---------------------------------------------------------------------------
# Navigation
# ---------------------------------------------------------------------------

pg = st.navigation([
    st.Page(page_options,    title="1. options",            icon=":material/bar_chart:"),
    st.Page(page_height_width, title="2. height & width",  icon=":material/aspect_ratio:"),
    st.Page(page_renderer,   title="3. renderer",           icon=":material/tune:"),
    st.Page(page_theme,      title="4. theme",              icon=":material/palette:"),
    st.Page(page_interactions, title="5. interactions",       icon=":material/mouse:"),
    st.Page(page_key,        title="6. key",                icon=":material/key:"),
    st.Page(page_on_change,  title="7. on_change",          icon=":material/notifications:"),
    st.Page(page_map,        title="8. map / Map",          icon=":material/map:"),
    st.Page(page_jscode,     title="9. JsCode",             icon=":material/code:"),
    st.Page(page_layouts,    title="10. collapsible layouts", icon=":material/dashboard:"),
    st.Page(page_pyecharts,  title="11. pyecharts",         icon=":material/auto_awesome:"),
])
pg.run()
