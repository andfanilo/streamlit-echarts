# Analysis: Streamlit-ECharts Canvas vs SVG Remount/Flicker Behavior

## The Reported Behavior

Users observe a "flicker" when rapidly switching between the `canvas` and `svg` renderers in the `streamlit-echarts` demo app.

## Investigation & Findings

### 1. Incomplete `renderer` Prop Implementation

The first finding is that changing the `renderer` prop (from "canvas" to "svg") in the frontend component _currently does not actually swap the ECharts renderer_.

ECharts cannot dynamically swap between Canvas and SVG on an active instance. It requires a hard `.dispose()` and a completely fresh `.init()` call to apply the new renderer.

In `frontend/src/index.ts`, the `renderer` is read from `data` and passed to `echarts.init()` when the chart is first created:

```typescript
if (!state.chart || state.chart.isDisposed()) {
  state.chart = echarts.init(container, themeName, { renderer });
}
```

However, there is no logic to track if the `renderer` prop has changed on subsequent renders, and therefore no logic to `dispose()` the chart and re-initialize it. Thus, the DOM remains perfectly stable (a single Canvas element) under normal circumstances, and the chart does not natively remount.

### 2. The Cause of the Flicker

If the DOM is stable and the chart isn't natively remounting, why does it flicker when users spam the radio button?

This is a side-effect of Streamlit's architecture, specifically how it handles rapid, interrupted render cycles:

- When a user clicks a Streamlit widget, Python begins a rerun.
- If the user clicks the widget again _before_ the first rerun finishes, Streamlit aborts the first rerun and starts a new one immediately.
- During these rapid, aborted cycles, Streamlit's React frontend can sometimes perform a hard DOM replacement of the element holding the component.

When Streamlit replaces the `parentElement` in the DOM:

1. Our `weakMap` loses its reference to the component state.
2. The component is "unmounted", triggering our `Cleanup` function.
3. Streamlit inserts a brand new container.
4. `EchartsRenderer` is called with this new container. Our `getOrCreateInstanceState` creates a fresh, empty state.
5. A fresh ECharts instance is initialized via `echarts.init()`.
6. ECharts applies the options and **replays the initial entry animation** (e.g., bars growing from the X-axis).

**Conclusion:** The flicker is the ECharts entry animation playing because Streamlit aggressively unmounted and remounted the entire component wrapper due to rapid widget interaction. It is not an inadvertent resize, but a true remount of the component container.

## Recommendations for Fixing

1. **Add Proper Renderer Change Logic:**
   We need to track the `renderer` prop just like we track the `theme` prop. If the `renderer` changes between renders, we must:
   - Call `state.chart.dispose()`
   - Set `state.chart = null`
     This will force the component to re-initialize a fresh chart with the correct renderer type.

2. **Force `setOption` After Re-Init:**
   When we dispose and re-init a chart (because of a theme or renderer change), we _must_ forcefully call `.setOption()` on the new chart instance, even if the user's `options` dictionary hasn't changed.
   Currently, the component uses a memoized `getOptionsGenerator` that only returns `hasChanged: true` if the deep-serialization of the options changed. If only the renderer changed, `hasChanged` is `false`, and `setOption` is skipped, resulting in a blank chart.
   We must track if a re-initialization occurred during the current render frame and force the application of `state.getOptions(options).data`.

3. **Update Observers:**
   The `ResizeObserver` and `IntersectionObserver` currently capture the initial `state.chart` in their closure. If the chart is disposed and recreated, they still hold a reference to the old disposed chart. They should be updated to access `state.chart` dynamically so they always resize the active instance.
