import React from "react"
import {
  ComponentProps,
  Streamlit,
  withStreamlitConnection,
} from "streamlit-component-lib"
import { isObject } from "lodash"

import echarts from "echarts"
import "echarts-gl"
import "echarts-liquidfill"
import "echarts-wordcloud"
import "echarts/map/js/china.js"
import ReactEcharts from "echarts-for-react"

import deepMap from "./utils"

/**
 * Arguments Streamlit receives from the Python side
 */
interface PythonArgs {
  options: object
  theme: string | object
  onEvents: object
  height: string
  width: string
  renderer: "canvas" | "svg"
}

const EchartsChart = (props: ComponentProps) => {
  const JS_PLACEHOLDER = "--x_x--0_0--"

  const registerTheme = (themeProp: string | object) => {
    const customThemeName = "custom_theme"
    if (isObject(themeProp)) {
      echarts.registerTheme(customThemeName, themeProp)
    }
    return isObject(themeProp) ? customThemeName : themeProp
  }

  const convertJavascriptCode = (obj: object) => {
    let funcReg = new RegExp(
      `${JS_PLACEHOLDER}\\s*(function\\s*.*)\\s*${JS_PLACEHOLDER}`
    )

    // Look in all nested values of options for Pyecharts Javascript placeholder
    return deepMap(obj, function (v: string) {
      let match = funcReg.exec(v)
      if (match) {
        const funcStr = match[1]
        return new Function("return " + funcStr)()
      } else {
        return v
      }
    })
  }

  const {
    options,
    theme,
    onEvents,
    height,
    width,
    renderer,
  }: PythonArgs = props.args
  const cleanTheme = registerTheme(theme)
  const cleanOptions = convertJavascriptCode(options)
  const cleanOnEvents = convertJavascriptCode(onEvents)

  return (
    <>
      <ReactEcharts
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
