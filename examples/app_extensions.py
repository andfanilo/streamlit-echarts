import streamlit as st

from pyecharts import options as opts
from pyecharts.charts import Liquid
from streamlit_echarts import st_echarts
from streamlit_echarts import st_pyecharts

def main():
    with st.echo("below"):
        options = {
            "series": [{
                "type": 'liquidFill',
                "data": [0.5, 0.4, 0.3],
                "color": ['red', '#0f0', 'rgb(0, 0, 255)'],
                "itemStyle": {
                    "opacity": 0.6
                },
                "emphasis": {
                    "itemStyle": {
                        "opacity": 0.9
                    }
                }
            }]
        }
        st_echarts(options)

        
        c = (
            Liquid()
            .add("lq", [0.6, 0.7])
            .set_global_opts(title_opts=opts.TitleOpts(title="Liquid-基本示例"))
        )
        st_pyecharts(c)

if __name__ == "__main__":
    main()