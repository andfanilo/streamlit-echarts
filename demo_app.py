import json
import random
from random import randint
from streamlit_echarts import JsCode
from streamlit_echarts import st_echarts

import pandas as pd
import streamlit as st
from pyecharts import options as opts
from pyecharts.charts import Bar
from pyecharts.charts import Geo
from pyecharts.charts import Liquid
from pyecharts.charts import Timeline
from pyecharts.charts import WordCloud
from pyecharts.faker import Faker
from pyecharts.globals import ThemeType


def main():
    ST_PAGES = {
        "Basic line chart": render_basic_line,
        "Basic area chart": render_basic_area,
        "Stacked area chart": render_stacked_area,
        "Mixed line and bar": render_mixed_line_bar,
        "Custom pie chart": render_custom_pie,
        "Effect scatter chart": render_effect_scatter,
        "Calendar heatmap": render_calendar_heatmap,
        "Basic treemap": render_treemap,
        "Datazoom": render_datazoom,
        "Dataset": render_dataset,
        "Map": render_map,
        "Click event": render_event,
        "Liquidfill": render_liquid,
        "Wordcloud": render_wordcloud,
    }

    PY_ST_PAGES = {
        "Basic bar chart": render_bar_py,
        "Custom themes": render_custom_py,
        "Filter with legend": render_filter_legend_py,
        "Vertical datazoom": render_vertical_datazoom_py,
        "Timeline": render_timeline_py,
        "Chart with randomization": render_randomize_py,
        "JsCode coloring": render_js_py,
        "Map": render_map_py,
        "Liquidfill": render_liquid_py,
        "Wordcloud": render_wordcloud_py,
    }

    st.title("Hello ECharts !")
    st.sidebar.header("Configuration")

    select_lang = st.sidebar.selectbox(
        "Choose your preferred API:", ("echarts", "pyecharts")
    )

    if select_lang == "echarts":
        page = st.sidebar.selectbox("Choose an example", options=list(ST_PAGES.keys()))
        ST_PAGES[page]()
    if select_lang == "pyecharts":
        page = st.sidebar.selectbox(
            "Choose an example", options=list(PY_ST_PAGES.keys())
        )
        PY_ST_PAGES[page]()


def render_basic_line():
    with st.echo("below"):
        options = {
            "xAxis": {
                "type": "category",
                "data": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
            },
            "yAxis": {"type": "value"},
            "series": [
                {"data": [820, 932, 901, 934, 1290, 1330, 1320], "type": "line"}
            ],
        }
        st_echarts(
            options=options,
            height="400px",
        )
        st_echarts(
            options=options,
            height="400px",
            theme="dark",
        )


def render_basic_area():
    with st.echo("below"):
        options = {
            "xAxis": {
                "type": "category",
                "boundaryGap": False,
                "data": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
            },
            "yAxis": {"type": "value"},
            "series": [
                {
                    "data": [820, 932, 901, 934, 1290, 1330, 1320],
                    "type": "line",
                    "areaStyle": {},
                }
            ],
        }
        st_echarts(options=options)


def render_stacked_area():
    with st.echo("below"):
        options = {
            "title": {"text": "堆叠区域图"},
            "tooltip": {
                "trigger": "axis",
                "axisPointer": {
                    "type": "cross",
                    "label": {"backgroundColor": "#6a7985"},
                },
            },
            "legend": {
                "data": ["邮件营销", "联盟广告", "视频广告", "直接访问", "搜索引擎"]
            },
            "toolbox": {"feature": {"saveAsImage": {}}},
            "grid": {"left": "3%", "right": "4%", "bottom": "3%", "containLabel": True},
            "xAxis": [
                {
                    "type": "category",
                    "boundaryGap": False,
                    "data": ["周一", "周二", "周三", "周四", "周五", "周六", "周日"],
                }
            ],
            "yAxis": [{"type": "value"}],
            "series": [
                {
                    "name": "邮件营销",
                    "type": "line",
                    "stack": "总量",
                    "areaStyle": {},
                    "data": [120, 132, 101, 134, 90, 230, 210],
                },
                {
                    "name": "联盟广告",
                    "type": "line",
                    "stack": "总量",
                    "areaStyle": {},
                    "data": [220, 182, 191, 234, 290, 330, 310],
                },
                {
                    "name": "视频广告",
                    "type": "line",
                    "stack": "总量",
                    "areaStyle": {},
                    "data": [150, 232, 201, 154, 190, 330, 410],
                },
                {
                    "name": "直接访问",
                    "type": "line",
                    "stack": "总量",
                    "areaStyle": {},
                    "data": [320, 332, 301, 334, 390, 330, 320],
                },
                {
                    "name": "搜索引擎",
                    "type": "line",
                    "stack": "总量",
                    "label": {"normal": {"show": True, "position": "top"}},
                    "areaStyle": {},
                    "data": [820, 932, 901, 934, 1290, 1330, 1320],
                },
            ],
        }
        st_echarts(options)


