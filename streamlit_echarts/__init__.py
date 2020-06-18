import datetime
import simplejson as json
import os
from typing import Dict
from typing import Sequence
from typing import Union

import streamlit as st
from pyecharts.charts.base import Base
from pyecharts.commons.utils import JsCode
from pyecharts.commons.utils import remove_key_with_none_value
from pyecharts.options.series_options import BasicOpts

_RELEASE = False  # on packaging, pass this to True

if not _RELEASE:
    _component_func = st.declare_component("st_echart", url="http://localhost:3001",)
else:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend/build")
    _component_func = st.declare_component("st_echart", path=build_dir)


def st_echarts(options: Dict, theme: str = "", key=None):
    """Display echarts chart from options dictionary
    :param options: dictionary of options
    :param theme: prebuilt theme or object
    :param key:
    :return: chart
    """
    return _component_func(options=options, theme=theme, key=key, default=None)


def st_pyecharts(chart: Base, theme: Union[str, Dict] = "", key=None):
    """Display echarts chart from pyecharts instance
    :param chart: pyecharts instance
    :param theme: prebuilt theme or object
    :param key:
    :return: chart
    """

    def default(o):
        """Copied from pyecharts' rendering to keep it's JS placeholder ^^"
        """
        if isinstance(o, (datetime.date, datetime.datetime)):
            return o.isoformat()
        if isinstance(o, JsCode):
            return (
                o.replace("\\n|\\t", "")
                .replace(r"\\n", "\n")
                .replace(r"\\t", "\t")
                .js_code
            )
        if isinstance(o, BasicOpts):
            if isinstance(o.opts, Sequence):
                return [remove_key_with_none_value(item) for item in o.opts]
            else:
                return remove_key_with_none_value(o.opts)

    options = json.dumps(chart.get_options(), default=default, ignore_nan=True)
    return _component_func(
        options=json.loads(options), theme=theme, key=key, default=None
    )
