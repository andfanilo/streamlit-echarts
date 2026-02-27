# Smart Bi-directional Interactions

**Roadmap ID:** `smart_interactions` | **GitHub Issue:** #58
**Complexity:** 5/10 | **Utility:** 9/10

## Goal

Replace the single `chart_event` trigger bucket with a **structured selection API** aligned with `st.plotly_chart`'s `on_select` / `selection_mode` conventions — giving Python callers a familiar, typed interface that matches Streamlit's native charting patterns.

## Current State

Today the component has one communication channel:

```
JS: setTriggerValue("chart_event", result)   →   Python: on_change callback
```

- `events` dict maps ECharts event names to user-supplied JS strings
- The JS function's return value is forwarded verbatim as `chart_event`
- No structured selection (click, brush, lasso) — users must parse raw ECharts params
- No debouncing — high-frequency events like `brushSelected` fire on every pixel

## Alignment with `st.plotly_chart`

This design mirrors the selection API of `st.plotly_chart` so that Streamlit users encounter a familiar pattern:

| Concept | `st.plotly_chart` | `st_echarts` (this plan) |
|---------|-------------------|--------------------------|
| Opt-in to selection | `on_select="rerun"` or `on_select=callable` | `on_select="rerun"` or `on_select=callable` |
| Opt-out (default) | `on_select="ignore"` | `on_select="ignore"` |
| Selection modes | `selection_mode=("points","box","lasso")` | `selection_mode=("points","box","lasso")` |
| Return shape | `result.selection.points`, `.box`, `.lasso`, `.point_indices` | Same structure |

## Design

### 1. Unified `on_select` Trigger (matches `st.plotly_chart`)

Instead of separate `on_click` / `on_brush` callbacks, use a **single** `on_select` parameter — exactly like `st.plotly_chart`:

- `"ignore"` (default) — no selection events, no rerun. Backward-compatible.
- `"rerun"` — Streamlit reruns on selection; `st_echarts()` returns a dict with `.selection`.
- `callable` — Streamlit reruns and calls the function as a callback before the rest of the app.

Selection uses **CCv2 state** (not a trigger): `setStateValue("selection", selectionPayload)`. This is critical — state persists across reruns caused by other widgets, matching `st.plotly_chart`'s behavior where selections survive unrelated interactions. A trigger would reset to `None` on every rerun, making the selection useless in multi-widget apps.

The existing `events` / `on_change` channel remains untouched as a **trigger** for raw ECharts event forwarding (fire-and-forget semantics are correct there).

| Channel | Type | Fires on | Python param |
|---|---|---|---|
| `chart_event` | trigger | User-defined `events` dict | `on_change` (unchanged) |
| `selection` | **state** | Click on data point, box selection, lasso selection | `on_select` |

### 2. `selection_mode` (matches `st.plotly_chart`)

```python
selection_mode: "points" | "box" | "lasso" | Iterable[str]
```

- Default: `("points", "box", "lasso")` — all modes active (same as plotly)
- `"points"` — click/tap on individual data points
- `"box"` — rectangular brush selection
- `"lasso"` — freeform polygon brush selection
- Only takes effect when `on_select` is not `"ignore"`

The frontend maps these to ECharts brush types:
- `"points"` → wires `click` listener (no brush toolbox needed)
- `"box"` → `brush.type: "rect"` + toolbox button
- `"lasso"` → `brush.type: "polygon"` + toolbox button

### 3. Structured Selection Payload (mirrors `st.plotly_chart`)

```python
# result.selection (returned when on_select != "ignore")
selection = {
    "points": [                           # always present, may be empty
        {
            "point_index": int,           # index within the series data array
            "series_index": int,          # which series (≈ curve_number in plotly)
            "series_name": str | None,    # series.name if set
            "x": Any,                     # x-axis / category value
            "y": Any,                     # y-axis value
            "value": Any,                 # raw data value (for non-cartesian charts)
            "name": str | None,           # data point name if applicable
        }
    ],
    "point_indices": list[int],           # flat list of all selected point_index values
    "box": [                              # list of box selection areas (empty if unused)
        {
            "x_range": [float, float],    # [min, max] on x-axis
            "y_range": [float, float],    # [min, max] on y-axis
        }
    ],
    "lasso": [                            # list of lasso selection areas (empty if unused)
        {
            "coordinates": [[float, float], ...],  # polygon vertices
        }
    ],
}
```

**Key alignment choices:**
- `points` always includes all selected points (from clicks, box, and lasso) — same as plotly
- `point_indices` is a flat convenience list — same as plotly
- `box` and `lasso` are **lists** of area dicts (not single dicts) — same as plotly
- When nothing is selected, all lists are empty (not `None`) — same as plotly

