from __future__ import annotations

import importlib.metadata
from collections.abc import Callable

import streamlit as st

__version__ = importlib.metadata.version("streamlit-echarts")

out = st.components.v2.component(
    "streamlit-echarts.streamlit_echarts",
    js="index-*.js",
    html='<div class="echarts-container"></div>',
    isolate_styles=False,
)


class Map:
    def __init__(
        self, map_name: str, geo_json: dict, special_areas: dict | None = None
    ) -> None:
        self.map_name: str = map_name
        self.geo_json: dict = geo_json
        self.special_areas: dict | None = special_areas

    def to_json(self):
        return {
            "mapName": self.map_name,
            "geoJson": self.geo_json,
            "specialAreas": self.special_areas,
        }


class JsCode:
    def __init__(self, js_code: str):
        js_placeholder = "--x_x--0_0--"
        self.js_code = f"{js_placeholder}{js_code}{js_placeholder}"


def st_echarts(
    options: dict,
    theme: str | dict = "",
    events: dict[str, str] | None = None,
    height: str = "300px",
    width: str = "100%",
    renderer: str = "canvas",
    map: Map | None = None,
    key: str | None = None,
    on_change: Callable[[], None] | None = None,
):
    """Display an ECharts instance in Streamlit

    Parameters
    ----------
    options: dict
        Dictionary of echarts options. JS code should have been wrapped beforehand.
    theme: str | dict
        Prebuilt theme, or object defining theme
    events: dict
        Dictionary of mouse events to string JS functions.
        Don't wrap values with JsCode placeholder.
    height: str
        Height of ECharts chart
    width: str
        Width of ECharts chart
    renderer: {'canvas', 'svg'}
        Renderer for displaying chart
    map: Map
        Details of GeoJSON map to register into echarts
    key: str
        An optional string to use as the unique key for the widget.
        Assign a key so the component is not remount every time the script is rerun.
    on_change: callable
        Optional callback invoked when the component fires a chart event.

    Example
    -------
    >>> from streamlit_echarts import st_echarts
    >>>
    >>> options = {
    ...     "xAxis": {
    ...         "type": "category",
    ...         "data": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
    ...     },
    ...     "yAxis": {"type": "value"},
    ...     "series": [
    ...         {"data": [820, 932, 901, 934, 1290, 1330, 1320], "type": "line"}
    ...     ],
    ... }
    >>> st_echarts(options=options)
    """
    if events is None:
        events = {}

    component_value = out(
        data={
            "options": options,
            "theme": theme,
            "onEvents": {k: JsCode(v).js_code for k, v in events.items()},
            "height": height,
            "width": width,
            "renderer": renderer,
            "map": map.to_json() if map is not None else None,
        },
        default={},
        key=key,
        on_chart_event_change=on_change if on_change else lambda: None,
    )

    return component_value
