import json
import random

import streamlit as st
from pyecharts import options as opts
from pyecharts.charts import Bar

st.register_component("echarts_chart", url="http://localhost:3001")

b = (
    Bar()
    .add_xaxis(["Microsoft", "Amazon", "IBM", "Oracle", "Google", "Alibaba"])
    .add_yaxis("2017-2018 Revenue in (billion $)", random.sample(range(100), 10))
    .set_global_opts(
        title_opts=opts.TitleOpts(
            title="Top cloud providers 2018", subtitle="2017-2018 Revenue"
        ),
        toolbox_opts=opts.ToolboxOpts(),
    )
)
options = json.loads(b.dump_options())
st.echarts_chart(options=options, key="echarts")
st.button("Randomize data")
