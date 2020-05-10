import streamlit as st

st.header("Hello ECharts !")
st.register_component("echarts_chart", url="http://localhost:3001")

st.subheader("Basic rendering")
st.echarts_chart(
    options={
        "xAxis": {
            "type": "category",
            "data": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        },
        "yAxis": {"type": "value"},
        "series": [{"data": [820, 932, 901, 934, 1290, 1330, 1320], "type": "line"}],
    }
)

st.subheader("Customized pie chart")
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
st.echarts_chart(options=pie_options)

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
