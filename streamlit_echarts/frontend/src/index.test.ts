import { beforeEach, describe, expect, test, vi } from "vitest";

// Mock ECharts and extensions before importing the module under test
vi.mock("echarts", () => ({
  registerTheme: vi.fn(),
  registerMap: vi.fn(),
  init: vi.fn(),
}));
vi.mock("echarts-gl", () => ({}));
vi.mock("echarts-liquidfill", () => ({}));
vi.mock("echarts-wordcloud", () => ({}));

import * as echarts from "echarts";
import {
  getOptionsGenerator,
  setThemeGenerator,
  setEventsGenerator,
} from "./index";

describe("getOptionsGenerator", () => {
  let getOptions: ReturnType<typeof getOptionsGenerator>;

  beforeEach(() => {
    getOptions = getOptionsGenerator();
  });

  test("should return parsed options and hasChanged true on first call", () => {
    const options = { xAxis: { type: "category" as const } };
    const result = getOptions(options);

    expect(result.hasChanged).toBe(true);
    expect(result.data).toEqual({ xAxis: { type: "category" } });
  });

  test("should return hasChanged false for the same options", () => {
    const options = { xAxis: { type: "category" as const } };
    getOptions(options);
    const result = getOptions(options);

    expect(result.hasChanged).toBe(false);
  });

  test("should return hasChanged true for different options", () => {
    getOptions({ xAxis: { type: "category" as const } });
    const result = getOptions({ xAxis: { type: "value" as const } });

    expect(result.hasChanged).toBe(true);
    expect(result.data).toEqual({ xAxis: { type: "value" } });
  });

  test("should evaluate JsCode placeholders via deepMap", () => {
    const options = {
      tooltip: {
        formatter:
          "--x_x--0_0--function (params) { return params.name; }--x_x--0_0--",
      },
    };
    const result = getOptions(options);

    expect(result.hasChanged).toBe(true);
    expect(typeof (result.data as any).tooltip.formatter).toBe("function");
  });
});

describe("setThemeGenerator", () => {
  let setTheme: ReturnType<typeof setThemeGenerator>;
  let container: HTMLDivElement;

  beforeEach(() => {
    vi.mocked(echarts.registerTheme).mockClear();
    setTheme = setThemeGenerator();
    container = document.createElement("div");
    document.body.appendChild(container);
  });

  test("should return themeChanged true on first call with string theme", () => {
    const result = setTheme("dark", container);

    expect(result.themeChanged).toBe(true);
    expect(result.themeName).toBe("dark");
  });

  test("should return themeChanged false for the same theme", () => {
    setTheme("dark", container);
    const result = setTheme("dark", container);

    expect(result.themeChanged).toBe(false);
  });

  test("should register streamlit theme and return themeChanged true", () => {
    const result = setTheme("streamlit", container);

    expect(result.themeChanged).toBe(true);
    expect(result.themeName).toBe("streamlit");
    expect(echarts.registerTheme).toHaveBeenCalledWith(
      "streamlit",
      expect.objectContaining({ color: expect.any(Array) }),
    );
  });

  test("should register custom object theme", () => {
    const customTheme = { color: ["#ff0000"] };
    const result = setTheme(customTheme, container);

    expect(result.themeChanged).toBe(true);
    expect(result.themeName).toBe("custom_theme");
    expect(echarts.registerTheme).toHaveBeenCalledWith(
      "custom_theme",
      customTheme,
    );
  });

  test("should detect change when theme changes from one to another", () => {
    setTheme("dark", container);
    const result = setTheme("light", container);

    expect(result.themeChanged).toBe(true);
    expect(result.themeName).toBe("light");
  });
});

describe("setEventsGenerator", () => {
  let setEvents: ReturnType<typeof setEventsGenerator>;
  let mockChart: any;
  let mockSetTriggerValue: (name: "chart_event", value: any) => void;

  beforeEach(() => {
    setEvents = setEventsGenerator();
    mockChart = {
      on: vi.fn(),
      off: vi.fn(),
    };
    mockSetTriggerValue = vi.fn() as any;
  });

  test("should bind events and return true on first call", () => {
    const onEvents = {
      click:
        "--x_x--0_0--function (params) { return params.name; }--x_x--0_0--",
    };
    const result = setEvents(mockChart, onEvents, mockSetTriggerValue);

    expect(result).toBe(true);
    expect(mockChart.on).toHaveBeenCalledWith("click", expect.any(Function));
  });

  test("should return false when events have not changed", () => {
    const onEvents = {
      click:
        "--x_x--0_0--function (params) { return params.name; }--x_x--0_0--",
    };
    setEvents(mockChart, onEvents, mockSetTriggerValue);
    const result = setEvents(mockChart, onEvents, mockSetTriggerValue);

    expect(result).toBe(false);
  });

  test("should unbind old and bind new events on change", () => {
    const onEvents1 = {
      click:
        "--x_x--0_0--function (params) { return params.name; }--x_x--0_0--",
    };
    const onEvents2 = {
      mouseover:
        "--x_x--0_0--function (params) { return params.value; }--x_x--0_0--",
    };

    setEvents(mockChart, onEvents1, mockSetTriggerValue);
    mockChart.on.mockClear();

    const result = setEvents(mockChart, onEvents2, mockSetTriggerValue);

    expect(result).toBe(true);
    expect(mockChart.off).toHaveBeenCalledWith("click");
    expect(mockChart.on).toHaveBeenCalledWith(
      "mouseover",
      expect.any(Function),
    );
  });

  test("should call setTriggerValue when event handler fires", () => {
    const onEvents = {
      click:
        "--x_x--0_0--function (params) { return params.name; }--x_x--0_0--",
    };
    setEvents(mockChart, onEvents, mockSetTriggerValue);

    // Get the handler that was passed to chart.on
    const handler = mockChart.on.mock.calls[0][1];
    handler({ name: "test-value" });

    expect(mockSetTriggerValue).toHaveBeenCalledWith(
      "chart_event",
      "test-value",
    );
  });
});
