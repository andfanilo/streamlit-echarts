import random

import streamlit as st
from pyecharts import options as opts
from pyecharts.charts import Bar
from pyecharts.charts import Geo
from pyecharts.charts import Timeline
from pyecharts.commons.utils import JsCode
from pyecharts.faker import Faker
from pyecharts.globals import ThemeType

from streamlit_echarts import st_pyecharts


def main():
    PAGES = {
        "Basic bar chart": render_bar,
        "Custom themes": render_custom,
        "Filter with legend": render_filter_legend,
        "Vertical datazoom": render_vertical_datazoom,
        "Timeline": render_timeline,
        "Chart with randomization": render_randomize,
        "JsCode coloring": render_js,
        "Map": render_map,
    }

    st.header("Hello Pyecharts !")
    st.sidebar.header("Configuration")
    page = st.sidebar.selectbox("Choose an example", options=list(PAGES.keys()))
    PAGES[page]()


def render_bar():
    with st.echo("below"):
        b = (
            Bar()
            .add_xaxis(["Microsoft", "Amazon", "IBM", "Oracle", "Google", "Alibaba"])
            .add_yaxis(
                "2017-2018 Revenue in (billion $)", [21.2, 20.4, 10.3, 6.08, 4, 2.2]
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(
                    title="Top cloud providers 2018", subtitle="2017-2018 Revenue"
                ),
                toolbox_opts=opts.ToolboxOpts(),
            )
        )
        st_pyecharts(b)


def render_custom():
    with st.echo("below"):
        b = (
            Bar()
            .add_xaxis(["Microsoft", "Amazon", "IBM", "Oracle", "Google", "Alibaba"])
            .add_yaxis(
                "2017-2018 Revenue in (billion $)", [21.2, 20.4, 10.3, 6.08, 4, 2.2]
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(
                    title="Top cloud providers 2018", subtitle="2017-2018 Revenue"
                )
            )
        )
        st_pyecharts(b, theme=ThemeType.DARK)

        st_pyecharts(
            b,
            theme={
                "backgroundColor": "#f4cccc",
                "textStyle": {"color": "rgba(255, 0, 0, 0.8)"},
            },
        )


def render_filter_legend():
    with st.echo("below"):
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
            .set_global_opts(
                title_opts=opts.TitleOpts(title="Bar-动画配置基本示例", subtitle="我是副标题")
            )
        )
        st_pyecharts(c)


def render_vertical_datazoom():
    with st.echo("below"):
        c = (
            Bar()
            .add_xaxis(Faker.days_attrs)
            .add_yaxis("商家A", Faker.days_values, color=Faker.rand_color())
            .set_global_opts(
                title_opts=opts.TitleOpts(title="Bar-DataZoom（slider-垂直）"),
                datazoom_opts=opts.DataZoomOpts(orient="vertical"),
            )
        )
        st_pyecharts(c, height="400px")


def render_timeline():
    with st.echo("below"):
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
        st_pyecharts(tl)


def render_randomize():
    with st.echo("below"):
        b = (
            Bar()
            .add_xaxis(["Microsoft", "Amazon", "IBM", "Oracle", "Google", "Alibaba"])
            .add_yaxis(
                "2017-2018 Revenue in (billion $)", random.sample(range(100), 10)
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(
                    title="Top cloud providers 2018", subtitle="2017-2018 Revenue"
                ),
                toolbox_opts=opts.ToolboxOpts(),
            )
        )
        st_pyecharts(
            b, key="echarts"
        )  # Add key argument to not remount component at every Streamlit run
        st.button("Randomize data")


def render_js():
    with st.echo("below"):
        st.markdown(
            """Overwrite chart colors with JS. 
        Under 50 : red. Between 50 - 100 : blue. Over 100 : green"""
        )
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
        st_pyecharts(c)


def render_map():
    with st.echo("below"):
        g = (
            Geo()
            .add_schema(maptype="china")
            .add("geo", [list(z) for z in zip(Faker.provinces, Faker.values())])
            .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
            .set_global_opts(
                visualmap_opts=opts.VisualMapOpts(),
                title_opts=opts.TitleOpts(title="Geo-基本示例"),
            )
        )
        st_pyecharts(g)


if __name__ == "__main__":
    main()
