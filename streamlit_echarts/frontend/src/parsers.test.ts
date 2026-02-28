import { describe, expect, test } from "vitest";
import { evalStringToFunction, JS_PLACEHOLDER } from "./parsers";

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
    expect(result).toBe(partial);
  });

  test("returns string unchanged when only end placeholder is present", () => {
    const partial = `function(x) { return x; }${JS_PLACEHOLDER}`;
    const result = evalStringToFunction(partial);
    expect(typeof result).toBe("string");
    expect(result).toBe(partial);
  });

  test("evaluates an arrow function with parens", () => {
    const wrapped = `${JS_PLACEHOLDER}(x) => x * 2${JS_PLACEHOLDER}`;
    const result = evalStringToFunction(wrapped);
    expect(typeof result).toBe("function");
    expect((result as Function)(5)).toBe(10);
  });

  test("evaluates an arrow function without parens", () => {
    const wrapped = `${JS_PLACEHOLDER}x => x * 2${JS_PLACEHOLDER}`;
    const result = evalStringToFunction(wrapped);
    expect(typeof result).toBe("function");
    expect((result as Function)(4)).toBe(8);
  });

  test("evaluates an arrow function with block body", () => {
    const wrapped = `${JS_PLACEHOLDER}(params) => { return params.name; }${JS_PLACEHOLDER}`;
    const fn = evalStringToFunction(wrapped) as Function;
    expect(typeof fn).toBe("function");
    expect(fn({ name: "tooltip" })).toBe("tooltip");
  });

  test("returns original string for invalid JS", () => {
    const wrapped = `${JS_PLACEHOLDER}not valid javascript !!!${JS_PLACEHOLDER}`;
    const result = evalStringToFunction(wrapped);
    expect(typeof result).toBe("string");
    expect(result).toBe(wrapped);
  });

  test("evaluates a function that throws at runtime without breaking eval", () => {
    const wrapped = `${JS_PLACEHOLDER}function() { throw new Error("boom"); }${JS_PLACEHOLDER}`;
    const fn = evalStringToFunction(wrapped);
    // eval itself succeeds — the function is valid syntax
    expect(typeof fn).toBe("function");
    // but calling it throws at runtime
    expect(() => (fn as Function)()).toThrow("boom");
  });
});
