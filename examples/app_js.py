import datetime
from typing import Sequence

import simplejson as json
import streamlit as st
from pyecharts import options as opts
from pyecharts.charts import Bar
from pyecharts.charts.base import Base
from pyecharts.commons.utils import JsCode
from pyecharts.commons.utils import remove_key_with_none_value
from pyecharts.faker import Faker
from pyecharts.options.series_options import BasicOpts


ec = st.declare_component(url="http://localhost:3001")


def default(o):
    """Copied from pyecharts' rendering to keep it's JS placeholder ^^"
    """
    if isinstance(o, (datetime.date, datetime.datetime)):
        return o.isoformat()
    if isinstance(o, JsCode):
        return (
            o.replace("\\n|\\t", "").replace(r"\\n", "\n").replace(r"\\t", "\t").js_code
        )
    if isinstance(o, BasicOpts):
        if isinstance(o.opts, Sequence):
            return [remove_key_with_none_value(item) for item in o.opts]
        else:
            return remove_key_with_none_value(o.opts)


@ec
def wrapper(f, chart: Base, theme: str = "", key=None):
    options = json.dumps(chart.get_options(), default=default, ignore_nan=True)
    return f(options=json.loads(options), theme=theme, key=key, default=None)


st.register_component("echarts_chart", ec)

color_function = """
        function (params) {
            if (params.value > 0 && params.value < 50) {
                return 'red';
            } else if (params.value > 50 && params.value < 100) {
                return 'blue';
            }
            return 'green';
        }
        """
c = (
    Bar()
    .add_xaxis(Faker.choose())
    .add_yaxis(
        "商家A",
        Faker.values(),
        itemstyle_opts=opts.ItemStyleOpts(color=JsCode(color_function)),
    )
    .add_yaxis(
        "商家B",
        Faker.values(),
        itemstyle_opts=opts.ItemStyleOpts(color=JsCode(color_function)),
    )
    .add_yaxis(
        "商家C",
        Faker.values(),
        itemstyle_opts=opts.ItemStyleOpts(color=JsCode(color_function)),
    )
    .set_global_opts(title_opts=opts.TitleOpts(title="Bar-自定义柱状颜色"))
)
st.echarts_chart(c)
