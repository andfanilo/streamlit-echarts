import { beforeEach, describe, expect, test, vi } from "vitest";

// Mock ECharts and extensions before importing the module under test
vi.mock("echarts", () => ({
  registerTheme: vi.fn(),
  registerMap: vi.fn(),
  init: vi.fn(),
  color: {
    modifyAlpha: vi.fn((c: string, a: number) => `rgba(0,0,0,${a})`),
  },
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
import { EMPTY_SELECTION } from "./selection";

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

  test("should swap double quotes in --st-font for single quotes (SVG-safe, issue #82)", () => {
    container.style.setProperty("--st-font", '"Source Sans", sans-serif');
    setTheme("streamlit", container);

    expect(echarts.registerTheme).toHaveBeenCalledWith(
      "streamlit",
      expect.objectContaining({
        textStyle: expect.objectContaining({
          fontFamily: "'Source Sans', sans-serif",
        }),
      }),
    );
  });

  test("should register custom object theme under a content-based name", () => {
    const customTheme = { color: ["#ff0000"] };
    const result = setTheme(customTheme, container);

    expect(result.themeChanged).toBe(true);
    expect(result.themeName).toMatch(/^custom_theme_/);
    expect(echarts.registerTheme).toHaveBeenCalledWith(
      result.themeName,
      customTheme,
    );
  });

  test("should register distinct custom themes under different names", () => {
    const themeA = { color: ["#ff0000"] };
    const themeB = { color: ["#00ff00"] };
    const nameA = setTheme(themeA, container).themeName;
    const nameB = setTheme(themeB, container).themeName;

    expect(nameA).not.toBe(nameB);
    expect(echarts.registerTheme).toHaveBeenCalledWith(nameA, themeA);
    expect(echarts.registerTheme).toHaveBeenCalledWith(nameB, themeB);
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

  test("does NOT emit when the handler returns undefined (client-side only)", () => {
    const onEvents = {
      click: "--x_x--0_0--function () { /* side effect only */ }--x_x--0_0--",
    };
    setEvents(mockChart, onEvents, mockSetTriggerValue);

    const handler = mockChart.on.mock.calls[0][1];
    handler({ name: "whatever" });

    expect(mockSetTriggerValue).not.toHaveBeenCalled();
  });

  test("emits null when the handler explicitly returns null", () => {
    const onEvents = {
      click: "--x_x--0_0--function () { return null; }--x_x--0_0--",
    };
    setEvents(mockChart, onEvents, mockSetTriggerValue);

    const handler = mockChart.on.mock.calls[0][1];
    handler({});

    expect(mockSetTriggerValue).toHaveBeenCalledWith("chart_event", null);
  });
});

describe("setEventsGenerator — zrender events (zr: prefix)", () => {
  let setEvents: ReturnType<typeof setEventsGenerator>;
  let mockChart: any;
  let mockZr: any;
  let mockSetTriggerValue: (name: keyof EchartsStateShape, value: any) => void;

  beforeEach(() => {
    setEvents = setEventsGenerator();
    mockZr = { on: vi.fn(), off: vi.fn() };
    mockChart = {
      on: vi.fn(),
      off: vi.fn(),
      getZr: vi.fn(() => mockZr),
    };
    mockSetTriggerValue = vi.fn() as any;
  });

  test("binds a zr:-prefixed event on the zrender instance with the prefix stripped", () => {
    const onEvents = {
      "zr:click": "--x_x--0_0--function (e) { return e.offsetX; }--x_x--0_0--",
    };
    setEvents(mockChart, onEvents, mockSetTriggerValue);

    expect(mockZr.on).toHaveBeenCalledWith("click", expect.any(Function));
    // It must NOT leak onto the chart-level emitter (neither stripped nor raw)
    expect(mockChart.on).not.toHaveBeenCalledWith(
      "click",
      expect.any(Function),
    );
    expect(mockChart.on).not.toHaveBeenCalledWith(
      "zr:click",
      expect.any(Function),
    );
  });

  test("routes chart-level and zr-level handlers to their own emitters", () => {
    const onEvents = {
      click: "--x_x--0_0--function (p) { return p.name; }--x_x--0_0--",
      "zr:click": "--x_x--0_0--function (e) { return e.offsetX; }--x_x--0_0--",
    };
    setEvents(mockChart, onEvents, mockSetTriggerValue);

    expect(mockChart.on).toHaveBeenCalledWith("click", expect.any(Function));
    expect(mockZr.on).toHaveBeenCalledWith("click", expect.any(Function));
  });

  test("unbinds zr handlers from the zrender instance (by reference) on change", () => {
    const onEvents1 = {
      "zr:click": "--x_x--0_0--function (e) { return e.offsetX; }--x_x--0_0--",
    };
    const onEvents2 = {
      "zr:mousemove":
        "--x_x--0_0--function (e) { return e.offsetY; }--x_x--0_0--",
    };
    setEvents(mockChart, onEvents1, mockSetTriggerValue);
    const boundHandler = mockZr.on.mock.calls[0][1];
    mockZr.on.mockClear();

    setEvents(mockChart, onEvents2, mockSetTriggerValue);

    expect(mockZr.off).toHaveBeenCalledWith("click", boundHandler);
    expect(mockZr.on).toHaveBeenCalledWith("mousemove", expect.any(Function));
  });

  test("zr handler forwards its return value through setTriggerValue", () => {
    const onEvents = {
      "zr:click":
        "--x_x--0_0--function (e) { return e.target ? null : 'blank'; }--x_x--0_0--",
    };
    setEvents(mockChart, onEvents, mockSetTriggerValue);

    const handler = mockZr.on.mock.calls[0][1];
    handler({ target: null, offsetX: 5, offsetY: 9 });

    expect(mockSetTriggerValue).toHaveBeenCalledWith("chart_event", "blank");
  });

  test("does not touch getZr() when there are no zr: handlers", () => {
    const onEvents = {
      click: "--x_x--0_0--function (p) { return p.name; }--x_x--0_0--",
    };
    setEvents(mockChart, onEvents, mockSetTriggerValue);

    expect(mockChart.getZr).not.toHaveBeenCalled();
  });
});

describe("setSelectionGenerator", () => {
  let setSelection: ReturnType<typeof setSelectionGenerator>;
  let mockChart: any;
  let mockZr: any;
  let mockSetStateValue: any;

  beforeEach(() => {
    setSelection = setSelectionGenerator();
    mockZr = { on: vi.fn(), off: vi.fn() };
    mockChart = {
      on: vi.fn(),
      off: vi.fn(),
      getOption: vi.fn(() => ({ series: [] })),
      convertFromPixel: vi.fn(),
      getZr: vi.fn(() => mockZr),
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

  test("double-click on blank canvas clears the selection (points mode)", () => {
    setSelection(mockChart, true, ["points"], mockSetStateValue);

    // points mode wires a single zrender listener: the dblclick deselect.
    const [event, deselectHandler] = mockZr.on.mock.calls[0];
    expect(event).toBe("dblclick");

    deselectHandler({ target: null }); // blank canvas → no graphic element hit

    expect(mockSetStateValue).toHaveBeenCalledWith(
      "selection",
      EMPTY_SELECTION,
    );
  });

  test("double-click on a graphic element does NOT clear the selection", () => {
    setSelection(mockChart, true, ["points"], mockSetStateValue);
    const deselectHandler = mockZr.on.mock.calls[0][1];

    deselectHandler({ target: {} }); // hit a bar/point

    expect(mockSetStateValue).not.toHaveBeenCalled();
  });

  test("unbinds the zrender deselect handler on re-wire", () => {
    setSelection(mockChart, true, ["points"], mockSetStateValue);
    const deselectHandler = mockZr.on.mock.calls[0][1];

    setSelection(mockChart, true, ["box"], mockSetStateValue);

    expect(mockZr.off).toHaveBeenCalledWith("dblclick", deselectHandler);
  });

  describe("brush event ordering", () => {
    const handlerFor = (name: string) =>
      mockChart.on.mock.calls.find((c: any) => c[0] === name)![1];

    const areas = [
      {
        brushType: "rect",
        range: [
          [0, 10],
          [0, 10],
        ],
      },
    ];
    const batch = [{ areas, selected: [{ seriesIndex: 0, dataIndex: [1] }] }];

    test("emits once when brushSelected arrives after brushEnd (fast drag, debounce trailing)", () => {
      setSelection(mockChart, true, ["box"], mockSetStateValue);

      handlerFor("brushEnd")({ areas });
      expect(mockSetStateValue).not.toHaveBeenCalled();

      handlerFor("brushSelected")({ batch });
      expect(mockSetStateValue).toHaveBeenCalledTimes(1);
      expect(mockSetStateValue).toHaveBeenCalledWith(
        "selection",
        expect.objectContaining({ point_indices: [1] }),
      );
    });

    test("emits once when brushEnd arrives after brushSelected (pause mid-drag, release without moving)", () => {
      setSelection(mockChart, true, ["box"], mockSetStateValue);

      handlerFor("brushSelected")({ batch });
      expect(mockSetStateValue).not.toHaveBeenCalled();

      handlerFor("brushEnd")({ areas });
      expect(mockSetStateValue).toHaveBeenCalledTimes(1);
      expect(mockSetStateValue).toHaveBeenCalledWith(
        "selection",
        expect.objectContaining({ point_indices: [1] }),
      );
    });

    test("toolbox clear (brushSelected with empty areas, no brushEnd) empties the selection", () => {
      setSelection(mockChart, true, ["box"], mockSetStateValue);

      // Complete a gesture first so there is a selection to clear.
      handlerFor("brushEnd")({ areas });
      handlerFor("brushSelected")({ batch });
      mockSetStateValue.mockClear();

      handlerFor("brushSelected")({ batch: [{ areas: [], selected: [] }] });

      expect(mockSetStateValue).toHaveBeenCalledTimes(1);
      expect(mockSetStateValue).toHaveBeenCalledWith(
        "selection",
        EMPTY_SELECTION,
      );
    });

    test("brushEnd with no areas empties the selection", () => {
      setSelection(mockChart, true, ["box"], mockSetStateValue);

      handlerFor("brushEnd")({ areas: [] });

      expect(mockSetStateValue).toHaveBeenCalledWith(
        "selection",
        EMPTY_SELECTION,
      );
    });

    test("does not emit anything before any gesture completes", () => {
      setSelection(mockChart, true, ["box"], mockSetStateValue);

      // e.g. the brushSelected ECharts fires right after brush setup
      handlerFor("brushSelected")({ batch: [] });

      expect(mockSetStateValue).not.toHaveBeenCalled();
    });
  });
});

describe("chart re-init on renderer/theme change", () => {
  let parentElement: HTMLDivElement;
  let mockSetTriggerValue: any;
  let mockSetStateValue: any;
  let mockChart: any;

  const makeData = (renderer: "canvas" | "svg", theme: string = "dark") => ({
    options: { xAxis: { type: "category" as const } },
    theme,
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
      getOption: vi.fn(() => ({})),
      dispatchAction: vi.fn(),
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

  test("should dispose and re-init chart when theme changes", () => {
    const args = {
      data: makeData("canvas"),
      parentElement,
      setTriggerValue: mockSetTriggerValue,
      setStateValue: mockSetStateValue,
    };

    EchartsRenderer(args as any);
    vi.mocked(echarts.init).mockClear();

    const args2 = { ...args, data: makeData("canvas", "light") };
    const cleanup = EchartsRenderer(args2 as any);

    expect(mockChart.dispose).toHaveBeenCalled();
    expect(echarts.init).toHaveBeenCalledWith(
      expect.any(HTMLDivElement),
      "light",
      {
        renderer: "canvas",
      },
    );

    cleanup!();
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

describe("replaceMerge handling", () => {
  let parentElement: HTMLDivElement;
  let mockSetTriggerValue: any;
  let mockSetStateValue: any;
  let mockChart: any;

  beforeEach(() => {
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
      getOption: vi.fn(() => ({})),
      dispatchAction: vi.fn(),
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

  // Re-use makeData from the "renderer change handling" scope isn't possible
  // since it's block-scoped, so define a local helper.
  const mkData = (replaceMerge?: string | string[]) => ({
    options: { xAxis: { type: "category" as const } },
    theme: "dark" as const,
    onEvents: {},
    height: "400px",
    width: "100%",
    renderer: "canvas" as const,
    replaceMerge,
    map: null,
    selectionActive: false,
    selectionMode: [] as string[],
  });

  test("should call setOption with notMerge:true when replaceMerge is undefined", () => {
    const args = {
      data: mkData(),
      parentElement,
      setTriggerValue: mockSetTriggerValue,
      setStateValue: mockSetStateValue,
    };
    EchartsRenderer(args as any);
    expect(mockChart.setOption).toHaveBeenCalledWith(expect.any(Object), {
      notMerge: true,
    });
  });

  test("should call setOption with replaceMerge when provided as string", () => {
    const args = {
      data: mkData("series"),
      parentElement,
      setTriggerValue: mockSetTriggerValue,
      setStateValue: mockSetStateValue,
    };
    EchartsRenderer(args as any);
    expect(mockChart.setOption).toHaveBeenCalledWith(expect.any(Object), {
      replaceMerge: "series",
    });
  });

  test("should call setOption with replaceMerge when provided as array", () => {
    const args = {
      data: mkData(["series", "xAxis"]),
      parentElement,
      setTriggerValue: mockSetTriggerValue,
      setStateValue: mockSetStateValue,
    };
    EchartsRenderer(args as any);
    expect(mockChart.setOption).toHaveBeenCalledWith(expect.any(Object), {
      replaceMerge: ["series", "xAxis"],
    });
  });
});

describe("selection brush clear wiring", () => {
  let parentElement: HTMLDivElement;
  let mockChart: any;
  let mockSetTriggerValue: any;
  let mockSetStateValue: any;

  const mkData = (selectionActive: boolean, selectionMode: string[]) => ({
    options: { xAxis: { type: "category" as const } },
    theme: "dark" as const,
    onEvents: {},
    height: "400px",
    width: "100%",
    renderer: "canvas" as const,
    map: null,
    selectionActive,
    selectionMode,
  });

  beforeEach(() => {
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
      getOption: vi.fn(() => ({ brush: [{}] })),
      dispatchAction: vi.fn(),
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

  test("disabling selection clears drawn areas and removes the brush component", () => {
    const base = {
      parentElement,
      setTriggerValue: mockSetTriggerValue,
      setStateValue: mockSetStateValue,
    };

    // Enable brush selection, then reset the spies
    EchartsRenderer({ ...base, data: mkData(true, ["box", "lasso"]) } as any);
    mockChart.setOption.mockClear();
    mockChart.dispatchAction.mockClear();

    // Disable selection → clear path
    const cleanup = EchartsRenderer({
      ...base,
      data: mkData(false, []),
    } as any);

    expect(mockChart.dispatchAction).toHaveBeenCalledWith({
      type: "brush",
      areas: [],
    });
    expect(mockChart.setOption).toHaveBeenCalledWith(expect.any(Object), {
      replaceMerge: ["brush"],
    });

    cleanup!();
  });

  test("re-applies brush overlay when options change but selection config does not", () => {
    const base = {
      parentElement,
      setTriggerValue: mockSetTriggerValue,
      setStateValue: mockSetStateValue,
    };

    EchartsRenderer({ ...base, data: mkData(true, ["box"]) } as any);
    mockChart.setOption.mockClear();
    mockChart.dispatchAction.mockClear();

    // Same selection config, new options. The notMerge:true options apply
    // wipes the previously merged brush, so it must be merged back.
    const cleanup = EchartsRenderer({
      ...base,
      data: {
        ...mkData(true, ["box"]),
        options: { xAxis: { type: "value" as const } },
      },
    } as any);

    expect(mockChart.setOption).toHaveBeenCalledWith(
      expect.objectContaining({ brush: expect.anything() }),
      { notMerge: false },
    );
    // The clear path must not run on a plain options update.
    expect(mockChart.dispatchAction).not.toHaveBeenCalled();

    cleanup!();
  });

  test("does not touch brush config on options change when no brush mode is wanted", () => {
    const base = {
      parentElement,
      setTriggerValue: mockSetTriggerValue,
      setStateValue: mockSetStateValue,
    };

    EchartsRenderer({ ...base, data: mkData(false, []) } as any);
    mockChart.setOption.mockClear();
    mockChart.dispatchAction.mockClear();

    const cleanup = EchartsRenderer({
      ...base,
      data: {
        ...mkData(false, []),
        options: { xAxis: { type: "value" as const } },
      },
    } as any);

    // Only the options apply — no brush merge, no clear path.
    expect(mockChart.setOption).toHaveBeenCalledTimes(1);
    expect(mockChart.setOption).toHaveBeenCalledWith(expect.any(Object), {
      notMerge: true,
    });
    expect(mockChart.dispatchAction).not.toHaveBeenCalled();

    cleanup!();
  });
});

describe("external dispose recovery", () => {
  let parentElement: HTMLDivElement;
  let mockSetTriggerValue: any;
  let mockSetStateValue: any;

  const makeMockChart = () => ({
    on: vi.fn(),
    off: vi.fn(),
    setOption: vi.fn(),
    getOption: vi.fn(() => ({})),
    dispatchAction: vi.fn(),
    resize: vi.fn(),
    dispose: vi.fn(),
    isDisposed: vi.fn(() => false),
    getZr: vi.fn(() => ({ on: vi.fn(), off: vi.fn() })),
  });

  beforeEach(() => {
    globalThis.ResizeObserver = vi.fn(function () {
      return { observe: vi.fn(), unobserve: vi.fn(), disconnect: vi.fn() };
    }) as any;
    globalThis.IntersectionObserver = vi.fn(function () {
      return { observe: vi.fn(), unobserve: vi.fn(), disconnect: vi.fn() };
    }) as any;

    parentElement = document.createElement("div");
    const container = document.createElement("div");
    container.className = "echarts-container";
    parentElement.appendChild(container);
    document.body.appendChild(parentElement);

    mockSetTriggerValue = vi.fn();
    mockSetStateValue = vi.fn();
  });

  test("re-inits and rebinds options/handlers when the chart was disposed externally", () => {
    const firstChart = makeMockChart();
    vi.mocked(echarts.init).mockReturnValue(firstChart as any);

    const args = {
      data: {
        options: { xAxis: { type: "category" as const } },
        theme: "dark" as const,
        onEvents: {},
        height: "400px",
        width: "100%",
        renderer: "canvas" as const,
        map: null,
        selectionActive: true,
        selectionMode: ["points"],
      },
      parentElement,
      setTriggerValue: mockSetTriggerValue,
      setStateValue: mockSetStateValue,
    };

    EchartsRenderer(args as any);
    expect(firstChart.on).toHaveBeenCalledWith("click", expect.any(Function));

    // Simulate a dispose that happened outside the renderer between reruns.
    firstChart.isDisposed.mockReturnValue(true);
    const freshChart = makeMockChart();
    vi.mocked(echarts.init).mockReturnValue(freshChart as any);

    // Identical data: nothing changed, yet the dead chart must be replaced
    // and options + selection handlers re-applied to the fresh instance.
    const cleanup = EchartsRenderer(args as any);

    expect(freshChart.setOption).toHaveBeenCalledWith(expect.any(Object), {
      notMerge: true,
    });
    expect(freshChart.on).toHaveBeenCalledWith("click", expect.any(Function));

    cleanup!();
  });
});
