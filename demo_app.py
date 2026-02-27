import json
from urllib.request import urlopen

import streamlit as st

from streamlit_echarts import JsCode, Map, st_echarts

# Base bar chart options reused across pages
OPTIONS = {
    "xAxis": {"type": "category", "data": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]},
    "yAxis": {"type": "value"},
    "series": [{"data": [120, 200, 150, 80, 70, 110, 130], "type": "bar"}],
}


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------

def page_options():
    st.header("1. `options`")
    st.markdown(
        "`options` is the only required argument. "
        "It accepts a plain Python `dict` that maps 1-to-1 to the ECharts option object."
    )
    with st.echo():
        options = {
            "xAxis": {"type": "category", "data": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]},
            "yAxis": {"type": "value"},
            "series": [{"data": [120, 200, 150, 80, 70, 110, 130], "type": "bar"}],
        }
        st_echarts(options=options, key="options_demo")


def page_height_width():
    st.header("2. `height` and `width`")
    st.markdown(
        "Both accept any valid CSS size string. "
        '`height` defaults to `"300px"`; `width` defaults to `"100%"`.'
    )

    col1, col2 = st.columns(2)
    with col1:
        st.caption('height="150px"')
        with st.echo():
            st_echarts(options=OPTIONS, height="150px", key="height_small")
    with col2:
        st.caption('height="500px"')
        with st.echo():
            st_echarts(options=OPTIONS, height="500px", key="height_large")

    st.caption('width="50%"')
    with st.echo():
        st_echarts(options=OPTIONS, width="50%", key="width_half")


def page_renderer():
    st.header("3. `renderer`")
    st.markdown(
        '`"canvas"` (default) is faster for many data points. '
        '`"svg"` produces a scalable graphic that prints crisply and is accessible to screen readers.'
    )
    renderer = st.radio("renderer", ["canvas", "svg"], horizontal=True, key="renderer_radio")
    with st.echo():
        st_echarts(options=OPTIONS, renderer=renderer, key="renderer_demo")


def page_theme():
    st.header("4. `theme`")

    BUILTIN_THEMES = ["", "dark", "streamlit"]

    tab_string, tab_dict = st.tabs(["Built-in string theme", "Custom dict theme"])

    with tab_string:
        theme_name = st.selectbox(
            "Theme name (empty string = default)",
            BUILTIN_THEMES,
            key="theme_selectbox",
        )
        with st.echo():
            st_echarts(options=OPTIONS, theme=theme_name, key=f"theme_{theme_name}")

    with tab_dict:
        with st.echo():
            CUSTOM_THEME = {
                "color": ["#e06c75", "#98c379", "#61afef"],
                "backgroundColor": "#282c34",
                "textStyle": {"color": "#abb2bf"},
            }
            st_echarts(options=OPTIONS, theme=CUSTOM_THEME, key="theme_dict_demo")


def page_events():
    st.header("5. `events`")
    st.markdown(
        "`events` maps ECharts event names to JavaScript handler strings. "
        "The handler's **return value** becomes the component's return value in Python."
    )

    st.subheader("click event")
    with st.echo():
        click_result = st_echarts(
            options=OPTIONS,
            events={"click": "function(p){return {name: p.name, value: p.value}}"},
            key="events_click",
        )
    if click_result:
        st.write("Last click:", click_result)
    else:
        st.info("Click a bar to fire a click event.")

    st.subheader("mouseover event")
    st.caption("Note: `mouseover` fires on every hover — use `click` for less noise.")
    with st.echo():
        hover_result = st_echarts(
            options=OPTIONS,
            events={"mouseover": "function(p){return {name: p.name, value: p.value}}"},
            key="events_mouseover",
        )
    if hover_result:
        st.write("Last hover:", hover_result)
    else:
        st.info("Hover over a bar to fire a mouseover event.")


