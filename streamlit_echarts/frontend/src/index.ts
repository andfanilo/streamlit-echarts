import {
  FrontendRenderer,
  FrontendRendererArgs,
} from "@streamlit/component-v2-lib";

import * as echarts from "echarts";
import "echarts-gl";
import "echarts-liquidfill";
import "echarts-wordcloud";

import deepMap from "./utils";
import { evalStringToFunction } from "./parsers";
import {
  SelectionData,
  EMPTY_SELECTION,
  transformClickToSelection,
  transformBrushToSelection,
  buildBrushOption,
} from "./selection";

interface Map {
  mapName: string;
  geoJson: any;
  specialAreas: any;
}

export type EchartsStateShape = {
  chart_event?: any;
  selection?: SelectionData;
};

export type EchartsDataShape = {
  options: echarts.EChartsOption;
  theme: string | object;
  onEvents: Record<string, string>;
  height: string;
  width: string;
  renderer: "canvas" | "svg";
  map: Map | null;
  selectionActive?: boolean;
  selectionMode?: string[];
};

const FALLBACK_PALETTE = [
  "#0068C9",
  "#83C9FF",
  "#FF2B2B",
  "#FFABAB",
  "#29B09D",
  "#7DEFA1",
  "#FF8700",
  "#FFD16A",
  "#6D3FC0",
  "#D5B5FF",
];

/**
 * Memoized options parser. Runs deepMap + evalStringToFunction only when
 * the serialized options change.
 */
export const getOptionsGenerator = () => {
  let savedKey: string | null = null;
  let savedOptions: echarts.EChartsOption | null = null;

  return (options: echarts.EChartsOption) => {
    const key = JSON.stringify(options);
    if (key !== savedKey) {
      savedKey = key;
      savedOptions = deepMap(options, evalStringToFunction, {});
      return { data: savedOptions, hasChanged: true };
    }
    return { data: savedOptions, hasChanged: false };
  };
};

/**
 * Memoized theme registration. Calls echarts.registerTheme only when the
 * theme prop or the resolved Streamlit CSS variable values change.
 * Returns the theme name to pass to echarts.init and whether it changed.
 */
export const setThemeGenerator = () => {
  let currentKey: string | null = null;
  let currentThemeName: string = "";

  return (
    theme: string | object,
    container: HTMLElement,
  ): { themeName: string; themeChanged: boolean } => {
    const customThemeName = "custom_theme";

    // Read CSS vars needed for the "streamlit" theme.
    const getCssVar = (v: string) =>
      getComputedStyle(container).getPropertyValue(v).trim();

    const backgroundColor =
      theme === "streamlit" ? getCssVar("--st-background-color") : "";
    const textColor = theme === "streamlit" ? getCssVar("--st-text-color") : "";
    const font = theme === "streamlit" ? getCssVar("--st-font") : "";
    const categoricalRaw =
      theme === "streamlit" ? getCssVar("--st-chart-categorical-colors") : "";

    const key = JSON.stringify({
      theme,
      backgroundColor,
      textColor,
      font,
      categoricalRaw,
    });

    if (key === currentKey) {
      return { themeName: currentThemeName, themeChanged: false };
    }

    currentKey = key;

    if (theme === "streamlit") {
      const palette = categoricalRaw
        ? categoricalRaw.split(",").map((c) => c.trim())
        : FALLBACK_PALETTE;
      const tc = textColor || "#31333F";
      // Subtle color for axis lines, split lines, borders
      const subtleColor = textColor
        ? textColor + "33" // 20% opacity
        : "#31333F33";
      const stTheme = {
        color: palette,
        backgroundColor: backgroundColor || "transparent",
        textStyle: {
          color: tc,
          fontFamily: font || undefined,
        },
        title: { textStyle: { color: tc } },
        legend: { textStyle: { color: tc } },
        tooltip: {
          backgroundColor: backgroundColor || "#fff",
          borderColor: subtleColor,
          textStyle: { color: tc },
        },
        categoryAxis: {
          axisLabel: { color: tc },
          axisLine: { lineStyle: { color: subtleColor } },
          axisTick: { lineStyle: { color: subtleColor } },
          splitLine: { lineStyle: { color: subtleColor } },
        },
        valueAxis: {
          axisLabel: { color: tc },
          axisLine: { lineStyle: { color: subtleColor } },
          axisTick: { lineStyle: { color: subtleColor } },
          splitLine: { lineStyle: { color: subtleColor } },
        },
        dataZoom: {
          textStyle: { color: tc },
        },
      };
      echarts.registerTheme("streamlit", stTheme);
      currentThemeName = "streamlit";
    } else if (typeof theme === "object" && theme !== null) {
      echarts.registerTheme(customThemeName, theme);
      currentThemeName = customThemeName;
    } else {
      currentThemeName = theme as string;
    }

    return { themeName: currentThemeName, themeChanged: true };
  };
};

