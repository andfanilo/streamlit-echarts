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
