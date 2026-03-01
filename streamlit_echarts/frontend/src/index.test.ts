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
import type { EchartsStateShape } from "./index";
import EchartsRenderer, {
  getOptionsGenerator,
  setThemeGenerator,
  setEventsGenerator,
  setSelectionGenerator,
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
    const formatter = (result.data as any).tooltip.formatter;
    expect(typeof formatter).toBe("function");
    expect(formatter({ name: "bar" })).toBe("bar");
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
  let mockSetTriggerValue: (name: keyof EchartsStateShape, value: any) => void;

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
    expect(mockChart.off).toHaveBeenCalledWith("click", expect.any(Function));
    expect(mockChart.on).toHaveBeenCalledWith(
      "mouseover",
      expect.any(Function),
    );
  });

  test("should call setTriggerValue with the parsed function's return value", () => {
    const onEvents = {
      click:
        "--x_x--0_0--function (params) { return params.name.toUpperCase() + '!'; }--x_x--0_0--",
    };
    setEvents(mockChart, onEvents, mockSetTriggerValue);

    // Get the handler that was passed to chart.on
    const handler = mockChart.on.mock.calls[0][1];
    handler({ name: "test-value" });

    // The transformed result proves the JsCode function was actually parsed and executed
    expect(mockSetTriggerValue).toHaveBeenCalledWith(
      "chart_event",
      "TEST-VALUE!",
    );
  });
});

describe("setSelectionGenerator", () => {
  let setSelection: ReturnType<typeof setSelectionGenerator>;
  let mockChart: any;
  let mockSetStateValue: any;

  beforeEach(() => {
    setSelection = setSelectionGenerator();
    mockChart = {
      on: vi.fn(),
      off: vi.fn(),
      getOption: vi.fn(() => ({ series: [] })),
      convertFromPixel: vi.fn(),
    };
    mockSetStateValue = vi.fn();
  });

  test("should return true and bind handlers on first call with selectionActive=true", () => {
    const result = setSelection(mockChart, true, ["points"], mockSetStateValue);
    expect(result).toBe(true);
    expect(mockChart.on).toHaveBeenCalledWith("click", expect.any(Function));
  });

  test("should return false and not re-bind on same config", () => {
    setSelection(mockChart, true, ["points"], mockSetStateValue);
    const callCountAfterFirst = mockChart.on.mock.calls.length;

    const result = setSelection(mockChart, true, ["points"], mockSetStateValue);
    expect(result).toBe(false);
    expect(mockChart.on).toHaveBeenCalledTimes(callCountAfterFirst);
  });

  test("should return true when selectionMode changes", () => {
    setSelection(mockChart, true, ["points"], mockSetStateValue);
    const result = setSelection(
      mockChart,
      true,
      ["points", "box"],
      mockSetStateValue,
    );
    expect(result).toBe(true);
  });

  test("should bind click when mode includes points", () => {
    setSelection(mockChart, true, ["points"], mockSetStateValue);
    expect(mockChart.on).toHaveBeenCalledWith("click", expect.any(Function));
  });

  test("should bind brushSelected+brushEnd when mode includes box", () => {
    setSelection(mockChart, true, ["box"], mockSetStateValue);

    const eventNames = mockChart.on.mock.calls.map((c: any) => c[0]);
    expect(eventNames).toContain("brushSelected");
    expect(eventNames).toContain("brushEnd");
  });

  test("should unbind old handlers on re-wire", () => {
    setSelection(mockChart, true, ["points"], mockSetStateValue);
    const clickHandler = mockChart.on.mock.calls[0][1];

    setSelection(mockChart, true, ["box"], mockSetStateValue);

    expect(mockChart.off).toHaveBeenCalledWith("click", clickHandler);
  });

  test("should not bind handlers when selectionActive=false", () => {
    setSelection(mockChart, false, ["points"], mockSetStateValue);
    expect(mockChart.on).not.toHaveBeenCalled();
  });

  test("should call setStateValue with selection on click", () => {
    setSelection(mockChart, true, ["points"], mockSetStateValue);

    const clickHandler = mockChart.on.mock.calls[0][1];
    clickHandler({
      componentType: "series",
      dataIndex: 0,
      seriesIndex: 0,
      seriesName: "S",
      data: 42,
    });

    expect(mockSetStateValue).toHaveBeenCalledWith(
      "selection",
      expect.objectContaining({
        points: expect.arrayContaining([
          expect.objectContaining({ point_index: 0, value: 42 }),
        ]),
      }),
    );
  });
});

describe("renderer change handling", () => {
  let parentElement: HTMLDivElement;
  let mockSetTriggerValue: any;
  let mockSetStateValue: any;
  let mockChart: any;

  const makeData = (renderer: "canvas" | "svg") => ({
    options: { xAxis: { type: "category" as const } },
    theme: "dark" as const,
    onEvents: {},
    height: "400px",
    width: "100%",
    renderer,
    map: null,
    selectionActive: false,
    selectionMode: [] as string[],
  });

  beforeEach(() => {
    // Stub browser APIs not available in jsdom
    globalThis.ResizeObserver = vi.fn(function () {
      return { observe: vi.fn(), unobserve: vi.fn(), disconnect: vi.fn() };
    }) as any;
    globalThis.IntersectionObserver = vi.fn(function () {
      return { observe: vi.fn(), unobserve: vi.fn(), disconnect: vi.fn() };
    }) as any;

    mockChart = {
      on: vi.fn(),
      off: vi.fn(),
      setOption: vi.fn(),
      resize: vi.fn(),
      dispose: vi.fn(),
      isDisposed: vi.fn(() => false),
    };
    vi.mocked(echarts.init).mockReturnValue(mockChart as any);

    parentElement = document.createElement("div");
    const container = document.createElement("div");
    container.className = "echarts-container";
    parentElement.appendChild(container);
    document.body.appendChild(parentElement);

    mockSetTriggerValue = vi.fn();
    mockSetStateValue = vi.fn();
  });

  test("should dispose and re-init chart when renderer changes", () => {
    const args = {
      data: makeData("canvas"),
      parentElement,
      setTriggerValue: mockSetTriggerValue,
      setStateValue: mockSetStateValue,
    };

    // First render with canvas
    const cleanup1 = EchartsRenderer(args as any);
    expect(echarts.init).toHaveBeenCalledWith(
      expect.any(HTMLDivElement),
      expect.any(String),
      { renderer: "canvas" },
    );
    vi.mocked(echarts.init).mockClear();

    // Second render with svg — should dispose old and re-init
    const args2 = { ...args, data: makeData("svg") };
    const cleanup2 = EchartsRenderer(args2 as any);

    expect(mockChart.dispose).toHaveBeenCalled();
    expect(echarts.init).toHaveBeenCalledWith(
      expect.any(HTMLDivElement),
      expect.any(String),
      { renderer: "svg" },
    );

    // Clean up
    cleanup2!();
  });

  test("should NOT dispose chart when renderer stays the same", () => {
    const args = {
      data: makeData("canvas"),
      parentElement,
      setTriggerValue: mockSetTriggerValue,
      setStateValue: mockSetStateValue,
    };

    // First render
    EchartsRenderer(args as any);
    vi.mocked(echarts.init).mockClear();
    mockChart.dispose.mockClear();

    // Second render with same renderer
    const cleanup = EchartsRenderer(args as any);

    expect(mockChart.dispose).not.toHaveBeenCalled();
    expect(echarts.init).not.toHaveBeenCalled();

    cleanup!();
  });
});
