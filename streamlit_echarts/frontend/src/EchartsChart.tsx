import React, { useCallback, useEffect, useRef } from "react"
import {
  ComponentProps,
  Streamlit,
  withStreamlitConnection,
} from "streamlit-component-lib"
import { isObject, mapValues } from "lodash"

import * as echarts from "echarts"
import "echarts-gl"
import "echarts-liquidfill"
import "echarts-wordcloud"
import ReactEcharts, { EChartsOption } from "echarts-for-react"

import deepMap from "./utils"

interface Map {
  mapName: string
  geoJson: object
  specialAreas: object
}

/**
 * Arguments Streamlit receives from the Python side
 */
interface PythonArgs {
  options: EChartsOption
  theme: string | object
  onEvents: any
  height: string
  width: string
  renderer: "canvas" | "svg"
  map: Map
}

const EchartsChart = (props: ComponentProps) => {
  const echartsElementRef = useRef<ReactEcharts>(null)
  const echartsInstanceRef = useRef()
  const JS_PLACEHOLDER = "--x_x--0_0--"

  const registerTheme = (themeProp: string | object) => {
    const customThemeName = "custom_theme"
    if (isObject(themeProp)) {
      echarts.registerTheme(customThemeName, themeProp)
    }
    return isObject(themeProp) ? customThemeName : themeProp
  }

  /**
   * If string can be evaluated as a Function, return activated function. Else return string.
   * @param s string to evaluate to function
   * @returns Function if can be evaluated as one, else input string
   */
  const evalStringToFunction = (s: string) => {
    let funcReg = new RegExp(
      `${JS_PLACEHOLDER}\\s*(function\\s*.*)\\s*${JS_PLACEHOLDER}`
    )
    let match = funcReg.exec(s)
    if (match) {
      const funcStr = match[1]
      return new Function("return " + funcStr)()
    } else {
      return s
    }
  }

  /**
   * Deep map all values in an object to evaluate all strings as functions
   * We use this to look in all nested values of options for Pyecharts Javascript placeholder
   * @param obj object to deep map on
   * @returns object with all functions in values evaluated
   */
  const evalStringToFunctionDeepMap = (obj: object) => {
    return deepMap(obj, evalStringToFunction, {})
  }

  const {
    options,
    theme,
    onEvents,
    height,
    width,
    renderer,
    map,
  }: PythonArgs = props.args
  const cleanTheme = registerTheme(theme)

  if (isObject(map)) {
    echarts.registerMap(map.mapName, map.geoJson, map.specialAreas)
  }

  // no need for memo, react-echarts uses fast-deep-equal to compare option/event change and update on change
  const cleanOptions = evalStringToFunctionDeepMap(options)
  const cleanOnEvents: any = {}
  Object.keys(onEvents).map((key: string) => {
    const eventFunction = onEvents[key]
    cleanOnEvents[key] = useCallback(
      (params: any) => {
        const s = evalStringToFunction(eventFunction)(params)
        Streamlit.setComponentValue(s)
      },
      [eventFunction]
    )
  })

  useEffect(() => {
    if (null === echartsElementRef.current) {
      return
    }

    echartsInstanceRef.current = echartsElementRef.current.getEchartsInstance()
  })

  return (
    <>
      <ReactEcharts
        ref={echartsElementRef}
        option={cleanOptions}
        notMerge={true}
        lazyUpdate={true}
        style={{ height: height, width: width }}
        theme={cleanTheme}
        onChartReady={() => {
          Streamlit.setFrameHeight()
        }}
        onEvents={cleanOnEvents}
        opts={{ renderer: renderer }}
      />
    </>
  )
}

export default withStreamlitConnection(EchartsChart)
