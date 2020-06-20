# Streamlit - ECharts

A custom component to run Echarts in Streamlit session.

It's basically a Streamlit wrapper over [echarts-for-react](https://github.com/hustcc/echarts-for-react).

![](./img/demo.gif)

## Install

```shell script
pip install pyecharts simplejson  # <-- optional, if you need to use st_pyecharts
pip install -i https://test.pypi.org/simple/ --no-deps streamlit-echarts
```

## Run

```shell script
streamlit run examples/app.py
```

### Usage

Check `examples/` folder for examples.

This library provides 2 functions to display echarts :
* `st_echarts` to display charts from echarts json options as Python dicts (check the [official examples](https://echarts.apache.org/examples/en/index.html))
* `st_pyecharts` to display charts from Pyecharts instances (check the [official examples](https://gallery.pyecharts.org/#/))
* `JsCode` util class (directly extracted from Pyecharts !) to format JsCode.

## Development 

### Install

* JS side

```shell script
cd frontend
npm install
```

* Python side 

```shell script
conda create -n streamlit-echarts python=3.7
conda activate streamlit-echarts
pip install pyecharts simplejson streamlit-0.61.0-py2.py3-none-any.whl 
pip install -e .
```

### Run

* JS side

```shell script
cd frontend
npm run start
```

* Python side

```shell script
streamlit run examples/app.py
```

## Caveats

### Theme definition

* Defining the theme in Pyecharts when instantiating chart like `Bar(init_opts=opts.InitOpts(theme=ThemeType.LIGHT))` 
does not work, you need to call theme in `st_pyecharts(c, theme=ThemeType.LIGHT)`.

### On Javascript functions 

Pyecharts uses `JsCode` to indicate javascript code, so in the custom component we parse every value in options
looking the specific `JsCode` placeholder and parse those as a JS function.

As such if you want to pass JS function as strings from Python args, use the `JsCode` module to wrap code with this placeholder :
* In Python dict, wrap with placeholder by calling `JsCode(function).jscode`.
``` 
series: [
    {
        type: 'scatter', // this is scatter chart
        itemStyle: {
            opacity: 0.8
        },
        symbolSize: JsCode("function (val) { return val[2] * 40;}").js_code,
        data: [["14.616","7.241","0.896"],["3.958","5.701","0.955"],["2.768","8.971","0.669"],["9.051","9.710","0.171"],["14.046","4.182","0.536"],["12.295","1.429","0.962"],["4.417","8.167","0.113"],["0.492","4.771","0.785"],["7.632","2.605","0.645"],["14.242","5.042","0.368"]]
    }
]
```
* In Pyecharts, JsCode automatically calls `.jscode` when dumping options.
```
.set_series_opts(
        label_opts=opts.LabelOpts(
            position="right",
            formatter=JsCode(
                "function(x){return Number(x.data.percent * 100).toFixed() + '%';}"
            ),
        )
    )
``` 

To implement [Events and Actions in ECharts](https://echarts.apache.org/en/tutorial.html#Events%20and%20Actions%20in%20ECharts)
you should directly integrate in the React custom component for now so we don't try to parse JS coming from Python.

### Using pyecharts with st.html

While this package provides a `st_pyecharts` method, if you're using `pyecharts` you can directly embed your pyecharts visualization inside `st.html` 
by passing the output of the chart's `.render_embed()`.

```python
from pyecharts.charts import Bar
from pyecharts import options as opts
import streamlit as st

c = (Bar()
    .add_xaxis(["Microsoft", "Amazon", "IBM", "Oracle", "Google", "Alibaba"])
    .add_yaxis('2017-2018 Revenue in (billion $)', [21.2, 20.4, 10.3, 6.08, 4, 2.2])
    .set_global_opts(title_opts=opts.TitleOpts(title="Top cloud providers 2018", subtitle="2017-2018 Revenue"),
                     toolbox_opts=opts.ToolboxOpts())
    .render_embed() # generate a local HTML file
)
st.html(c, width=1000, height=1000)
```

Using `st_pyecharts` is still something you would want if you need to change data regularly 
without remounting the component. 