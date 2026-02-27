"""Streamlit app for E2E testing of the selection API."""

import streamlit as st

from streamlit_echarts import st_echarts

st.title("Selection E2E Tests")

# --- Bar chart with on_select="rerun" ---
st.subheader("Click Selection")
bar_options = {
    "animation": False,
    "xAxis": {"type": "category", "data": ["A", "B", "C"]},
    "yAxis": {"type": "value"},
    "series": [{"name": "Sales", "type": "bar", "data": [10, 20, 30]}],
}
result = st_echarts(
    options=bar_options,
    on_select="rerun",
    selection_mode="points",
    height="300px",
    key="click_select",
)
if result and result.get("selection"):
    sel = result["selection"]
    st.write(f"Selected points: {len(sel['points'])}")
    if sel["points"]:
        st.write(f"First point value: {sel['points'][0]['value']}")

# --- Ignore mode chart ---
st.subheader("Ignore Mode")
ignore_result = st_echarts(
    options=bar_options,
    on_select="ignore",
    height="300px",
    key="ignore_select",
)
st.write(f"Ignore result type: {type(ignore_result).__name__}")
