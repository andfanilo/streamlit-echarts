import React, { FC, useMemo, useRef } from "react";
import { FrontendRendererArgs } from "@streamlit/component-v2-lib";
import { isObject } from "lodash";

import * as echarts from "echarts";
import "echarts-gl";
import "echarts-liquidfill";
import "echarts-wordcloud";
import ReactEcharts, { EChartsOption } from "echarts-for-react";

import deepMap from "./utils";

interface Map {
  mapName: string;
  geoJson: any;
  specialAreas: any;
}

export type EchartsStateShape = {
  chart_event?: any;
};

export type EchartsDataShape = {
  options: EChartsOption;
  theme: string | object;
  onEvents: Record<string, string>;
  height: string;
  width: string;
  renderer: "canvas" | "svg";
  map: Map | null;
};

type Props = Pick<
  FrontendRendererArgs<EchartsStateShape, EchartsDataShape>,
  "setStateValue" | "setTriggerValue"
> &
  EchartsDataShape;

const EchartsChart: FC<Props> = ({
  options,
  theme,
  onEvents,
  height,
  width,
  renderer,
  map,
  setStateValue,
  setTriggerValue,
}) => {
  const echartsElementRef = useRef<ReactEcharts>(null);
  const JS_PLACEHOLDER = "--x_x--0_0--";

  const registerTheme = (themeProp: string | object) => {
    const customThemeName = "custom_theme";

    // Built-in "streamlit" theme: reads CSS variables set by Streamlit
    // so the chart automatically adapts to light/dark mode.
    if (themeProp === "streamlit") {
      // Read from the chart element itself (matches streamlit-bokeh pattern).
      // Falls back to document.body on first render before the ref is attached.
      const containerEl = echartsElementRef.current?.ele ?? document.body;
      const style = getComputedStyle(containerEl);
      const getCssVar = (v: string) => style.getPropertyValue(v).trim();

      const backgroundColor = getCssVar("--st-background-color");
      const textColor = getCssVar("--st-text-color");
      const font = getCssVar("--st-font");

      const stTheme = {
        color: [
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
        ],
        backgroundColor: backgroundColor || "transparent",
        textStyle: {
          color: textColor || "#31333F",
          fontFamily: font || undefined,
        },
        title: { textStyle: { color: textColor || "#31333F" } },
        legend: { textStyle: { color: textColor || "#31333F" } },
        categoryAxis: { axisLabel: { color: textColor || "#31333F" } },
        valueAxis: { axisLabel: { color: textColor || "#31333F" } },
      };
      echarts.registerTheme("streamlit", stTheme);
      return "streamlit";
    }

    if (isObject(themeProp)) {
      echarts.registerTheme(customThemeName, themeProp);
    }
    return isObject(themeProp) ? customThemeName : themeProp;
  };

  /**
   * If string can be evaluated as a Function, return activated function. Else return string.
   * @param s string to evaluate to function
   * @returns Function if can be evaluated as one, else input string
   */
  const evalStringToFunction = (s: string) => {
    let funcReg = new RegExp(
      `${JS_PLACEHOLDER}\\s*(function\\s*.*)\\s*${JS_PLACEHOLDER}`,
    );
    let match = funcReg.exec(s);
    if (match) {
      const funcStr = match[1];
      return new Function("return " + funcStr)();
    } else {
      return s;
    }
  };

  /**
   * Deep map all values in an object to evaluate all strings as functions
   * We use this to look in all nested values of options for Pyecharts Javascript placeholder
   * @param obj object to deep map on
   * @returns object with all functions in values evaluated
   */
  const evalStringToFunctionDeepMap = (obj: object) => {
    return deepMap(obj, evalStringToFunction, {});
  };

  const cleanTheme = registerTheme(theme);

  if (isObject(map)) {
    echarts.registerMap(map.mapName, map.geoJson, map.specialAreas);
  }

  // no need for memo, react-echarts uses fast-deep-equal to compare option/event change and update on change
  const cleanOptions = evalStringToFunctionDeepMap(options);

  // Build event handler map. useMemo avoids re-creating handlers on every render.
  // Note: useCallback cannot be called inside a forEach (Rules of Hooks), so we
  // use a single useMemo for the entire events object instead.
  const cleanOnEvents = useMemo<Record<string, Function>>(() => {
    const result: Record<string, Function> = {};
    Object.keys(onEvents).forEach((eventKey) => {
      const eventFunction = onEvents[eventKey];
      result[eventKey] = (params: any) => {
        const s = evalStringToFunction(eventFunction)(params);
        setTriggerValue("chart_event", s);
      };
    });
    return result;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [onEvents, setTriggerValue]);

  return (
    <ReactEcharts
      ref={echartsElementRef}
      option={cleanOptions}
      notMerge={true}
      lazyUpdate={true}
      style={{ height: height, width: width }}
      theme={cleanTheme}
      onEvents={cleanOnEvents}
      opts={{ renderer: renderer }}
    />
  );
};

export default EchartsChart;
