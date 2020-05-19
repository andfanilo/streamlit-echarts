import json
import random

import streamlit as st
from pyecharts import options as opts
from pyecharts.charts import Bar
from pyecharts.charts import Timeline
from pyecharts.faker import Faker

st.header("Hello ECharts !")
ec = st.declare_component(url="http://localhost:3001")
st.register_component("echarts_chart", ec)

st.subheader("Basic rendering")
b = (
    Bar()
    .add_xaxis(["Microsoft", "Amazon", "IBM", "Oracle", "Google", "Alibaba"])
    .add_yaxis("2017-2018 Revenue in (billion $)", [21.2, 20.4, 10.3, 6.08, 4, 2.2])
    .set_global_opts(
        title_opts=opts.TitleOpts(
            title="Top cloud providers 2018", subtitle="2017-2018 Revenue"
        ),
        toolbox_opts=opts.ToolboxOpts(),
    )
)
options = json.loads(b.dump_options())
st.echarts_chart(options=options)

st.subheader("With custom theme")
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

st.subheader("With animation")
c = (
    Bar(
        init_opts=opts.InitOpts(
            animation_opts=opts.AnimationOpts(
                animation_delay=1000, animation_easing="elasticOut"
            )
        )
    )
    .add_xaxis(Faker.choose())
    .add_yaxis("商家A", Faker.values())
    .add_yaxis("商家B", Faker.values())
    .set_global_opts(title_opts=opts.TitleOpts(title="Bar-动画配置基本示例", subtitle="我是副标题"))
)
options_animation = json.loads(c.dump_options())
st.echarts_chart(options=options_animation)

st.subheader("With timeline")
x = Faker.choose()
tl = Timeline()
for i in range(2015, 2020):
    bar = (
        Bar()
        .add_xaxis(x)
        .add_yaxis("商家A", Faker.values())
        .add_yaxis("商家B", Faker.values())
        .set_global_opts(title_opts=opts.TitleOpts("某商店{}年营业额".format(i)))
    )
    tl.add(bar, "{}年".format(i))
options_timeline = json.loads(tl.dump_options())
st.echarts_chart(options=options_timeline)

st.subheader("With a button to push random data")
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
st.echarts_chart(
    options=options, key="echarts"
)  # Add key argument to not remount component at every Streamlit run
st.button("Randomize data")