/**
 * Memoized event wiring. Calls chart.off/chart.on only when the serialized
 * onEvents change.
 */
export const setEventsGenerator = () => {
  let savedKey: string | null = null;
  let savedHandlers: Record<string, Function> = {};

  return (
    chart: echarts.ECharts,
    onEvents: Record<string, string>,
    setTriggerValue: FrontendRendererArgs<EchartsStateShape>["setTriggerValue"],
  ): boolean => {
    const key = JSON.stringify(onEvents);
    if (key === savedKey) {
      return false;
    }

    // Unbind old handlers by reference (not by name) to preserve other listeners
    for (const eventName of Object.keys(savedHandlers)) {
      chart.off(eventName, savedHandlers[eventName] as any);
    }

    // Build and bind new handlers
    const handlers: Record<string, Function> = {};
    for (const eventName of Object.keys(onEvents)) {
      const fn = evalStringToFunction(onEvents[eventName]) as Function;
      const handler = (params: any) => {
        setTriggerValue("chart_event", fn(params));
      };
      handlers[eventName] = handler;
      chart.on(eventName, handler as any);
    }

    savedKey = key;
    savedHandlers = handlers;
    return true;
  };
};

/**
 * Memoized selection wiring. Manages click and brush listeners for the
 * structured selection API. Uses handler-specific unbind to coexist with
 * user-defined event handlers.
 */
export const setSelectionGenerator = () => {
  let savedKey: string | null = null;
  let savedHandlers: { event: string; handler: Function }[] = [];

  return (
    chart: echarts.ECharts,
    selectionActive: boolean,
    selectionMode: string[],
    setStateValue: FrontendRendererArgs<EchartsStateShape>["setStateValue"],
  ): boolean => {
    const key = JSON.stringify({ selectionActive, selectionMode });
    if (key === savedKey) {
      return false;
    }

    // Unbind old handlers by reference
    for (const { event, handler } of savedHandlers) {
      chart.off(event, handler as any);
    }
    savedHandlers = [];

    if (!selectionActive) {
      savedKey = key;
      return true;
    }

    // Click handler for "points" mode
    if (selectionMode.includes("points")) {
      const clickHandler = (params: any) => {
        const selection = transformClickToSelection(params);
        setStateValue("selection", selection);
      };
      chart.on("click", clickHandler as any);
      savedHandlers.push({ event: "click", handler: clickHandler });
    }

    // Brush handlers for "box" and "lasso" modes
    // ECharts fires brushEnd (areas) BEFORE the final brushSelected (batch),
    // so we cache areas from brushEnd and trigger state from brushSelected.
    if (selectionMode.includes("box") || selectionMode.includes("lasso")) {
      let cachedAreas: any[] = [];

      const brushEndHandler = (params: any) => {
        cachedAreas = params.areas ?? [];
        if (cachedAreas.length === 0) {
          setStateValue("selection", EMPTY_SELECTION);
        }
      };

      const brushSelectedHandler = (params: any) => {
        const batch = params.batch ?? [];
        if (cachedAreas.length === 0) return;
        const selection = transformBrushToSelection(batch, cachedAreas, chart);
        setStateValue("selection", selection);
      };

      chart.on("brushEnd", brushEndHandler as any);
      chart.on("brushSelected", brushSelectedHandler as any);
      savedHandlers.push(
        { event: "brushEnd", handler: brushEndHandler },
        { event: "brushSelected", handler: brushSelectedHandler },
      );
    }

    savedKey = key;
    return true;
  };
};

/**
 * Component-scoped state keyed by the host element to support multiple
 * instances.
 */
type ComponentState = {
  chart: echarts.ECharts | null;
  resizeObserver: ResizeObserver | null;
  intersectionObserver: IntersectionObserver | null;
  getOptions: ReturnType<typeof getOptionsGenerator>;
  setTheme: ReturnType<typeof setThemeGenerator>;
  setEvents: ReturnType<typeof setEventsGenerator>;
  setSelection: ReturnType<typeof setSelectionGenerator>;
};

