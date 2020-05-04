# Streamlit - ECharts

A custom component to run Echarts in Streamlit session !

Based on [echarts-for-react](https://github.com/hustcc/echarts-for-react).

## Install

```shell script
conda create -n streamlit-echarts python=3.7
conda activate streamlit-echarts
pip install streamlit-0.58.0-py2.py3-none-any.whl pyecharts

cd frontend
npm install
```

## Use

`st.echarts_chart` accepts a dictionary of objects in the `options` argument.

Check `examples/app.py` for an example.

## Run development setup

In a terminal :

```
cd frontend
npm run start
```

In another terminal :

```
streamlit run examples/app.py
```
