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

`st.echarts_chart` accepts as arguments :
* **options** as a dictionary of objects
* **theme** as a prebuilt theme or object 

Check `examples/` folder for examples.

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
