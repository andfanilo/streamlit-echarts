---
name: displaying-streamlit-data
description: Displaying charts, dataframes, and metrics in Streamlit. Use when visualizing data, configuring dataframe columns, or adding sparklines to metrics. Covers native charts, Altair, and column configuration.
license: Apache-2.0
---

# Streamlit charts & data

Present data clearly.

## Choosing display elements

| Element | Use Case |
|---------|----------|
| `st.dataframe` | Interactive exploration, sorting, filtering |
| `st.data_editor` | User-editable tables |
| `st.table` | Static display, no interaction needed |
| `st.metric` | KPIs with delta indicators |
| `st.json` | Structured data inspection |

## Native charts first

Prefer Streamlit's native charts for simple cases.

```python
st.line_chart(df, x="date", y="revenue")
st.bar_chart(df, x="category", y="count")
st.scatter_chart(df, x="age", y="salary")
st.area_chart(df, x="date", y="value")
```

Native charts support additional parameters: `color` for series grouping, `stack` for bar/area stacking, `size` for scatter point sizing, `horizontal` for horizontal bars. See the [chart API reference](https://docs.streamlit.io/develop/api-reference/charts) for full options.

## Human-readable labels

Use clear labels—not column names or abbreviations. Skip `x_label`/`y_label` if the column names are already readable.

```python
# BAD: cryptic column names without labels
st.line_chart(df, x="dt", y="rev")

# GOOD: readable columns, no labels needed
st.line_chart(df, x="date", y="revenue")

# GOOD: cryptic columns, add labels
st.line_chart(df, x="dt", y="rev", x_label="Date", y_label="Revenue")
```

## Altair for complex charts

Use Altair when you need more control. Altair is bundled with Streamlit (no extra install), while Plotly requires an additional package. Pick one and stay consistent throughout your app.

```python
import altair as alt

chart = alt.Chart(df).mark_line().encode(
    x=alt.X("date:T", title="Date"),
    y=alt.Y("revenue:Q", title="Revenue ($)"),
    color="region:N"
)
st.altair_chart(chart)
```

**When to use Altair:**
- Custom axis formatting
- Multiple series with legends
- Interactive tooltips
- Layered visualizations

## Dataframe column configuration

Use `column_config` where it adds value—formatting currencies, showing progress bars, displaying links or images. Don't add config just for labels or tooltips that don't meaningfully improve readability. Works with both `st.dataframe` and `st.data_editor`.

```python
st.dataframe(
    df,
    column_config={
        "revenue": st.column_config.NumberColumn(
            "Revenue",
            format="$%.2f"
        ),
        "completion": st.column_config.ProgressColumn(
            "Progress",
            min_value=0,
            max_value=100
        ),
        "url": st.column_config.LinkColumn("Website"),
        "logo": st.column_config.ImageColumn("Logo"),
        "created_at": st.column_config.DatetimeColumn(
            "Created",
            format="MMM DD, YYYY"
        ),
        "internal_id": None,  # Hide non-essential columns
    },
    hide_index=True,
)
```

**Note on hiding columns:** Setting a column to `None` hides it from the UI, but the data is still sent to the frontend. For truly sensitive data, pre-filter the DataFrame before displaying.

**Dataframe best practices:**
- **Hide useless index:** `hide_index=True`
- **Or make index meaningful:** `df = df.set_index("customer_name")` before displaying
- **Hide internal/technical columns:** Set column to `None` in config (but pre-filter for sensitive data)
- **Use visual column types where they help:** sparklines for trends, progress bars for completion, images for logos

**Column types:**
- `AreaChartColumn` → Area sparklines
- `BarChartColumn` → Bar sparklines
- `CheckboxColumn` → Boolean as checkbox
- `DateColumn` → Date only (no time)
- `DatetimeColumn` → Dates with formatting
- `ImageColumn` → Images
- `JSONColumn` → Display JSON objects
- `LineChartColumn` → Sparkline charts
- `LinkColumn` → Clickable links
- `ListColumn` → Display lists/arrays
- `MultiselectColumn` → Multi-value selection
- `NumberColumn` → Numbers with formatting
- `ProgressColumn` → Progress bars
- `SelectboxColumn` → Editable dropdown
- `TextColumn` → Text with formatting
- `TimeColumn` → Time only (no date)

## Pinned columns

Keep important columns visible while scrolling horizontally:

```python
st.dataframe(
    df,
    column_config={
        "Title": st.column_config.TextColumn(pinned=True),  # Always visible
        "Rating": st.column_config.ProgressColumn(min_value=0, max_value=10),
    },
    hide_index=True,
)
```

## Data editor

Use `st.data_editor` when users need to edit data directly:

```python
edited_df = st.data_editor(
    df,
    num_rows="dynamic",  # Allow adding/deleting rows
    column_config={
        "status": st.column_config.SelectboxColumn(
            "Status",
            options=["pending", "approved", "rejected"]
        ),
    },
)

# React to edits
if not edited_df.equals(df):
    save_changes(edited_df)
```

## JSON display

For structured data inspection. Accepts dicts, lists, or any JSON-serializable object:

```python
st.json({"name": "John", "scores": [95, 87, 92]})
```

## Sparklines in metrics

Add `chart_data` and `chart_type` to metrics for visual context.

```python
values = [700, 720, 715, 740, 762, 755, 780]

st.metric(
    label="Developers",
    value="762k",
    delta="-7.42% (MoM)",
    delta_color="inverse",
    chart_data=values,
    chart_type="line"  # or "bar"
)
```

**Note:** Sparklines only show y-values and ignore x-axis spacing. Use them for evenly-spaced data (like daily or weekly snapshots). For irregularly-spaced time series, use a proper chart instead.

See `building-streamlit-dashboards` for composing metrics into dashboard layouts.

## References

- [st.dataframe](https://docs.streamlit.io/develop/api-reference/data/st.dataframe)
- [st.data_editor](https://docs.streamlit.io/develop/api-reference/data/st.data_editor)
- [st.column_config](https://docs.streamlit.io/develop/api-reference/data/st.column_config)
- [st.metric](https://docs.streamlit.io/develop/api-reference/data/st.metric)
- [st.json](https://docs.streamlit.io/develop/api-reference/data/st.json)
- [st.line_chart](https://docs.streamlit.io/develop/api-reference/charts/st.line_chart)
- [st.bar_chart](https://docs.streamlit.io/develop/api-reference/charts/st.bar_chart)
- [st.altair_chart](https://docs.streamlit.io/develop/api-reference/charts/st.altair_chart)
