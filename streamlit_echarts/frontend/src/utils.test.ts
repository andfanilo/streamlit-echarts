import { describe, expect, test } from "vitest";
import deepMap from "./utils";

describe("deepMap", () => {
  test("applies iterator to each value of a flat object", () => {
    const input = { a: "1", b: "2" };
    const result = deepMap(input, (v: string) => v + "!", {});
    expect(result).toEqual({ a: "1!", b: "2!" });
  });

  test("recursively applies iterator to nested objects", () => {
    const input = { a: { b: "1" } };
    const result = deepMap(input, (v: string) => v + "!", {});
    expect(result).toEqual({ a: { b: "1!" } });
  });

  test("returns an empty object for an empty input", () => {
    const result = deepMap({}, (v: string) => v, {});
    expect(result).toEqual({});
  });

  test("processes array values via lodash transform", () => {
    const input = { items: ["a", "b"] };
    const result = deepMap(input, (v: string) => v.toUpperCase(), {});
    expect(result).toEqual({ items: ["A", "B"] });
  });

  test("handles deeply nested objects", () => {
    const input = { a: { b: { c: "deep" } } };
    const result = deepMap(input, (v: string) => v + "!", {});
    expect(result).toEqual({ a: { b: { c: "deep!" } } });
  });

  test("does not mutate the original object", () => {
    const input = { a: "original" };
    deepMap(input, (v: string) => v + "!", {});
    expect(input).toEqual({ a: "original" });
  });
});
