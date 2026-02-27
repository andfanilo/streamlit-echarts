---
name: using-streamlit-layouts
description: Structuring Streamlit app layouts. Use when placing content in sidebars, columns, containers, or dialogs. Covers sidebar usage, column limits, horizontal containers, dialogs, and bordered cards.
license: Apache-2.0
---

# Streamlit layout

How you structure your app affects usability more than you think.

## Sidebar: navigation + global filters only

The sidebar should only contain navigation and app-level filters. Main content goes in the main area.

```python
# GOOD
with st.sidebar:
    date_range = st.date_input("Date range")
    region = st.selectbox("Region", ["All", "US", "EU", "APAC"])
    st.caption("App v1.2.3")
```

```python
# BAD: Too much content in sidebar
with st.sidebar:
    st.title("Dashboard")
    st.dataframe(df)  # Don't put main content here
    st.bar_chart(data)
```

**What goes in sidebar:**
- Global filters (date range, user selection, region)
- App info (version, feedback link)

**What stays out:**
- Main content, charts, tables, results

## Columns: max 4, set alignment

Don't use too many columns—they get cramped.

```python
# GOOD
col1, col2 = st.columns(2)

# Custom widths (ratios)
col1, col2 = st.columns([2, 1])  # 2:1 ratio

# OK with alignment
cols = st.columns(4, vertical_alignment="center")

# BAD: Too many, cramped
col1, col2, col3, col4, col5, col6 = st.columns(6)
```

## Horizontal containers for button groups

Use `st.container(horizontal=True)` instead of columns for button groups:

```python
with st.container(horizontal=True):
    st.button("Cancel")
    st.button("Save")
    st.button("Submit")
```

## Aligning elements

Use `horizontal_alignment` on containers to position elements:

```python
# Center elements
with st.container(horizontal_alignment="center"):
    st.image("logo.png", width=200)
    st.title("Welcome")

# Right-align elements
with st.container(horizontal_alignment="right"):
    st.button("Settings", icon=":material/settings:")

# Distribute evenly (great for button groups)
with st.container(horizontal=True, horizontal_alignment="distribute"):
    st.button("Cancel")
    st.button("Save")
    st.button("Submit")
```

Options: `"left"` (default), `"center"`, `"right"`, `"distribute"`

## Bordered containers

Use `border=True` on containers for visual grouping. See `building-streamlit-dashboards` for dashboard-specific patterns like KPI cards.

```python
with st.container(border=True):
    st.subheader("Section title")
    st.write("Grouped content here")
```

## Tabs

Organize content into switchable views:

```python
tab1, tab2 = st.tabs(["Chart", "Data"])

with tab1:
    st.line_chart(data)
with tab2:
    st.dataframe(df)
```

## Expander

Collapsible sections for secondary content:

```python
with st.expander("See details"):
    st.write("Hidden content here")
    st.code("print('hello')")
```

## Empty and placeholders

`st.empty()` creates a single-element placeholder that can be updated or cleared:

```python
placeholder = st.empty()

# Update the placeholder
placeholder.text("Loading...")
result = load_data()
placeholder.dataframe(result)

# Clear it
placeholder.empty()
```

## Popover

Click to reveal content:

```python
with st.popover("Settings"):
    st.checkbox("Dark mode")
    st.slider("Font size", 10, 24)
```

## Dialogs for focused interactions

Use `@st.dialog` for UI that doesn't need to be always visible:

```python
@st.dialog("Confirm deletion")
def confirm_delete(item_name):
    st.write(f"Are you sure you want to delete **{item_name}**?")
    if st.button("Delete", type="primary"):
        delete_item(item_name)
        st.rerun()

if st.button("Delete item"):
    confirm_delete("My Document")
```

**Key points:**
- Dialogs rerun independently from the main script
- Use `st.session_state` to pass widget values from the dialog to the main app
- Call `st.rerun()` to close dialog and refresh main app
- Use `dismissible=False` for forced actions
- `st.sidebar` is not supported inside dialogs

**When to use dialogs:**
- Confirmation prompts
- Settings panels
- Forms that don't need to be always visible

## Spacing

Control spacing between elements with `gap` on containers:

```python
# Remove spacing for tight list-like UIs
with st.container(gap=None, border=True):
    for item in items:
        st.checkbox(item.text)

# Explicit gap sizes
with st.container(gap="small"):
    ...
```

Add vertical space with `st.space`:

```python
st.space("small")   # Small gap
st.space("medium")  # Medium gap
st.space("large")   # Large gap
st.space(50)        # Custom pixels
```

## Width and height

Control element sizing:

```python
# Stretch to fill available space (equal height columns)
cols = st.columns(2)
with cols[0].container(border=True, height="stretch"):
    st.line_chart(data)
with cols[1].container(border=True, height="stretch"):
    st.dataframe(df)

# Shrink to content size
st.container(width="content")

# Fixed pixel sizes
st.container(height=300)
```

## References

- [st.columns](https://docs.streamlit.io/develop/api-reference/layout/st.columns)
- [st.container](https://docs.streamlit.io/develop/api-reference/layout/st.container)
- [st.sidebar](https://docs.streamlit.io/develop/api-reference/layout/st.sidebar)
- [st.tabs](https://docs.streamlit.io/develop/api-reference/layout/st.tabs)
- [st.expander](https://docs.streamlit.io/develop/api-reference/layout/st.expander)
- [st.popover](https://docs.streamlit.io/develop/api-reference/layout/st.popover)
- [st.empty](https://docs.streamlit.io/develop/api-reference/layout/st.empty)
- [st.dialog](https://docs.streamlit.io/develop/api-reference/execution-flow/st.dialog)