def render_mixed_line_bar():
    with st.echo("below"):
        options = {
            "tooltip": {
                "trigger": "axis",
                "axisPointer": {"type": "cross", "crossStyle": {"color": "#999"}},
            },
            "toolbox": {
                "feature": {
                    "dataView": {"show": True, "readOnly": False},
                    "magicType": {"show": True, "type": ["line", "bar"]},
                    "restore": {"show": True},
                    "saveAsImage": {"show": True},
                }
            },
            "legend": {"data": ["蒸发量", "降水量", "平均温度"]},
            "xAxis": [
                {
                    "type": "category",
                    "data": [
                        "1月",
                        "2月",
                        "3月",
                        "4月",
                        "5月",
                        "6月",
                        "7月",
                        "8月",
                        "9月",
                        "10月",
                        "11月",
                        "12月",
                    ],
                    "axisPointer": {"type": "shadow"},
                }
            ],
            "yAxis": [
                {
                    "type": "value",
                    "name": "水量",
                    "min": 0,
                    "max": 250,
                    "interval": 50,
                    "axisLabel": {"formatter": "{value} ml"},
                },
                {
                    "type": "value",
                    "name": "温度",
                    "min": 0,
                    "max": 25,
                    "interval": 5,
                    "axisLabel": {"formatter": "{value} °C"},
                },
            ],
            "series": [
                {
                    "name": "蒸发量",
                    "type": "bar",
                    "data": [
                        2.0,
                        4.9,
                        7.0,
                        23.2,
                        25.6,
                        76.7,
                        135.6,
                        162.2,
                        32.6,
                        20.0,
                        6.4,
                        3.3,
                    ],
                },
                {
                    "name": "降水量",
                    "type": "bar",
                    "data": [
                        2.6,
                        5.9,
                        9.0,
                        26.4,
                        28.7,
                        70.7,
                        175.6,
                        182.2,
                        48.7,
                        18.8,
                        6.0,
                        2.3,
                    ],
                },
                {
                    "name": "平均温度",
                    "type": "line",
                    "yAxisIndex": 1,
                    "data": [
                        2.0,
                        2.2,
                        3.3,
                        4.5,
                        6.3,
                        10.2,
                        20.3,
                        23.4,
                        23.0,
                        16.5,
                        12.0,
                        6.2,
                    ],
                },
            ],
        }
        st_echarts(options)


