# Plan: Modernizing JsCode

## Context
`JsCode` is a utility to pass JavaScript functions from Python to the ECharts frontend. The current implementation relies on a rigid regex and does not support modern JavaScript syntax like arrow functions.

## Objectives
1.  **Support Arrow Functions**: Update the frontend parser to handle `() => ...` syntax.
2.  **Improve Robustness**: Use string splitting instead of complex regex for placeholder extraction.
3.  **Better DX**: Enhance the Python `JsCode` class for easier usage.

## Proposed Changes

### 1. Frontend: `streamlit_echarts/frontend/src/parsers.ts`
Replace the regex-based `evalStringToFunction` with a more flexible implementation.

```typescript
const JS_PLACEHOLDER = "--x_x--0_0--";

export function evalStringToFunction(s: string): Function | string {
  if (typeof s !== "string" || !s.includes(JS_PLACEHOLDER)) {
    return s;
  }

  const parts = s.split(JS_PLACEHOLDER);
  // Expecting [prefix, js_code, suffix]
  if (parts.length >= 3) {
    const funcStr = parts[1].trim();
    try {
      // Function constructor can evaluate both "function() {}" and "() => {}"
      // wrapping in parens to ensure expressions are treated as values
      return new Function(`"use strict"; return (${funcStr})`)();
    } catch (e) {
      console.error("JsCode evaluation failed:", e);
      return s;
    }
  }
  return s;
}
```

### 2. Python: `streamlit_echarts/__init__.py`
Add `__str__` and `__repr__` to the `JsCode` class so it can be used more naturally in strings or during debugging.

```python
class JsCode:
    def __init__(self, js_code: str):
        js_placeholder = "--x_x--0_0--"
        self.js_code = f"{js_placeholder}{js_code}{js_placeholder}"

    def __str__(self):
        return self.js_code

    def __repr__(self):
        return f"JsCode({self.js_code})"
```

### 3. Tests: `streamlit_echarts/frontend/src/parsers.test.ts`
Add test cases for:
- Arrow functions: `(params) => params.value`
- Modern syntax: `params => { return params.name }`
- Multi-line functions.
- A `JsCode`-shaped object `{"js_code": "..."}` passed to `evalStringToFunction` returns the object unchanged (not a function) — documenting that serialization to a plain string is the Python side's responsibility, not the frontend's (see `jscode_serialization_tests` in roadmap).

### 4. Tests: `streamlit_echarts/tests/test_init.py`
Add Python unit tests for `_serialize_options`:
- `JsCode` at the top level of options is replaced with its `.js_code` string.
- `JsCode` nested inside a dict value is replaced.
- `JsCode` inside a list element is replaced.
- Non-`JsCode` values (strings, ints, dicts, lists) pass through unchanged.

## Validation Plan
1.  Run existing vitest suite: `npm run test` (in frontend).
2.  Create a demo script in `e2e_playwright` or update `demo_app.py` to use an arrow function in a tooltip formatter.
3.  Verify the chart renders correctly and the JS function executes.
