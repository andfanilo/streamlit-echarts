import streamlit as st
from streamlit_echarts import st_echarts

st.subheader("Streamlit ECharts Demo")

options = {
    "xAxis": {
        "type": "category",
        "data": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
    },
    "yAxis": {"type": "value"},
    "series": [{"data": [820, 932, 901, 934, 1290, 1330, 1320], "type": "bar"}],
}

events = {
    "click": "function(params) { return [params.type, params.name, params.value]; }"
}

result = st_echarts(
    options=options,
    events=events,
    theme="streamlit",
    height="400px",
)

st.markdown("---")
st.subheader("Event Result")
if result and result.get("chart_event"):
    st.write(f"You clicked on: {result['chart_event']}")
else:
    st.write("Click on a bar in the chart to see events.")

st.markdown("---")
st.subheader("Tab Resize Test")
st.write("The chart is on Tab 2 (initially hidden). Switch tabs to verify it renders correctly.")

tab1, tab2 = st.tabs(["Tab 1", "Tab 2"])

with tab1:
    st.write("No chart here — switch to Tab 2.")

with tab2:
    tab_options = {
        "animation": False,
        "xAxis": {"type": "category", "data": ["A", "B", "C", "D", "E"]},
        "yAxis": {"type": "value"},
        "series": [{"data": [10, 40, 25, 60, 15], "type": "bar"}],
    }
    st_echarts(options=tab_options, height="300px", key="tab_chart")

st.markdown("---")
st.subheader("Expander Resize Test")
st.write("The chart below is inside an expander (initially collapsed).")

with st.expander("Click to expand chart"):
    expander_options = {
        "animation": False,
        "xAxis": {"type": "category", "data": ["Jan", "Feb", "Mar", "Apr"]},
        "yAxis": {"type": "value"},
        "series": [{"data": [150, 230, 180, 310], "type": "line"}],
    }
    st_echarts(options=expander_options, height="300px", key="expander_chart")
