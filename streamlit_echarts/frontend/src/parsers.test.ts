import { describe, expect, test } from "vitest";
import { evalStringToFunction } from "./parsers";

const JS_PLACEHOLDER = "--x_x--0_0--";

describe("evalStringToFunction", () => {
  test("returns a plain string unchanged", () => {
    expect(evalStringToFunction("hello")).toBe("hello");
  });

  test("returns an empty string unchanged", () => {
    expect(evalStringToFunction("")).toBe("");
  });

  test("evaluates a wrapped function and returns a callable", () => {
    const wrapped = `${JS_PLACEHOLDER}function(x) { return x * 2; }${JS_PLACEHOLDER}`;
    const result = evalStringToFunction(wrapped);
    expect(typeof result).toBe("function");
    expect((result as Function)(3)).toBe(6);
  });

  test("wrapped function can access its arguments", () => {
    const wrapped = `${JS_PLACEHOLDER}function(params) { return params.name; }${JS_PLACEHOLDER}`;
    const fn = evalStringToFunction(wrapped) as Function;
    expect(fn({ name: "click" })).toBe("click");
  });

  test("returns string unchanged when only start placeholder is present", () => {
    const partial = `${JS_PLACEHOLDER}function(x) { return x; }`;
    const result = evalStringToFunction(partial);
    expect(typeof result).toBe("string");
  });

  test("returns string unchanged when only end placeholder is present", () => {
    const partial = `function(x) { return x; }${JS_PLACEHOLDER}`;
    const result = evalStringToFunction(partial);
    expect(typeof result).toBe("string");
  });
});