### 4. Python API Changes

```python
def st_echarts(
    options: dict,
    theme: str | dict = "",
    events: dict[str, str] | None = None,
    height: str = "300px",
    width: str = "100%",
    renderer: str = "canvas",
    map: Map | None = None,
    key: str | None = None,
    # --- existing ---
    on_change: Callable[[], None] | None = None,
    # --- new (aligned with st.plotly_chart) ---
    on_select: Literal["ignore", "rerun"] | Callable[[], None] = "ignore",
    selection_mode: str | Iterable[str] = ("points", "box", "lasso"),
):
```

**Return value changes:**
- When `on_select="ignore"`: returns current `component_value` (backward-compatible)
- When `on_select="rerun"` or callable: returns an object with `.selection` attribute containing the selection dict
- Selection persists in `st.session_state[key].selection` automatically (CCv2 state, not trigger)
- Pass `default={"selection": EMPTY_SELECTION}` to ensure `.selection` is always a valid dict from the first render — never `None` or `AttributeError`
- **`st.form` note:** selection triggers immediately regardless of form context (same as `st.plotly_chart`) — document this behavior

### 5. Frontend Architecture

New file: `frontend/src/selection.ts`

```
selection.ts
├── SelectionData                                     # TypeScript type
├── EMPTY_SELECTION: SelectionData                    # { points:[], point_indices:[], box:[], lasso:[] }
├── transformClickToSelection(params): SelectionData  # ECharts click → SelectionData
├── transformBrushToSelection(params, chart): SelectionData  # brush batch → SelectionData
├── buildBrushOption(selectionMode: string[]): EChartsOption # toolbox+brush config
```

New memoized generator in `index.ts`: `setSelectionGenerator()` — manages click/brushSelected/brushEnd listener lifecycle, similar to `setEventsGenerator`.

### 6. Debouncing Strategy

`brushSelected` fires continuously during drag. Approach:

- Use `brushEnd` (fires once on mouse-up) instead of `brushSelected` for the trigger
- `brushEnd` doesn't carry data directly — read `chart.getOption().brush` areas + replay selection lookup via `chart.dispatchAction({ type: 'brush', areas })` or traverse `chart.getOption().series[i].data` manually
- Alternative: debounce `brushSelected` with a 150ms trailing timer, cancel on new event

**Recommendation:** Use `brushEnd` + manual data lookup. Simpler, no timer management, and the payload is always complete.

---

## Implementation Challenges

### Challenge 1: CCv2 State/Callback Registration for `on_select`

**Problem:** Using `setStateValue("selection", ...)` requires a matching `on_selection_change=...` callback and `default={"selection": ...}` in the mount call. When `on_select="ignore"`, we must not register the callback, the default, or wire any listeners.

**Mitigation:** Python only passes `on_selection_change=...` and `default={"selection": EMPTY_SELECTION}` when `on_select != "ignore"`. Pass a boolean `selectionActive: true/false` down via `data` so the frontend knows whether to call `setStateValue("selection", ...)` and wire listeners at all.

```python
mount_kwargs = {}
if on_select != "ignore":
    callback = on_select if callable(on_select) else lambda: None
    mount_kwargs["on_selection_change"] = callback
    mount_kwargs["default"] = {"selection": EMPTY_SELECTION}

data={
    ...,
    "selectionActive": on_select != "ignore",
    "selectionMode": list(selection_mode),  # ["points", "box", "lasso"]
}
```

### Challenge 2: `brushEnd` Carries No Data

**Problem:** ECharts `brushEnd` event only signals that the user finished dragging. It does not include the selected data points — only `brushSelected` does. But `brushSelected` fires on every drag frame.

**Mitigation:** Two-phase approach:
1. Listen to `brushSelected` — cache the latest payload in a local variable (no trigger fired)
2. Listen to `brushEnd` — read the cached `brushSelected` payload, transform it, fire `setTriggerValue("brush", ...)`

This gives us the complete data from `brushSelected` but only triggers a Streamlit rerun on `brushEnd`. Must clear the cache after firing to prevent stale replays.

### Challenge 3: Brush Toolbox Injection Without Clobbering User Options

**Problem:** When `selection_mode` includes `"box"` or `"lasso"`, we need to inject `toolbox.feature.brush` and `brush` config into the ECharts options. But the user may already have their own toolbox config. Using `notMerge: true` (current behavior for options) would wipe user toolbox items.

