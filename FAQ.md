# FAQ

## Legends or axis labels are clipped / cut off

ECharts renders everything inside its own canvas or SVG element, so clipping
is an ECharts layout concern rather than a CSS issue on the component wrapper.

**Recommended options:**

```python
options = {
    "grid": {
        # Auto-expand the grid margins to contain axis tick labels
        "containLabel": True,
    },
    "tooltip": {
        # Keep tooltips inside the chart area (important for embedded components)
        "confine": True,
    },
    # ... your series, xAxis, yAxis, etc.
}
```

If you have **long legend text**, truncate it explicitly:

```python
options = {
    "legend": {
        "textStyle": {
            "width": 120,
            "overflow": "truncate",
        },
    },
    # ...
}
```

For **rotated axis labels** that extend past the edge, align the boundary
labels inward (ECharts 5.5+):

```python
options = {
    "xAxis": {
        "axisLabel": {
            "rotate": 45,
            "alignMinLabel": "left",
            "alignMaxLabel": "right",
        },
    },
    # ...
}
```

See the [ECharts grid documentation](https://echarts.apache.org/en/option.html#grid)
and [ECharts FAQ](https://echarts.apache.org/en/faq.html) for more details.

## ECharts Toolbox "saveAsImage" fails or causes a rerun

The `saveAsImage` feature in the ECharts toolbox may not work reliably within the Streamlit environment because it tries to trigger a browser download that can be intercepted by Streamlit's routing or iframe security. This often manifests as the chart resetting or the app rerunning without saving the image.

**Recommended workaround:**

Right-click anywhere on the chart canvas and select **"Save Image As..."** from the browser's context menu. This is the most reliable way to save the chart as an image without any additional configuration or potential for app reruns.

For a more robust solution that uses `st.download_button`, see the [screenshot_return](#screenshot_return) item in the roadmap (GitHub issue #55).
