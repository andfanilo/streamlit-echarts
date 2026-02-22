const JS_PLACEHOLDER = "--x_x--0_0--";

/**
 * If string can be evaluated as a Function, return activated function. Else return string.
 * @param s string to evaluate to function
 * @returns Function if can be evaluated as one, else input string
 */
export function evalStringToFunction(s: string): Function | string {
  const funcReg = new RegExp(
    `${JS_PLACEHOLDER}\\s*(function\\s*.*)\\s*${JS_PLACEHOLDER}`,
  );
  const match = funcReg.exec(s);
  if (match) {
    const funcStr = match[1];
    return new Function("return " + funcStr)();
  }
  return s;
}
