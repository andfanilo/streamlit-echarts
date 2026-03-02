from __future__ import annotations

import importlib.metadata
import json
from collections.abc import Callable, Iterable
from typing import Literal

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

    def __str__(self):
        return self.js_code

    def __repr__(self):
        return f"JsCode({self.js_code})"


EMPTY_SELECTION = {
    "points": [],
    "point_indices": [],
    "series_point_indices": {},
    "box": [],
    "lasso": [],
}

_VALID_SELECTION_MODES = {"points", "box", "lasso"}


def _serialize_options(obj):
    """Recursively replace JsCode instances with their placeholder string."""
    if isinstance(obj, JsCode):
        return obj.js_code
    if isinstance(obj, dict):
        return {k: _serialize_options(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_serialize_options(v) for v in obj]
    return obj


def st_echarts(
    options: dict,
    theme: str | dict = "streamlit",
    events: dict[str, str] | None = None,
    height: str = "300px",
    width: str = "100%",
    renderer: str = "canvas",
    replace_merge: str | list[str] | None = None,
    map: Map | None = None,
    key: str | None = None,
    on_change: Callable[[], None] | None = None,
    on_select: Literal["ignore", "rerun"] | Callable[[], None] = "ignore",
    selection_mode: str | Iterable[str] = ("points", "box", "lasso"),
):
    """Display an ECharts instance in Streamlit

    Parameters
    ----------
    options: dict
        Dictionary of echarts options. JS code should have been wrapped beforehand.
    theme: str | dict
        Prebuilt theme, or object defining theme. Defaults to ``"streamlit"``
        which automatically adapts to Streamlit's light/dark mode.
    events: dict
        Dictionary of mouse events to string JS functions.
        Don't wrap values with JsCode placeholder.
    height: str
        Height of ECharts chart
    width: str
        Width of ECharts chart
    renderer: {'canvas', 'svg'}
        Renderer for displaying chart
    replace_merge: str or list of str or None
        Component types to replace instead of merge when updating options.
        Set to ``"series"`` or ``["series"]`` to enable ``universalTransition``
        animations between different data shapes. Defaults to ``None`` which
        fully replaces all options (``notMerge: true``).
    map: Map
        Details of GeoJSON map to register into echarts
    key: str
        An optional string to use as the unique key for the widget.
        Assign a key so the component is not remount every time the script is rerun.
    on_change: callable
        Optional callback invoked when the component fires a chart event.
    on_select: 'ignore' | 'rerun' | callable
        Controls selection behavior. 'ignore' disables selection (default).
        'rerun' triggers a Streamlit rerun on selection. A callable is invoked
        as a callback on selection change.
    selection_mode: str or iterable of str
        Which selection interactions to enable. Valid values: 'points', 'box', 'lasso'.
        Defaults to all three.

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

    # Normalize and validate selection_mode
    if isinstance(selection_mode, str):
        selection_mode = [selection_mode]
    else:
        selection_mode = list(selection_mode)

    invalid_modes = set(selection_mode) - _VALID_SELECTION_MODES
    if invalid_modes:
        raise ValueError(
            f"Invalid selection_mode values: {invalid_modes}. "
            f"Valid values are: {_VALID_SELECTION_MODES}"
        )

    # Validate on_select
    if not callable(on_select) and on_select not in ("ignore", "rerun"):
        raise ValueError(
            f"on_select must be 'ignore', 'rerun', or a callable, got {on_select!r}"
        )

    selection_active = on_select != "ignore"

    data = {
        "options": _serialize_options(options),
        "theme": theme,
        "onEvents": {k: JsCode(v).js_code for k, v in events.items()},
        "height": height,
        "width": width,
        "renderer": renderer,
        "replaceMerge": replace_merge,
        "map": map.to_json() if map is not None else None,
        "selectionActive": selection_active,
        "selectionMode": list(selection_mode) if selection_active else [],
    }

    mount_kwargs: dict = {
        "data": data,
        "key": key,
        "on_chart_event_change": on_change if on_change else lambda: None,
    }

    if selection_active:
        mount_kwargs["on_selection_change"] = (
            on_select if callable(on_select) else lambda: None
        )
        mount_kwargs["default"] = {"selection": EMPTY_SELECTION}
    else:
        mount_kwargs["default"] = {}

    component_value = out(**mount_kwargs)

    return component_value


def st_pyecharts(
    chart,
    theme: str | dict = "streamlit",
    events: dict[str, str] | None = None,
    height: str = "300px",
    width: str = "100%",
    renderer: str = "canvas",
    map: Map | None = None,
    key: str | None = None,
    on_change: Callable[[], None] | None = None,
    on_select: Literal["ignore", "rerun"] | Callable[[], None] = "ignore",
    selection_mode: str | Iterable[str] = ("points", "box", "lasso"),
):
    """Display a PyECharts chart instance in Streamlit.

    Requires the ``pyecharts`` optional dependency::

        pip install streamlit-echarts[pyecharts]

    Parameters
    ----------
    chart
        A pyecharts chart instance (e.g. ``Bar()``, ``Line()``, etc.).
    theme, events, height, width, renderer, map, key, on_change, on_select, selection_mode
        Same as :func:`st_echarts`.
    """
    try:
        from pyecharts.charts.base import Base  # noqa: F401
    except ImportError:
        raise ImportError(
            "st_pyecharts requires the 'pyecharts' package. "
            "Install it with: pip install streamlit-echarts[pyecharts]"
        ) from None

    options = json.loads(chart.dump_options())

    return st_echarts(
        options=options,
        theme=theme,
        events=events,
        height=height,
        width=width,
        renderer=renderer,
        map=map,
        key=key,
        on_change=on_change,
        on_select=on_select,
        selection_mode=selection_mode,
    )
