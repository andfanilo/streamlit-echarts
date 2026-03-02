export const JS_PLACEHOLDER = "--x_x--0_0--";

/**
 * If string can be evaluated as a Function, return activated function. Else return string.
 * Supports both classic `function` syntax and arrow functions.
 * @param s string to evaluate to function
 * @returns Function if can be evaluated as one, else input string
 */
export function evalStringToFunction(
  s: string,
  echartsLib?: object,
): Function | string {
  if (typeof s !== "string" || !s.includes(JS_PLACEHOLDER)) {
    return s;
  }

  const parts = s.split(JS_PLACEHOLDER);
  if (parts.length >= 3) {
    const funcStr = parts[1].trim();
    try {
      return new Function("echarts", `"use strict"; return (${funcStr})`)(
        echartsLib,
      );
    } catch (e) {
      console.error("JsCode evaluation failed:", e);
      return s;
    }
  }
  return s;
}
