import os
from typing import Dict
from typing import Union

import simplejson as json
import streamlit as st
from pyecharts.charts.base import Base
from pyecharts.charts.base import default

_RELEASE = False  # on packaging, pass this to True

if not _RELEASE:
    _component_func = st.declare_component("st_echart", url="http://localhost:3001",)
else:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend/build")
    _component_func = st.declare_component("st_echart", path=build_dir)


def st_echarts(
    options: Dict,
    theme: str = "",
    height: str = "300px",
    width: str = "100%",
    key: str = None,
):
    """Display echarts chart from options dictionary
    :param options: dictionary of echarts options
    :param theme: prebuilt theme as string, or object
    :param height: height of div wrapper
    :param width: width of div wrapper
    :param key: assign a key to prevent component remounting
    :return: chart
    """
    return _component_func(
        options=options, theme=theme, height=height, width=width, key=key, default=None
    )


def st_pyecharts(
    chart: Base,
    theme: Union[str, Dict] = "",
    height: str = "300px",
    width: str = "100%",
    key: str = None,
):
    """Display echarts chart from pyecharts instance
    :param chart: pyecharts instance
    :param theme: prebuilt theme as string, or object
    :param height: height of div wrapper
    :param width: width of div wrapper
    :param key: assign a key to prevent component remounting
    :return: chart
    """
    options = json.dumps(chart.get_options(), default=default, ignore_nan=True)
    return _component_func(
        options=json.loads(options), theme=theme, height=height, width=width, key=key, default=None
    )
