import json

import streamlit as st
from pyecharts import options as opts
from pyecharts.charts import Bar
from pyecharts.charts import Timeline
from pyecharts.faker import Faker

st.header("Hello ECharts !")
st.register_component("echarts_chart", url="http://localhost:3001")

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

options_json = option = {
    "xAxis": {
        "type": "category",
        "data": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
    },
    "yAxis": {"type": "value"},
    "series": [{"data": [820, 932, 901, 934, 1290, 1330, 1320], "type": "line"}],
}
st.echarts_chart(options=options_json)

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

st.subheader("With data zoom")
data = [
    ["14.616", "7.241", "0.896"],
    ["3.958", "5.701", "0.955"],
    ["2.768", "8.971", "0.669"],
    ["9.051", "9.710", "0.171"],
    ["14.046", "4.182", "0.536"],
    ["12.295", "1.429", "0.962"],
    ["4.417", "8.167", "0.113"],
    ["0.492", "4.771", "0.785"],
    ["7.632", "2.605", "0.645"],
    ["14.242", "5.042", "0.368"],
]
option_datazoom = {
    "xAxis": {"type": "value"},
    "yAxis": {"type": "value"},
    "dataZoom": [{"type": "slider", "start": 10, "end": 60}],
    "series": [
        {
            "type": "scatter",
            "itemStyle": {"opacity": 0.8},
            "symbolSize": [float(val[2]) * 40 for val in data],
            "data": data,
        }
    ],
}
st.echarts_chart(options=option_datazoom)
