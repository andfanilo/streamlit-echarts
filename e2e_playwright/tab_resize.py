"""Fixture app for tab resize E2E test."""

import streamlit as st

from streamlit_echarts import st_echarts

st.title("Tab Resize Test")

tab1, tab2 = st.tabs(["Tab 1", "Tab 2"])

with tab1:
    st.write("This is tab 1 — no chart here.")

with tab2:
    options = {
        "animation": False,
        "xAxis": {"type": "category", "data": ["A", "B", "C"]},
        "yAxis": {"type": "value"},
        "series": [{"data": [10, 20, 30], "type": "bar"}],
    }
    st_echarts(options=options, height="300px", key="tab_chart")