def render_custom_pie():
    with st.echo("below"):
        pie_options = {
            "backgroundColor": "#2c343c",
            "title": {
                "text": "Customized Pie",
                "left": "center",
                "top": 20,
                "textStyle": {"color": "#ccc"},
            },
            "tooltip": {"trigger": "item", "formatter": "{a} <br/>{b} : {c} ({d}%)"},
            "visualMap": {
                "show": False,
                "min": 80,
                "max": 600,
                "inRange": {"colorLightness": [0, 1]},
            },
            "series": [
                {
                    "name": "Source of interview",
                    "type": "pie",
                    "radius": "55%",
                    "center": ["50%", "50%"],
                    "data": [
                        {"value": 235, "name": "Video Ad"},
                        {"value": 274, "name": "Affiliate Ad"},
                        {"value": 310, "name": "Email marketing"},
                        {"value": 335, "name": "Direct access"},
                        {"value": 400, "name": "Search engine"},
                    ],
                    "roseType": "radius",
                    "label": {"color": "rgba(255, 255, 255, 0.3)"},
                    "labelLine": {
                        "lineStyle": {"color": "rgba(255, 255, 255, 0.3)"},
                        "smooth": 0.2,
                        "length": 10,
                        "length2": 20,
                    },
                    "itemStyle": {
                        "color": "#c23531",
                        "shadowBlur": 200,
                        "shadowColor": "rgba(0, 0, 0, 0.5)",
                    },
                    "animationType": "scale",
                    "animationEasing": "elasticOut",
                }
            ],
        }
        st_echarts(options=pie_options)


def render_effect_scatter():
    with st.echo("below"):
        options = {
            "xAxis": {"scale": True},
            "yAxis": {"scale": True},
            "series": [
                {
                    "type": "effectScatter",
                    "symbolSize": 20,
                    "data": [[161.2, 51.6], [167.5, 59]],
                },
                {
                    "type": "scatter",
                    "data": [
                        [161.2, 51.6],
                        [167.5, 59.0],
                        [159.5, 49.2],
                        [157.0, 63.0],
                        [155.8, 53.6],
                        [170.0, 59.0],
                        [159.1, 47.6],
                        [166.0, 69.8],
                        [176.2, 66.8],
                        [160.2, 75.2],
                        [172.5, 55.2],
                        [170.9, 54.2],
                        [172.9, 62.5],
                        [153.4, 42.0],
                        [160.0, 50.0],
                        [176.5, 71.8],
                        [164.4, 55.5],
                        [160.7, 48.6],
                        [174.0, 66.4],
                        [163.8, 67.3],
                    ],
                },
            ],
        }
        st_echarts(options)


def render_calendar_heatmap():
    with st.echo("below"):

        def get_virtual_data(year):
            date_list = pd.date_range(
                start=f"{year}-01-01", end=f"{year + 1}-01-01", freq="D"
            )
            return [[d.strftime("%Y-%m-%d"), randint(1, 10000)] for d in date_list]

        options = {
            "title": {"top": 30, "left": "center", "text": "2016年某人每天的步数"},
            "tooltip": {},
            "visualMap": {
                "min": 0,
                "max": 10000,
                "type": "piecewise",
                "orient": "horizontal",
                "left": "center",
                "top": 65,
                "textStyle": {"color": "#000"},
            },
            "calendar": {
                "top": 120,
                "left": 30,
                "right": 30,
                "cellSize": ["auto", 13],
                "range": "2016",
                "itemStyle": {"borderWidth": 0.5},
                "yearLabel": {"show": False},
            },
            "series": {
                "type": "heatmap",
                "coordinateSystem": "calendar",
                "data": get_virtual_data(2016),
            },
        }
        st_echarts(options)


def render_treemap():
    with st.echo("below"):
        options = {
            "series": [
                {
                    "type": "treemap",
                    "data": [
                        {
                            "name": "nodeA",
                            "value": 10,
                            "children": [
                                {"name": "nodeAa", "value": 4},
                                {"name": "nodeAb", "value": 6},
                            ],
                        },
                        {
                            "name": "nodeB",
                            "value": 20,
                            "children": [
                                {
                                    "name": "nodeBa",
                                    "value": 20,
                                    "children": [{"name": "nodeBa1", "value": 20}],
                                }
                            ],
                        },
                    ],
                }
            ]
        }
        st_echarts(options)


def render_datazoom():
    with st.echo("below"):
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
        option_js = {
            "xAxis": {"type": "value"},
            "yAxis": {"type": "value"},
            "dataZoom": [{"type": "slider", "start": 10, "end": 60}],
            "series": [
                {
                    "type": "scatter",
                    "itemStyle": {"opacity": 0.8},
                    "symbolSize": JsCode(
                        """function (val) {  return val[2] * 40; }"""
                    ).js_code,
                    "data": data,
                }
            ],
        }
        st_echarts(options=option_js)


