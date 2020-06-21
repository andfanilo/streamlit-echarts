import pandas as pd
from random import randint
import streamlit as st

from streamlit_echarts import JsCode
from streamlit_echarts import st_echarts


def main():
    PAGES = {
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
    }

    st.title("Hello ECharts !")
    st.sidebar.header("Configuration")
    page = st.sidebar.selectbox("Choose an example", options=list(PAGES.keys()))
    PAGES[page]()


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
            options=options, height="400px",
        )
        st_echarts(
            options=options, height="400px", theme="dark",
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
            "legend": {"data": ["邮件营销", "联盟广告", "视频广告", "直接访问", "搜索引擎"]},
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


if __name__ == "__main__":
    main()
