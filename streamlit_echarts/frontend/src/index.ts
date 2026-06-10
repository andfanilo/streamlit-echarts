import {
  FrontendRenderer,
  FrontendRendererArgs,
} from "@streamlit/component-v2-lib";

import * as echarts from "echarts";
import "echarts-gl";
import "echarts-liquidfill";
import "echarts-wordcloud";

import deepMap, { hashString } from "./utils";
import { evalJsCode } from "./parsers";
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
  replaceMerge?: string | string[];
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
 * Memoized options parser. Runs deepMap + evalJsCode only when the
 * serialized options change.
 */
export const getOptionsGenerator = () => {
  let savedKey: string | null = null;
  let savedOptions: echarts.EChartsOption | null = null;

  return (options: echarts.EChartsOption) => {
    const key = JSON.stringify(options);
    if (key !== savedKey) {
      savedKey = key;
      savedOptions = deepMap(
        options,
        (s: string) => evalJsCode(s, { echarts }),
        {},
      );
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
    // Read CSS vars needed for the "streamlit" theme.
    const getCssVar = (v: string) =>
      getComputedStyle(container).getPropertyValue(v).trim();

    const backgroundColor =
      theme === "streamlit" ? getCssVar("--st-background-color") : "";
    const textColor = theme === "streamlit" ? getCssVar("--st-text-color") : "";
    // Single-quote font names so they survive ECharts' SVG export (issue #82).
    const font =
      theme === "streamlit" ? getCssVar("--st-font").replace(/"/g, "'") : "";
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
      // Subtle color (~20% opacity) for axis lines, split lines, borders.
      // echarts.color.modifyAlpha parses any CSS color format Streamlit may
      // emit (hex/rgb/rgba/named); fall back to tc if the color is unparseable.
      const subtleColor = echarts.color.modifyAlpha(tc, 0.2) || tc;
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
      // Derive a content-based name so distinct custom themes across multiple
      // component instances don't overwrite each other on a shared global key.
      const customThemeName = `custom_theme_${hashString(JSON.stringify(theme))}`;
      echarts.registerTheme(customThemeName, theme);
      currentThemeName = customThemeName;
    } else {
      currentThemeName = theme as string;
    }

    return { themeName: currentThemeName, themeChanged: true };
  };
};

// Event names prefixed with this bind to the underlying zrender instance
// (canvas-wide, fires on blank space) instead of the chart (graphic elements
// only). See the "Listen to Events on the Blank Area" ECharts handbook page.
const ZR_PREFIX = "zr:";

type HandlerEntry = { name: string; handler: (params: any) => void };
type BoundHandler = { isZr: boolean; event: string; handler: Function };

// Resolve the zrender instance lazily so chart-only paths never call getZr()
// (it's only needed when a zr: handler is bound or unbound).
const makeGetZr = (chart: echarts.ECharts) => {
  let zr: ReturnType<echarts.ECharts["getZr"]> | null = null;
  return () => (zr ??= chart.getZr());
};

/**
 * Bind handlers to the chart, routing `zr:`-prefixed names (prefix stripped)
 * to the zrender instance. Returns records that let unbindHandlers remove
 * exactly these listeners later.
 */
const bindHandlers = (
  chart: echarts.ECharts,
  entries: HandlerEntry[],
): BoundHandler[] => {
  const getZr = makeGetZr(chart);
  return entries.map(({ name, handler }) => {
    const isZr = name.startsWith(ZR_PREFIX);
    const event = isZr ? name.slice(ZR_PREFIX.length) : name;
    if (isZr) getZr().on(event, handler as any);
    else chart.on(event, handler as any);
    return { isZr, event, handler };
  });
};

/**
 * Unbind handlers by reference (not by name) to preserve other listeners,
 * routing each to the emitter it was bound on.
 */
const unbindHandlers = (chart: echarts.ECharts, bound: BoundHandler[]) => {
  const getZr = makeGetZr(chart);
  for (const { isZr, event, handler } of bound) {
    if (isZr) getZr().off(event, handler as any);
    else chart.off(event, handler as any);
  }
};

/**
 * Memoized event wiring. Calls chart.off/chart.on (or the zrender instance's
 * off/on for `zr:`-prefixed names) only when the serialized onEvents change.
 */
export const setEventsGenerator = () => {
  let savedKey: string | null = null;
  let savedHandlers: BoundHandler[] = [];

  return (
    chart: echarts.ECharts,
    onEvents: Record<string, string>,
    setTriggerValue: FrontendRendererArgs<EchartsStateShape>["setTriggerValue"],
  ): boolean => {
    const key = JSON.stringify(onEvents);
    if (key === savedKey) {
      return false;
    }

    unbindHandlers(chart, savedHandlers);

    const entries: HandlerEntry[] = [];
    for (const name of Object.keys(onEvents)) {
      // `chart` is in scope so handlers can call instance methods (e.g.
      // convertFromPixel, dispatchAction). Safe because this generator is
      // reset on every chart dispose, so `chart` is never stale (issue #70).
      const fn = evalJsCode(onEvents[name], { echarts, chart });
      if (typeof fn !== "function") {
        console.error(
          `JsCode for event "${name}" did not evaluate to a function`,
        );
        continue;
      }
      const handler = (params: any) => {
        // Returning undefined (or nothing) marks a client-side-only handler:
        // skip the round-trip so side-effect handlers (setOption/dispatchAction)
        // and high-frequency events (zr:mousemove) don't spam reruns. Any other
        // value, including null, is emitted to Python.
        const result = fn(params);
        if (result !== undefined) {
          setTriggerValue("chart_event", result);
        }
      };
      entries.push({ name, handler });
    }

    savedKey = key;
    savedHandlers = bindHandlers(chart, entries);
    return true;
  };
};

/**
 * Memoized selection wiring. Manages click, double-click-to-deselect, and
 * brush listeners for the structured selection API. Uses handler-specific
 * unbind (chart- and zrender-level) to coexist with user event handlers.
 */
export const setSelectionGenerator = () => {
  let savedKey: string | null = null;
  let savedHandlers: BoundHandler[] = [];

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

    unbindHandlers(chart, savedHandlers);

    const entries: HandlerEntry[] = [];

    if (selectionActive && selectionMode.includes("points")) {
      entries.push({
        name: "click",
        handler: (params: any) => {
          setStateValue("selection", transformClickToSelection(params));
        },
      });

      // Double-click on blank canvas clears the selection (Plotly parity).
      // chart.on("click") never fires on empty space, so listen at the
      // zrender level (zr: prefix) and clear only when the double-click hit
      // no graphic element.
      entries.push({
        name: "zr:dblclick",
        handler: (e: any) => {
          if (!e.target) setStateValue("selection", EMPTY_SELECTION);
        },
      });
    }

    // Brush handlers for "box" and "lasso" modes
    // ECharts fires brushEnd (areas) BEFORE the final brushSelected (batch),
    // so we cache areas from brushEnd and trigger state from brushSelected.
    if (
      selectionActive &&
      (selectionMode.includes("box") || selectionMode.includes("lasso"))
    ) {
      let cachedAreas: any[] = [];

      entries.push({
        name: "brushEnd",
        handler: (params: any) => {
          cachedAreas = params.areas ?? [];
          if (cachedAreas.length === 0) {
            setStateValue("selection", EMPTY_SELECTION);
          }
        },
      });

      entries.push({
        name: "brushSelected",
        handler: (params: any) => {
          const batch = params.batch ?? [];
          if (cachedAreas.length === 0) return;
          setStateValue(
            "selection",
            transformBrushToSelection(batch, cachedAreas, chart),
          );
        },
      });
    }

    savedKey = key;
    savedHandlers = bindHandlers(chart, entries);
    return true;
  };
};

