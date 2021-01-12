import streamlit as st

from pyecharts import options as opts
from pyecharts.charts import Liquid
from pyecharts.charts import WordCloud
from streamlit_echarts import JsCode
from streamlit_echarts import st_echarts
from streamlit_echarts import st_pyecharts


def main():
    PAGES = {"Wordcloud": render_wordcloud, "Liquidfill": render_liquid}

    st.title("Hello ECharts extensions!")
    st.sidebar.header("Configuration")
    page = st.sidebar.selectbox("Choose an example", options=list(PAGES.keys()))
    PAGES[page]()


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

        c = (
            Liquid()
            .add("lq", [0.6, 0.7])
            .set_global_opts(title_opts=opts.TitleOpts(title="Liquid-基本示例"))
        )
        st_pyecharts(c)


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
                    title="热点分析", title_textstyle_opts=opts.TextStyleOpts(font_size=23)
                ),
                tooltip_opts=opts.TooltipOpts(is_show=True),
            )
        )
        st_pyecharts(c)


if __name__ == "__main__":
    main()
