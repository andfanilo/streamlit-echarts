import json

import streamlit as st
from pyecharts import options as opts
from pyecharts.charts import Bar

st.header("Hello ECharts !")
st.register_component("echarts_chart", url="http://localhost:3001")

b = (
    Bar()
    .add_xaxis(["Microsoft", "Amazon", "IBM", "Oracle", "Google", "Alibaba"])
    .add_yaxis("2017-2018 Revenue in (billion $)", [21.2, 20.4, 10.3, 6.08, 4, 2.2])
    .set_global_opts(
        title_opts=opts.TitleOpts(
            title="Top cloud providers 2018", subtitle="2017-2018 Revenue"
        )
    )
)
options = json.loads(b.dump_options())
st.echarts_chart(options=options, theme="dark")

st.echarts_chart(
    options=options,
    theme={
        "backgroundColor": "#f4cccc",
        "textStyle": {"color": "rgba(255, 0, 0, 0.8)"},
    },
)
