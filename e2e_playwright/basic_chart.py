"""Minimal Streamlit app for E2E testing of the st_echarts component."""

from streamlit_echarts import JsCode, st_echarts

import streamlit as st

st.title("ECharts E2E Tests")

# --- Basic line chart ---
st.subheader("Basic Line Chart")
basic_options = {
    "animation": False,
    "xAxis": {
        "type": "category",
        "data": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
    },
    "yAxis": {"type": "value"},
    "series": [{"data": [820, 932, 901, 934, 1290, 1330, 1320], "type": "line"}],
}
st_echarts(options=basic_options, height="300px", key="basic_line")

# --- Streamlit theme ---
st.subheader("Streamlit Theme")
st_echarts(options=basic_options, theme="streamlit", height="300px", key="streamlit_theme")

# --- Dark theme ---
st.subheader("Dark Theme")
st_echarts(options=basic_options, theme="dark", height="300px", key="dark_theme")

# --- JsCode event ---
st.subheader("JsCode Event")
event_options = {
    "xAxis": {"data": ["shirt", "pants", "shoes"]},
    "yAxis": {},
    "series": [{"name": "sales", "type": "bar", "data": [5, 20, 36]}],
}
events = {"click": "function(params) { return params.name; }"}
result = st_echarts(options=event_options, events=events, height="300px", key="event")
if result:
    st.write(f"Clicked: {result}")
