import json
from urllib.request import urlopen

import streamlit as st

from streamlit_echarts import JsCode, Map, st_echarts

st.title("st_echarts — Feature Reference")
st.markdown(
    "One section per `st_echarts` argument. "
    "Most sections reuse the same simple bar chart so attention stays on the parameter being demonstrated. "
    "See the [Apache ECharts docs](https://echarts.apache.org/en/option.html) for the full `options` schema."
)

st.divider()

# ---------------------------------------------------------------------------
# 1. options
# ---------------------------------------------------------------------------
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

st.divider()

# ---------------------------------------------------------------------------
# 2. height and width
# ---------------------------------------------------------------------------
st.header("2. `height` and `width`")
st.markdown(
    "Both accept any valid CSS size string. "
    '`height` defaults to `"300px"`; `width` defaults to `"100%"`.'
)

col1, col2 = st.columns(2)
with col1:
    st.caption('height="150px"')
    with st.echo():
        st_echarts(options=options, height="150px", key="height_small")
with col2:
    st.caption('height="500px"')
    with st.echo():
        st_echarts(options=options, height="500px", key="height_large")

st.caption('width="50%"')
with st.echo():
    st_echarts(options=options, width="50%", key="width_half")

st.divider()

# ---------------------------------------------------------------------------
# 3. renderer
# ---------------------------------------------------------------------------
st.header("3. `renderer`")
st.markdown(
    '`"canvas"` (default) is faster for many data points. '
    '`"svg"` produces a scalable graphic that prints crisply and is accessible to screen readers.'
)
renderer = st.radio("renderer", ["canvas", "svg"], horizontal=True, key="renderer_radio")
with st.echo():
    st_echarts(options=options, renderer=renderer, key="renderer_demo")

st.divider()

# ---------------------------------------------------------------------------
# 4. theme
# ---------------------------------------------------------------------------
st.header("4. `theme`")

BUILTIN_THEMES = ["", "dark", "streamlit"]
# Classic themes (vintage, macarons, chalk, etc.) require bundled theme JSON files
# that are not yet included — see `classic_themes_pack` in docs/roadmap.yaml.

tab_string, tab_dict = st.tabs(["Built-in string theme", "Custom dict theme"])

with tab_string:
    theme_name = st.selectbox(
        "Theme name (empty string = default)",
        BUILTIN_THEMES,
        key="theme_selectbox",
    )
    with st.echo():
        st_echarts(options=options, theme=theme_name, key=f"theme_{theme_name}")

with tab_dict:
    with st.echo():
        CUSTOM_THEME = {
            "color": ["#e06c75", "#98c379", "#61afef"],
            "backgroundColor": "#282c34",
            "textStyle": {"color": "#abb2bf"},
        }
        st_echarts(options=options, theme=CUSTOM_THEME, key="theme_dict_demo")

st.divider()

# ---------------------------------------------------------------------------
# 5. events
# ---------------------------------------------------------------------------
st.header("5. `events`")
st.markdown(
    "`events` maps ECharts event names to JavaScript handler strings. "
    "The handler's **return value** becomes the component's return value in Python."
)

st.subheader("click event")
with st.echo():
    click_result = st_echarts(
        options=options,
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
        options=options,
        events={"mouseover": "function(p){return {name: p.name, value: p.value}}"},
        key="events_mouseover",
    )
if hover_result:
    st.write("Last hover:", hover_result)
else:
    st.info("Hover over a bar to fire a mouseover event.")

st.divider()

# ---------------------------------------------------------------------------
# 6. key
# ---------------------------------------------------------------------------
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
        st_echarts(options=options)
with col_with_key:
    st.caption('key="stable" — persists across reruns')
    with st.echo():
        st_echarts(options=options, key="stable")

st.divider()

# ---------------------------------------------------------------------------
# 7. on_change
# ---------------------------------------------------------------------------
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
        options=options,
        events={"click": "function(p){return p.name}"},
        on_change=on_chart_change,
        key="on_change_demo",
    )
st.metric("Times on_change fired", st.session_state.change_count)

st.divider()

# ---------------------------------------------------------------------------
# 8. map and the Map class
# ---------------------------------------------------------------------------
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

st.divider()

# ---------------------------------------------------------------------------
# 9. JsCode
# ---------------------------------------------------------------------------
st.header("9. `JsCode`")
st.markdown(
    "`JsCode` wraps a JavaScript string so the frontend evaluates it as a live function "
    "rather than passing it as a plain string. Use it wherever ECharts expects a callback "
    "(formatters, symbol sizes, color functions, …)."
)

st.subheader("a) Custom tooltip formatter")
with st.echo():
    tooltip_options = {
        **options,
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

st.divider()

# ---------------------------------------------------------------------------
# 10. Tabs layout
# ---------------------------------------------------------------------------
st.header("10. Tabs layout")
st.markdown("Charts inside `st.tabs` resize correctly when their tab becomes visible.")

with st.echo():
    tab_empty, tab_chart = st.tabs(["No chart here", "Chart here"])
    with tab_empty:
        st.write("Switch to the **Chart here** tab.")
    with tab_chart:
        st_echarts(options=options, key="tab_demo")

st.caption("Chart correctly sizes itself when its tab becomes visible.")

st.divider()

# ---------------------------------------------------------------------------
# 11. Expander layout
# ---------------------------------------------------------------------------
st.header("11. Expander layout")
st.markdown("Charts inside `st.expander` resize correctly when the expander is opened.")

with st.echo():
    with st.expander("Expand to see chart"):
        st_echarts(options=options, key="expander_demo")

st.caption("Chart correctly sizes itself when the expander is opened.")