const componentState = new WeakMap<HTMLElement | ShadowRoot, ComponentState>();

const getOrCreateInstanceState = (
  host: HTMLElement | ShadowRoot,
): ComponentState => {
  let state = componentState.get(host);

  if (!state) {
    state = {
      chart: null,
      resizeObserver: null,
      intersectionObserver: null,
      getOptions: getOptionsGenerator(),
      setTheme: setThemeGenerator(),
      setEvents: setEventsGenerator(),
      setSelection: setSelectionGenerator(),
    };
    componentState.set(host, state);
  }

  return state;
};

const EchartsRenderer: FrontendRenderer<EchartsStateShape, EchartsDataShape> = (
  args,
) => {
  const { data, parentElement, setTriggerValue, setStateValue } = args;
  const {
    options,
    theme,
    onEvents,
    height,
    width,
    renderer,
    map,
    selectionActive = false,
    selectionMode = [],
  } = data;

  const container =
    parentElement.querySelector<HTMLDivElement>(".echarts-container");

  if (!container) {
    throw new Error("Unexpected: ECharts container element not found");
  }

  const state = getOrCreateInstanceState(parentElement);

  // 1. Size the container
  container.style.height = height;
  container.style.width = width;

  // 2. Register map if provided (idempotent)
  if (map && typeof map === "object" && map.mapName) {
    echarts.registerMap(map.mapName, map.geoJson, map.specialAreas);
  }

  // 3. Resolve theme (memoized). If theme changed, dispose existing chart
  //    because ECharts requires re-init for theme changes.
  const { themeName, themeChanged } = state.setTheme(theme, container);

  if (themeChanged && state.chart) {
    state.chart.dispose();
    state.chart = null;
    // Reset memoized generators so stale references are cleared and
    // options are re-applied to the new chart instance (preserving animations).
    state.getOptions = getOptionsGenerator();
    state.setEvents = setEventsGenerator();
    state.setSelection = setSelectionGenerator();
  }

  // 4. Create chart if needed
  if (!state.chart || state.chart.isDisposed()) {
    state.chart = echarts.init(container, themeName, { renderer });
  }

  // 5. Apply options if changed
  const { data: cleanOptions, hasChanged: optionsChanged } =
    state.getOptions(options);

  if (optionsChanged) {
    state.chart.setOption(cleanOptions!, { notMerge: true });
  }

  // 6. Wire events (memoized unbind/rebind)
  state.setEvents(state.chart, onEvents, setTriggerValue);

  // 6b. Wire selection listeners and overlay brush config
  const selectionChanged = state.setSelection(
    state.chart,
    selectionActive,
    selectionMode,
    setStateValue,
  );
  if (selectionChanged && selectionActive) {
    state.chart.setOption(buildBrushOption(selectionMode), {
      notMerge: false,
    });
  }

  // 7. Set up ResizeObserver (once per instance)
  //    Skip the initial callback fired by observe() — the chart was just
  //    created at the correct size and an immediate resize() would kill
  //    the entry animation.
  if (!state.resizeObserver) {
    let firstResize = true;
    state.resizeObserver = new ResizeObserver(() => {
      if (firstResize) {
        firstResize = false;
        return;
      }
      if (
        state.chart &&
        !state.chart.isDisposed() &&
        container.offsetParent !== null
      ) {
        state.chart.resize();
      }
    });
    state.resizeObserver.observe(container);
  }

  // 8. Set up IntersectionObserver to resize on tab/expander visibility change
  //    Same initial-callback skip as above.
  if (!state.intersectionObserver) {
    let firstIntersect = true;
    state.intersectionObserver = new IntersectionObserver((entries) => {
      if (firstIntersect) {
        firstIntersect = false;
        return;
      }
      for (const entry of entries) {
        if (entry.isIntersecting && state.chart && !state.chart.isDisposed()) {
          state.chart.resize();
        }
      }
    });
    state.intersectionObserver.observe(container);
  }

  // 9. Cleanup function
  return () => {
    if (state.intersectionObserver) {
      state.intersectionObserver.disconnect();
      state.intersectionObserver = null;
    }
    if (state.resizeObserver) {
      state.resizeObserver.disconnect();
      state.resizeObserver = null;
    }
    if (state.chart) {
      state.chart.dispose();
      state.chart = null;
    }
    componentState.delete(parentElement);
  };
};

export default EchartsRenderer;
