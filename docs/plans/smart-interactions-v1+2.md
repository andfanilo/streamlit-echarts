# Smart Interactions: Implementation Comparison (V1 vs V2)

This document provides a detailed technical comparison of two architectural approaches for implementing Streamlit-native bidirectional interactions in `streamlit-echarts`. These approaches were preserved in `feat/native-v1-backup` and `feat/native-v2-backup`.

## Executive Summary

| Feature | V1 (Basic Pipeline) | V2 (Data-Centric) |
| :--- | :--- | :--- |
| **Primary Goal** | Prove CCv2 connectivity | Enable actionable data analysis |
| **Coordinate System** | Pixel-based (View space) | Data-based (Model space) |
| **Series Mapping** | Flat list (Ambiguous) | Series-aware (Keyed by Name) |
| **Data Architecture** | `series.data` only | `series.data` + `dataset.source` |
| **Event Stability** | Global unbind (Risky) | Surgical unbind (Safe) |

---

## Technical Breakdown

### 1. Selection Fidelity & Utility
The most critical difference lies in *what* data is sent back to Python.

*   **V1 (Pixel-bound):** Returns raw `x/y` coordinates relative to the chart container. To use this data, a Python developer would have to manually re-calculate which data point corresponds to those pixels—a nearly impossible task given varying screen sizes and paddings.
*   **V2 (Data-bound):** Uses the ECharts `convertFromPixel` API. It translates the user's click/brush into the actual values of the axes (e.g., translating a click at `x: 450` into the date `"2024-05-12"`). This makes the selection immediately "actionable" for filtering DataFrames in Python.

### 2. Multi-Series Ambiguity
*   **V1:** Returns a single list of indices. If a chart has three series, Python cannot distinguish if "index 5" refers to Series A, B, or C.
*   **V2:** Structures the payload as a dictionary keyed by series name (e.g., `{"Sales": [1, 2, 3], "Profit": [1]}`). This maintains the data hierarchy across the bridge.

### 3. Support for ECharts "Dataset" API
Modern ECharts configurations prefer the `dataset` property over putting data directly into `series`.
*   **V1:** Only checks `series.data`. If a user employs the `dataset` pattern, the selection returns empty.
*   **V2:** Implements a `resolveDataItem` helper that traverses both `series.data` and `dataset.source`, ensuring compatibility with all ECharts data-loading patterns.

### 4. Lifecycle & Event Handling
Both versions use the CCv2 `WeakMap` for instance safety, but differ in robustness:
*   **V1:** Calls `chart.off('click')`, which removes **every** click handler on the chart. If a user provided a custom JS callback for a click via the `events` parameter, the selection logic would accidentally delete it.
*   **V2:** Maintains references to its specific handler functions and uses `chart.off('click', handlerReference)`. This allows the component's internal selection logic to coexist with user-defined JS events.

---

## Architectural Pros & Cons

### feat/native-v1-backup
**Pros:**
- Lightweight and easy to maintain.
- Modular `selection.ts` utility.
- Lower overhead for simple "point-and-click" use cases where only indices matter.

**Cons:**
- **Brittle:** High risk of "event stomping" on complex charts.
- **Incomplete:** Fails on charts using the `dataset` API.
- **Low Value:** Returning pixels forces the heavy lifting onto the end-user.

### feat/native-v2-backup
**Pros:**
- **High Fidelity:** Returns actual axis values and data coordinates.
- **Production Ready:** Handles Geo charts and multiple coordinate systems (Grids).
- **Safe:** Surgical event unbinding prevents interference with user JS.
- **Future Proof:** Fully supports the `dataset` API.

**Cons:**
- **Complexity:** Significant increase in TypeScript logic within `selection.ts`.
- **API Surface:** The Python-side `selection_mode` defaults are more opinionated.

---

## Conclusion

`feat/native-v2-backup` represents the "Smart Interactions" vision described in the roadmap. While V1 successfully established the CCv2 plumbing, V2 provides the high-quality data bridge necessary for building professional, interactive data applications. Future work should build upon the **V2 architecture**, focusing on adding "Named Triggers" to further refine the Python-side developer experience.