def page_selection():
    st.header("5b. `on_select` and `selection_mode`")
    st.markdown(
        "`on_select` enables structured selection interactions without writing JavaScript. "
        "`selection_mode` controls which interactions are active: `\"points\"` (click), `\"box\"` (rect brush), `\"lasso\"` (polygon brush)."
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

    st.subheader("Click selection (points) — filter source data")
    with st.echo():
        select_result = st_echarts(
            options=OPTIONS,
            key="select_points",
            on_select="rerun",
            selection_mode="points",
        )

        # Use point_indices to filter back to source data
        indices = select_result["selection"]["point_indices"]
        output = st.empty()
        if indices:
            output.table([SALES_DATA[i] for i in indices if i < len(SALES_DATA)])
        else:
            output.caption("Click a bar to filter the source data.")

    st.subheader("Brush selection (box + lasso) + session state")
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
    with st.echo():
        brush_result = st_echarts(
            options=scatter_options,
            key="select_brush",
            on_select="rerun",
            selection_mode=("box", "lasso"),
        )

    col_return2, col_state2 = st.columns(2)
    with col_return2:
        st.caption("Return value (`result.selection`)")
        sel = brush_result["selection"]
        if sel["point_indices"]:
            st.json(sel)
        else:
            st.caption("Use the brush tool in the toolbar to select points.")
    with col_state2:
        st.caption("`st.session_state['select_brush'].selection`")
        state_val2 = st.session_state.get("select_brush")
        if state_val2 and state_val2.get("selection", {}).get("point_indices"):
            st.json(state_val2["selection"])
        else:
            st.caption("Selection will appear here after brushing.")


def page_key():
    st.header("6. `key`")
    st.markdown(
        "Without `key`, Streamlit may remount the component on each rerun (e.g. after a widget interaction), "
        "replaying the entry animation and losing any internal ECharts state. "
        "A stable `key` tells Streamlit to reuse the same component instance across reruns."
    )

    if "rerun_count" not in st.session_state:
        st.session_state.rerun_count = 0

    if st.button("Rerun"):
        st.session_state.rerun_count += 1

    st.write(f"Rerun count: {st.session_state.rerun_count}")

    col_no_key, col_with_key = st.columns(2)
    with col_no_key:
        st.caption("No key — may remount and replay animation on rerun")
        with st.echo():
            st_echarts(options=OPTIONS)
    with col_with_key:
        st.caption('key="stable" — persists across reruns')
        with st.echo():
            st_echarts(options=OPTIONS, key="stable")


def page_on_change():
    st.header("7. `on_change`")
    st.markdown(
        "`on_change` is a server-side Python callback invoked whenever the component "
        "fires an event (i.e. whenever the return value changes). "
        "Use it as an alternative to checking the return value manually."
    )

    if "change_count" not in st.session_state:
        st.session_state.change_count = 0

    with st.echo():
        def on_chart_change():
            st.session_state.change_count += 1

        st_echarts(
            options=OPTIONS,
            events={"click": "function(p){return p.name}"},
            on_change=on_chart_change,
            key="on_change_demo",
        )
    st.metric("Times on_change fired", st.session_state.change_count)


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
        with st.echo():
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
            st_echarts(options=map_options, map=map_obj, height="450px", key="map_demo")
    except Exception as exc:
        st.warning(f"Could not load GeoJSON (network unavailable?): {exc}")


def page_jscode():
    st.header("9. `JsCode`")
    st.markdown(
        "`JsCode` wraps a JavaScript string so the frontend evaluates it as a live function "
        "rather than passing it as a plain string. Use it wherever ECharts expects a callback "
        "(formatters, symbol sizes, color functions, …)."
    )

    st.subheader("a) Custom tooltip formatter")
    with st.echo():
        tooltip_options = {
            **OPTIONS,
            "tooltip": {
                "trigger": "axis",
                "formatter": JsCode("function(p){return p[0].name + ': ' + p[0].value + ' units'}"),
            },
        }
        st_echarts(options=tooltip_options, key="jscode_tooltip")

    st.subheader("b) Dynamic symbol size in scatter")
    with st.echo():
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


def page_layouts():
    st.header("10 & 11. Layout containers")
    st.markdown("Charts inside `st.tabs` and `st.expander` resize correctly when revealed.")

    st.subheader("Tabs")
    with st.echo():
        tab_empty, tab_chart = st.tabs(["No chart here", "Chart here"])
        with tab_empty:
            st.write("Switch to the **Chart here** tab.")
        with tab_chart:
            st_echarts(options=OPTIONS, key="tab_demo")
    st.caption("Chart correctly sizes itself when its tab becomes visible.")

    st.subheader("Expander")
    with st.echo():
        with st.expander("Expand to see chart"):
            st_echarts(options=OPTIONS, key="expander_demo")
    st.caption("Chart correctly sizes itself when the expander is opened.")


# ---------------------------------------------------------------------------
# Navigation
# ---------------------------------------------------------------------------

pg = st.navigation([
    st.Page(page_options,    title="1. options",            icon=":material/bar_chart:"),
    st.Page(page_height_width, title="2. height & width",  icon=":material/aspect_ratio:"),
    st.Page(page_renderer,   title="3. renderer",           icon=":material/tune:"),
    st.Page(page_theme,      title="4. theme",              icon=":material/palette:"),
    st.Page(page_events,     title="5. events",             icon=":material/mouse:"),
    st.Page(page_selection,  title="5b. on_select",         icon=":material/select_all:"),
    st.Page(page_key,        title="6. key",                icon=":material/key:"),
    st.Page(page_on_change,  title="7. on_change",          icon=":material/notifications:"),
    st.Page(page_map,        title="8. map / Map",          icon=":material/map:"),
    st.Page(page_jscode,     title="9. JsCode",             icon=":material/code:"),
    st.Page(page_layouts,    title="10–11. layouts",        icon=":material/dashboard:"),
])
pg.run()