def render_dataset():
    with st.echo("below"):
        options = {
            "legend": {},
            "tooltip": {},
            "dataset": {
                "source": [
                    ["product", "2015", "2016", "2017"],
                    ["Matcha Latte", 43.3, 85.8, 93.7],
                    ["Milk Tea", 83.1, 73.4, 55.1],
                    ["Cheese Cocoa", 86.4, 65.2, 82.5],
                    ["Walnut Brownie", 72.4, 53.9, 39.1],
                ]
            },
            "xAxis": {"type": "category"},
            "yAxis": {},
            "series": [{"type": "bar"}, {"type": "bar"}, {"type": "bar"}],
        }
        st_echarts(options, renderer="svg")


def render_map():
    with st.echo("below"):
        options = {
            "backgroundColor": "#404a59",
            "title": {
                "text": "全国主要城市空气质量",
                "subtext": "data from PM25.in",
                "sublink": "http://www.pm25.in",
                "left": "center",
                "textStyle": {"color": "#fff"},
            },
            "tooltip": {"trigger": "item"},
            "legend": {
                "orient": "vertical",
                "top": "bottom",
                "left": "right",
                "data": ["pm2.5"],
                "textStyle": {"color": "#fff"},
            },
            "visualMap": {
                "min": 0,
                "max": 300,
                "splitNumber": 5,
                "color": ["#d94e5d", "#eac736", "#50a3ba"],
                "textStyle": {"color": "#fff"},
            },
            "geo": {
                "map": "china",
                "label": {"emphasis": {"show": False}},
                "itemStyle": {
                    "normal": {"areaColor": "#323c48", "borderColor": "#111"},
                    "emphasis": {"areaColor": "#2a333d"},
                },
            },
        }
        st_echarts(options)


def render_event():
    with st.echo("below"):
        st.markdown("Click on chart elements")
        options = {
            "xAxis": {
                "data": ["shirt", "cardign", "chiffon shirt", "pants", "heels", "socks"]
            },
            "yAxis": {},
            "series": [
                {"name": "sales", "type": "bar", "data": [5, 20, 36, 10, 10, 20]}
            ],
        }
        events = {"click": "function(params, echarts) {alert('click detection');}"}
        st_echarts(options, events=events)


def render_liquid():
    with st.echo("below"):
        options = {
            "series": [
                {
                    "type": "liquidFill",
                    "data": [0.5, 0.4, 0.3],
                    "color": ["red", "#0f0", "rgb(0, 0, 255)"],
                    "itemStyle": {"opacity": 0.6},
                    "emphasis": {"itemStyle": {"opacity": 0.9}},
                }
            ]
        }
        st_echarts(options)


def render_wordcloud():
    with st.echo("below"):
        options = {
            "tooltip": {},
            "series": [
                {
                    "type": "wordCloud",
                    "gridSize": 2,
                    "sizeRange": [12, 50],
                    "rotationRange": [-90, 90],
                    "shape": "pentagon",
                    "width": 600,
                    "height": 400,
                    "drawOutOfBound": True,
                    "emphasis": {
                        "textStyle": {"shadowBlur": 10, "shadowColor": "#333"}
                    },
                    "data": [
                        {
                            "name": "Sam S Club",
                            "value": 10000,
                            "textStyle": {"color": "black"},
                            "emphasis": {"textStyle": {"color": "red"}},
                        },
                        {"name": "Macys", "value": 6181},
                        {"name": "Amy Schumer", "value": 4386},
                        {"name": "Jurassic World", "value": 4055},
                        {"name": "Charter Communications", "value": 2467},
                        {"name": "Chick Fil A", "value": 2244},
                        {"name": "Planet Fitness", "value": 1898},
                        {"name": "Pitch Perfect", "value": 1484},
                        {"name": "Express", "value": 1112},
                        {"name": "Home", "value": 965},
                        {"name": "Johnny Depp", "value": 847},
                        {"name": "Lena Dunham", "value": 582},
                        {"name": "Lewis Hamilton", "value": 555},
                        {"name": "KXAN", "value": 550},
                        {"name": "Mary Ellen Mark", "value": 462},
                        {"name": "Farrah Abraham", "value": 366},
                        {"name": "Rita Ora", "value": 360},
                        {"name": "Serena Williams", "value": 282},
                        {"name": "NCAA baseball tournament", "value": 273},
                        {"name": "Point Break", "value": 265},
                    ],
                }
            ],
        }
        st_echarts(options)


