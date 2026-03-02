export const JS_PLACEHOLDER = "--x_x--0_0--";

/**
 * Evaluate a JsCode-wrapped string to its resulting value.
 * Strings containing `--x_x--0_0--` markers are extracted and evaluated via
 * `new Function()`. The optional `scope` object injects named bindings into
 * the evaluated code (e.g. `{ echarts }` makes `echarts.*` available).
 * Returns the evaluated result (function, object, primitive) or the original
 * string if evaluation fails or no markers are present.
 * @param s string potentially containing JsCode markers
 * @param scope named bindings injected into the eval scope
 * @returns evaluated value, or original string on failure
 */
export function evalJsCode(
  s: string,
  scope: Record<string, unknown> = {},
): unknown {
  if (typeof s !== "string" || !s.includes(JS_PLACEHOLDER)) {
    return s;
  }

  const parts = s.split(JS_PLACEHOLDER);
  if (parts.length >= 3) {
    const funcStr = parts[1].trim();
    const keys = Object.keys(scope);
    const values = keys.map((k) => scope[k]);
    try {
      return new Function(...keys, `"use strict"; return (${funcStr})`)(
        ...values,
      );
    } catch (e) {
      console.error("JsCode evaluation failed:", e);
      return s;
    }
  }
  return s;
}