/**
 * Component-scoped state keyed by the host element to support multiple
 * instances.
 */
type ComponentState = {
  chart: echarts.ECharts | null;
  currentRenderer: "canvas" | "svg" | null;
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
      currentRenderer: null,
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
    replaceMerge,
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

  // 3. Resolve theme (memoized). A theme or renderer change requires a chart
  //    re-init, so dispose the existing chart and reset the memoized
  //    generators — stale references are cleared and options are re-applied
  //    to the new chart instance (preserving animations).
  const { themeName, themeChanged } = state.setTheme(theme, container);
  const rendererChanged = renderer !== state.currentRenderer;
  state.currentRenderer = renderer;

  if ((themeChanged || rendererChanged) && state.chart) {
    state.chart.dispose();
    state.chart = null;
    state.getOptions = getOptionsGenerator();
    state.setEvents = setEventsGenerator();
    state.setSelection = setSelectionGenerator();
  }

  // 4. Create chart if needed. If the previous instance was disposed outside
  //    the theme/renderer path above, the memoized generators still hold keys
  //    and handlers for the dead chart — reset them so options are re-applied
  //    and event/selection handlers are rebound on the fresh instance.
  if (state.chart?.isDisposed()) {
    state.chart = null;
    state.getOptions = getOptionsGenerator();
    state.setEvents = setEventsGenerator();
    state.setSelection = setSelectionGenerator();
  }
  if (!state.chart) {
    state.chart = echarts.init(container, themeName, { renderer });
  }

  // 5. Apply options if changed
  const { data: cleanOptions, hasChanged: optionsChanged } =
    state.getOptions(options);

  if (optionsChanged) {
    const setOptionOpts = replaceMerge ? { replaceMerge } : { notMerge: true };
    state.chart.setOption(cleanOptions!, setOptionOpts);
  }

  // 6. Wire events (memoized unbind/rebind)
  state.setEvents(state.chart, onEvents, setTriggerValue);

  // 6b. Wire selection listeners and overlay brush config. Apply on ANY
  //     selection-config change, not only when active — otherwise disabling
  //     selection (or switching to points-only) left the brush tool and drawn
  //     areas stale in the chart.
  const selectionChanged = state.setSelection(
    state.chart,
    selectionActive,
    selectionMode,
    setStateValue,
  );
  const wantBrush =
    selectionMode.includes("box") || selectionMode.includes("lasso");
  if (wantBrush) {
    // Merge brush + toolbox brush feature on top of the user's options so
    // any user-defined toolbox features are preserved. Re-applied not only
    // on selection-config changes but also whenever options were re-applied:
    // step 5's notMerge:true setOption wipes the previously merged brush
    // component and toolbox button.
    if (selectionChanged || optionsChanged) {
      state.chart.setOption(buildBrushOption(selectionMode), {
        notMerge: false,
      });
    }
  } else if (selectionChanged) {
    // No brush wanted: clear any drawn areas, then remove the brush
    // component via replaceMerge (a plain merge leaves it stale) while the
    // toolbox merge unsets its brush feature. User toolbox features survive.
    const current = state.chart.getOption() as { brush?: unknown[] };
    if (Array.isArray(current.brush) && current.brush.length > 0) {
      state.chart.dispatchAction({ type: "brush", areas: [] });
    }
    state.chart.setOption(buildBrushOption(selectionMode), {
      replaceMerge: ["brush"],
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