def render_bar_py():
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
        st_echarts(options=json.loads(b.dump_options()))


def render_custom_py():
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
        st_echarts(options=json.loads(b.dump_options()), theme=ThemeType.DARK)

        st_echarts(
            options=json.loads(b.dump_options()),
            theme={
                "backgroundColor": "#f4cccc",
                "textStyle": {"color": "rgba(255, 0, 0, 0.8)"},
            },
        )


def render_filter_legend_py():
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
                title_opts=opts.TitleOpts(
                    title="Bar-动画配置基本示例", subtitle="我是副标题"
                )
            )
        )
        st_echarts(options=json.loads(c.dump_options()))


def render_vertical_datazoom_py():
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
        st_echarts(options=json.loads(c.dump_options()), height="400px")


def render_timeline_py():
    with st.echo("below"):
        x = Faker.choose()
        tl = Timeline()
        for i in range(2015, 2020):
            bar = (
                Bar()
                .add_xaxis(x)
                .add_yaxis("商家A", Faker.values())
                .add_yaxis("商家B", Faker.values())
                .set_global_opts(
                    title_opts=opts.TitleOpts("某商店{}年营业额".format(i))
                )
            )
            tl.add(bar, "{}年".format(i))
        st_echarts(options=json.loads(tl.dump_options()))


def render_randomize_py():
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
        st_echarts(
            options=json.loads(b.dump_options()), key="echarts"
        )  # Add key argument to not remount component at every Streamlit run
        st.button("Randomize data")


def render_js_py():
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
        st_echarts(options=json.loads(c.dump_options()))


def render_map_py():
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
        st_echarts(options=json.loads(g.dump_options()))


def render_liquid_py():
    with st.echo("below"):
        c = (
            Liquid()
            .add("lq", [0.6, 0.7])
            .set_global_opts(title_opts=opts.TitleOpts(title="Liquid-基本示例"))
        )
        st_echarts(options=json.loads(c.dump_options()))