**Mitigation:** Apply brush config as a **separate** `setOption()` call with `notMerge: false` (merge mode) after the main options apply. This overlays brush config onto whatever the user already set. Must be careful:
- Only call this secondary `setOption` when `selectionMode` includes `"box"` or `"lasso"`
- Track whether brush was previously injected so we can remove it (set `brush: []`, `toolbox.feature.brush: undefined`) when selection is deactivated
- When `selectionMode` is `["points"]` only, no brush toolbox is needed — only click listeners

### Challenge 4: Circular Rerun Loops

**Problem:** When Python reacts to a selection trigger, it typically updates `options` (e.g., highlights selected points). This causes the component to re-render, which could re-fire the same selection event if listeners aren't carefully managed.

**Mitigation:**
- The memoized `getOptionsGenerator` already prevents re-applying unchanged options — if Python sends the same options back, the chart won't re-render, so events won't re-fire
- For brush: after `setTriggerValue`, do **not** programmatically re-trigger the brush. The brush visual state lives inside ECharts and persists across re-renders
- On the Python side, document that users should guard callbacks:
  ```python
  def on_click():
      sel = st.session_state[key].click
      if sel != st.session_state.get("last_click"):
          st.session_state["last_click"] = sel
          # process...
  ```

### Challenge 5: Multi-Series Data Lookup in Brush Selection

**Problem:** `brushSelected.batch[].selected[seriesIdx].dataIndex` gives indices per series, but to build the `points` array we need the actual data values. We must call `chart.getOption().series[i].data[idx]` — but series data can be:
- A flat array `[1, 2, 3]`
- An array of objects `[{name: "a", value: 1}]`
- A dataset-driven series (no inline `data`, data comes from `dataset.source`)

**Mitigation:** Handle the common cases:
1. If `series[i].data` exists and is indexable, use it directly
2. If the value at index is an object with `name`/`value`, extract those
3. If `series[i].data` is absent (dataset mode), look up `chart.getOption().dataset[datasetIndex].source` using the series' `datasetIndex` (defaults to `0`) and resolve the row by `dataIndex`. This covers common pyecharts/DataFrame workflows where data lives in `dataset.source` rather than inline `series.data`
4. If dataset lookup also fails (e.g. dynamic transforms), fall back to `dataIndex`-only (no value/name) and document the limitation
5. Add a `raw` field to `SelectionData.points[]` that includes the unprocessed ECharts data entry for advanced users

### Challenge 6: Click on Empty Area vs Data Element

**Problem:** ECharts fires `click` both for data elements and for the chart background. For data elements, `params.dataIndex` is a number. For background clicks, the event has `params.componentType === "series"` but no `dataIndex`, or it might not fire at all depending on chart type.

**Mitigation:** Check `params.dataIndex != null` to distinguish data clicks from background clicks. When no data element is hit, call `setStateValue("selection", EMPTY_SELECTION)`. This clears the persisted selection state, ensuring Python-side `st.session_state[key].selection` reflects the deselection. Users detect deselection by checking `len(selection["points"]) == 0`. The same applies when the user clicks "Clear Brush" in the toolbox — the `brushSelected` event fires with empty batches, which our transform maps to `EMPTY_SELECTION`.

### Challenge 7: TypeScript Type Safety — State vs Trigger Keys

**Problem:** The current `EchartsStateShape` is typed as `{ chart_event?: any }`. We now need both a trigger key (`chart_event`) and a state key (`selection`). CCv2's `setStateValue` and `setTriggerValue` share the same generic type parameter, so both keys must be in the same shape type.

**Mitigation:** Expand the state shape:

```typescript
export type EchartsStateShape = {
  chart_event?: any;        // trigger — fire-and-forget for user events
  selection?: SelectionData; // state — persists across reruns
};
```

Both `setStateValue("selection", ...)` and `setTriggerValue("chart_event", ...)` are valid against this type. The runtime `selectionActive` flag controls whether the frontend writes to `selection`.

### Challenge 8: Event Listener Cleanup Ordering

**Problem:** The selection generator adds `click`/`brushEnd`/`brushSelected` listeners. The events generator adds user-defined listeners. If a user also defines `click` in their `events` dict, both systems try to bind to the same ECharts event name.

**Mitigation:** Selection listeners take priority — they fire the structured `select` trigger. User `events` listeners fire independently through `chart_event`. Since `chart.on("click", handler)` supports multiple handlers (additive, not replacing), both can coexist. Document that the user's `events.click` JS function runs alongside the built-in selection — they get both the raw `chart_event` trigger and the structured `select` trigger.

### Challenge 9: Testing Brush Interactions

