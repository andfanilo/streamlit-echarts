import json

import streamlit as st
from pyecharts import options as opts
from pyecharts.charts import Geo
from pyecharts.faker import Faker

from streamlit_echarts import st_echarts

st.subheader("With Visual Map")
g = (
    Geo()
    .add_schema(maptype="china")
    .add("geo", [list(z) for z in zip(Faker.provinces, Faker.values())])
    .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
    .set_global_opts(
        visualmap_opts=opts.VisualMapOpts(), title_opts=opts.TitleOpts(title="Geo-基本示例")
    )
)
options = json.loads(g.dump_options_with_quotes())
st_echarts(options=options)
