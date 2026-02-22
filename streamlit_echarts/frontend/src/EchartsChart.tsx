import React, { FC, useMemo, useRef } from "react";
import { FrontendRendererArgs } from "@streamlit/component-v2-lib";
import { isObject } from "lodash";

import * as echarts from "echarts";
import "echarts-gl";
import "echarts-liquidfill";
import "echarts-wordcloud";
import ReactEcharts, { EChartsOption } from "echarts-for-react";

import deepMap from "./utils";
import { evalStringToFunction } from "./parsers";

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
  const containerRef = useRef<HTMLDivElement>(null);

  // Read Streamlit CSS vars from whichever element is available.
  const getCssVar = (v: string) => {
    const el =
      (echartsElementRef.current?.ele as HTMLElement | null) ??
      containerRef.current ??
      document.body;
    return getComputedStyle(el).getPropertyValue(v).trim();
  };

  // Read CSS vars needed for the "streamlit" theme.
  // These are the inputs that determine whether we need to re-register.
  const backgroundColor =
    theme === "streamlit" ? getCssVar("--st-background-color") : "";
  const textColor = theme === "streamlit" ? getCssVar("--st-text-color") : "";
  const font = theme === "streamlit" ? getCssVar("--st-font") : "";

  /**
   * Memoized theme registration. echarts.registerTheme is only called when the
   * theme prop or the resolved Streamlit CSS variable values actually change.
   */
  const cleanTheme = useMemo<string>(() => {
    const customThemeName = "custom_theme";

    if (theme === "streamlit") {
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

    if (isObject(theme)) {
      echarts.registerTheme(customThemeName, theme);
      return customThemeName;
    }

    return theme as string;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [theme, backgroundColor, textColor, font]);

  if (isObject(map)) {
    echarts.registerMap(map.mapName, map.geoJson, map.specialAreas);
  }

  /**
   * Memoized options parsing. The deepMap + evalStringToFunction pipeline
   * (regex + new Function) runs only when the serialized options actually
   * change, skipping the work on every Streamlit rerun when options are
   * identical.
   */
  // eslint-disable-next-line react-hooks/exhaustive-deps
  const cleanOptions = useMemo(
    () => deepMap(options, evalStringToFunction, {}),
    // JSON.stringify lets us do a deep-equality check as the memo key.
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [JSON.stringify(options)],
  );

  // Build event handler map. useMemo avoids re-creating handlers on every render.
  // Note: useCallback cannot be called inside a forEach (Rules of Hooks), so we
  // use a single useMemo for the entire events object instead.
  const cleanOnEvents = useMemo<Record<string, Function>>(() => {
    const result: Record<string, Function> = {};
    Object.keys(onEvents).forEach((eventKey) => {
      const eventFunction = onEvents[eventKey];
      result[eventKey] = (params: any) => {
        const s = (evalStringToFunction(eventFunction) as Function)(params);
        setTriggerValue("chart_event", s);
      };
    });
    return result;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [onEvents, setTriggerValue]);

  return (
    <div ref={containerRef}>
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
    </div>
  );
};

export default EchartsChart;