**Problem:** Brush interactions involve complex multi-event sequences (mousedown → mousemove × N → mouseup → brushSelected → brushEnd). Unit-testing this with mocked ECharts is fragile.

**Mitigation:**
- Unit-test `transformBrushToSelection` and `transformClickToSelection` as pure functions with fixture data (no chart instance needed)
- Unit-test the cache-and-fire logic of the selection generator with mocked `chart.on` (capture handlers, call them in sequence)
- E2E-test actual brush interactions via Playwright (already set up in the project) — this is the only reliable way to test the full brush flow

---

### Challenge 10: Pixel-to-Axis Coordinate Transformation for Box/Lasso

**Problem:** ECharts brush `areas` report coordinates in **pixel space** by default. The plan's `SelectionData.box` promises `x_range`/`y_range` as axis values, but we never specified how to convert. Without conversion, Python users get useless pixel numbers they can't use to filter DataFrames.

**Mitigation:** Use `chart.convertFromPixel` after brush completes:

```typescript
const [xMin, yMin] = chart.convertFromPixel({ gridIndex: 0 }, [area.range[0], area.range[1]]);
const [xMax, yMax] = chart.convertFromPixel({ gridIndex: 0 }, [area.range[2], area.range[3]]);
```

Complications:
- **Multi-grid charts:** `convertFromPixel` requires a `gridIndex` (or `xAxisIndex`/`yAxisIndex`). For single-grid charts (vast majority), default to `gridIndex: 0`. For multi-grid, use `area.panelId` from the brush event to infer which grid the selection belongs to.
- **Category axes:** `convertFromPixel` returns a numeric index for category axes, not the category label. Must additionally look up `chart.getOption().xAxis[i].data[index]` to get the label string.
- **Geo/map charts:** `convertFromPixel({geoIndex: 0}, [px, py])` returns `[lon, lat]` — same API, different coord finder. Support this alongside cartesian grids since `Map` is a common `st_echarts` use case.
- **Polar/other non-cartesian:** `convertFromPixel` doesn't apply to all coordinate systems. For unsupported types, include raw pixel coords and document the limitation.
- **Lasso polygons:** Each vertex in `area.coordRange` needs individual conversion — iterate all points.

**Scope decision:** Support cartesian (grid) and geo/map charts with axis-value conversion. For other non-cartesian types, fall back to raw pixel coords with a `"coordinate_system": "pixel"` flag in the payload so users know.

### Challenge 11: `on_select="rerun"` Return Value vs Existing Return

**Problem:** Today `st_echarts` returns the raw `component_value` (the `chart_event` trigger payload or `{}`). With `on_select="rerun"`, we want to return an object with a `.selection` attribute — matching `st.plotly_chart`'s pattern. But this changes the return type.

**Mitigation:** Since we use `setStateValue("selection", ...)`, CCv2 automatically exposes `result.selection` as an attribute on the returned object — the key name already matches plotly's convention. No wrapper class needed. When `on_select="ignore"`, the `selection` key isn't registered, so `result` won't have `.selection` (backward-compatible). When `on_select` is active, `default={"selection": EMPTY_SELECTION}` ensures `result.selection` is always a valid dict from the first render.

---

## File Changes

| File | Change |
|------|--------|
| `frontend/src/selection.ts` | **New.** `SelectionData` type, `transformClickToSelection`, `transformBrushToSelection`, `buildBrushOption`, `EMPTY_SELECTION` |
| `frontend/src/index.ts` | Add `setSelectionGenerator` (uses `setStateValue`), expand `EchartsDataShape` with `selectionActive`/`selectionMode`, wire selection in renderer lifecycle, expand `EchartsStateShape` with `selection` |
| `streamlit_echarts/__init__.py` | Add `on_select`, `selection_mode` params; conditionally register `on_selection_change` callback + `default={"selection": EMPTY_SELECTION}`; pass `selectionActive`/`selectionMode` in `data` |
| `frontend/src/selection.test.ts` | **New.** Unit tests for transform functions and brush option builder |
| `frontend/src/index.test.ts` | Add tests for `setSelectionGenerator` |
| `tests/test_init.py` | Add tests for `on_select`/`selection_mode` params, data serialization, return type |

## Implementation Order

1. `selection.ts` — pure transform functions + types (testable in isolation)
2. `selection.test.ts` — unit tests for transforms
3. `index.ts` — `setSelectionGenerator` + renderer wiring
4. `index.test.ts` — generator tests
5. `__init__.py` — Python API: `on_select`, `selection_mode`, return wrapper
6. `test_init.py` — Python tests
7. E2E smoke test for click + brush selection

