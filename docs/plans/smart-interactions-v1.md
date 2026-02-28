# Plan: Smart Event Interactions (CCv2 State Sync)

## Goal
Implement a high-performance, state-aware interaction API for `st_echarts` that mirrors the native `st.plotly_chart` experience, ensuring selection data is persisted in `st.session_state`.

## API Specification

### Python Signature
```python
event = st_echarts(
    options=options,
    on_select="rerun",           # "ignore" (default), "rerun", or Callable
    selection_mode=["points", "box", "lasso"], # Align with st.plotly_chart
    key="my_chart"                # Essential for st.session_state sync
)
```

### Return & State Schema (`event.selection`)
The following structure is stored in `st.session_state[key].selection`:
- `point_indices`: List[int] - Clean list of indices for data filtering.
- `points`: List[dict] - Metadata (index, series, value, name).
- `box`: List[dict] - Rectangular selection ranges (if "box" mode used).
- `lasso`: List[dict] - Polygon path coordinates (if "lasso" mode used).
- `brush`: dict - Raw ECharts brush data (for advanced use cases).

## Implementation Details

### Frontend (TypeScript)
1. **Registry**: A `SMART_PARSERS` object mapping ECharts events to the "Selection" schema.
    - `click` / `selectchanged` -> `points`, `point_indices`.
    - `brush` / `brushEnd` -> `box`, `lasso`, `point_indices`.
2. **State Persistence**: Use **`setStateValue("selection", data)`** to emit events.
    - This ensures the data is registered in `st.session_state[key].selection`.
    - Data persists across app reruns triggered by other widgets.
3. **Throttling**:
    - `click`: Immediate update.
    - `brushEnd`: 200ms debounce to wait for user to finish dragging.

### Backend (Python)
1. **Mount Callable**: Define with `st.components.v2.component`.
2. **Callback Mapping**: Pass the `on_select` choice to the `on_selection_change` parameter.
3. **State Access**: Because `setStateValue` is used, the data is available via `event.selection` AND `st.session_state[key].selection`.

## Success Criteria
- [ ] Selection data persists when other widgets trigger a rerun.
- [ ] `st.session_state[key].selection` is populated correctly.
- [ ] No manual JS string parsing required for standard selection tasks.