def render_wordcloud_py():
    with st.echo("below"):
        data = [
            ("生活资源", "999"),
            ("供热管理", "888"),
            ("供气质量", "777"),
            ("生活用水管理", "688"),
            ("一次供水问题", "588"),
            ("交通运输", "516"),
            ("城市交通", "515"),
            ("环境保护", "483"),
            ("房地产管理", "462"),
            ("城乡建设", "449"),
            ("社会保障与福利", "429"),
            ("社会保障", "407"),
            ("文体与教育管理", "406"),
            ("公共安全", "406"),
            ("公交运输管理", "386"),
            ("出租车运营管理", "385"),
            ("供热管理", "375"),
            ("市容环卫", "355"),
            ("自然资源管理", "355"),
            ("粉尘污染", "335"),
            ("噪声污染", "324"),
            ("土地资源管理", "304"),
            ("物业服务与管理", "304"),
            ("医疗卫生", "284"),
            ("粉煤灰污染", "284"),
            ("占道", "284"),
            ("供热发展", "254"),
            ("农村土地规划管理", "254"),
            ("生活噪音", "253"),
            ("供热单位影响", "253"),
            ("城市供电", "223"),
            ("房屋质量与安全", "223"),
            ("大气污染", "223"),
            ("房屋安全", "223"),
            ("文化活动", "223"),
            ("拆迁管理", "223"),
            ("公共设施", "223"),
            ("供气质量", "223"),
            ("供电管理", "223"),
            ("燃气管理", "152"),
            ("教育管理", "152"),
            ("医疗纠纷", "152"),
            ("执法监督", "152"),
            ("设备安全", "152"),
            ("政务建设", "152"),
            ("县区、开发区", "152"),
            ("宏观经济", "152"),
            ("教育管理", "112"),
            ("社会保障", "112"),
            ("生活用水管理", "112"),
            ("物业服务与管理", "112"),
            ("分类列表", "112"),
            ("农业生产", "112"),
            ("二次供水问题", "112"),
            ("城市公共设施", "92"),
            ("拆迁政策咨询", "92"),
            ("物业服务", "92"),
            ("物业管理", "92"),
            ("社会保障保险管理", "92"),
            ("低保管理", "92"),
            ("文娱市场管理", "72"),
            ("城市交通秩序管理", "72"),
            ("执法争议", "72"),
            ("商业烟尘污染", "72"),
            ("占道堆放", "71"),
            ("地上设施", "71"),
            ("水质", "71"),
            ("无水", "71"),
            ("供热单位影响", "71"),
            ("人行道管理", "71"),
            ("主网原因", "71"),
            ("集中供热", "71"),
            ("客运管理", "71"),
            ("国有公交（大巴）管理", "71"),
            ("工业粉尘污染", "71"),
            ("治安案件", "71"),
            ("压力容器安全", "71"),
            ("身份证管理", "71"),
            ("群众健身", "41"),
            ("工业排放污染", "41"),
            ("破坏森林资源", "41"),
            ("市场收费", "41"),
            ("生产资金", "41"),
            ("生产噪声", "41"),
            ("农村低保", "41"),
            ("劳动争议", "41"),
            ("劳动合同争议", "41"),
            ("劳动报酬与福利", "41"),
            ("医疗事故", "21"),
            ("停供", "21"),
            ("基础教育", "21"),
            ("职业教育", "21"),
            ("物业资质管理", "21"),
            ("拆迁补偿", "21"),
            ("设施维护", "21"),
            ("市场外溢", "11"),
            ("占道经营", "11"),
            ("树木管理", "11"),
            ("农村基础设施", "11"),
            ("无水", "11"),
            ("供气质量", "11"),
            ("停气", "11"),
            ("市政府工作部门（含部门管理机构、直属单位）", "11"),
            ("燃气管理", "11"),
            ("市容环卫", "11"),
            ("新闻传媒", "11"),
            ("人才招聘", "11"),
            ("市场环境", "11"),
            ("行政事业收费", "11"),
            ("食品安全与卫生", "11"),
            ("城市交通", "11"),
            ("房地产开发", "11"),
            ("房屋配套问题", "11"),
            ("物业服务", "11"),
            ("物业管理", "11"),
            ("占道", "11"),
            ("园林绿化", "11"),
            ("户籍管理及身份证", "11"),
            ("公交运输管理", "11"),
            ("公路（水路）交通", "11"),
            ("房屋与图纸不符", "11"),
            ("有线电视", "11"),
            ("社会治安", "11"),
            ("林业资源", "11"),
            ("其他行政事业收费", "11"),
            ("经营性收费", "11"),
            ("食品安全与卫生", "11"),
            ("体育活动", "11"),
            ("有线电视安装及调试维护", "11"),
            ("低保管理", "11"),
            ("劳动争议", "11"),
            ("社会福利及事务", "11"),
            ("一次供水问题", "11"),
        ]

        c = (
            WordCloud()
            .add(series_name="热点分析", data_pair=data, word_size_range=[6, 66])
            .set_global_opts(
                title_opts=opts.TitleOpts(
                    title="热点分析",
                    title_textstyle_opts=opts.TextStyleOpts(font_size=23),
                ),
                tooltip_opts=opts.TooltipOpts(is_show=True),
            )
        )
        st_echarts(options=json.loads(c.dump_options()))


if __name__ == "__main__":
    st.set_page_config(page_title="Streamlit Echarts Demo", page_icon=":tada:")
    main()
