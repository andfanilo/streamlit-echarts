import React from "react"
import { ComponentProps, Streamlit, withStreamlitConnection } from "./streamlit"
import { isObject } from "lodash"

import echarts from "echarts"
import ReactEcharts from "echarts-for-react"

import deepMap from "./utils"

/**
 * Arguments Streamlit receives from the Python side
 */
interface PythonArgs {
    options: object
    theme: string | object
}

const EchartsChart = (props: ComponentProps) => {
  /**
   * Deal with theme
   * If theme prop is an object, register it under "custom_theme" name
   * If it's a string just return it
   * If it's None, ECharts component will take care of it
   */
  const getThemeName = (themeProp: string | object) => {
    const customThemeName = "custom_theme"
    if (isObject(themeProp)) {
      echarts.registerTheme(customThemeName, themeProp)
    }
    return isObject(themeProp) ? customThemeName : themeProp
  }

  const mapOptionValues = (obj: object) => {
    // Map over all values in options
    // cast strings as functions when specific pyecharts JS placeholder found
    let funcReg = new RegExp("--x_x--0_0--\\s*(function\\s*.*)\\s*--x_x--0_0--")

    return deepMap(obj, function (v: string) {
      //v = v.replace(/(\r\n|\n|\r)/g, "")
      let match = funcReg.exec(v)
      if (match) {
        const funcStr = match[1]
        return new Function("return " + funcStr)()
      } else {
        return v
      }
    })
  }

  const {options, theme}: PythonArgs = props.args
  const cleanTheme = getThemeName(theme)
  const cleanOptions = mapOptionValues(options)

  return (
    <>
      <ReactEcharts
        option={cleanOptions}
        theme={cleanTheme}
        onChartReady={() => {
          Streamlit.setFrameHeight()
        }}
      />
    </>
  )
}

export default withStreamlitConnection(EchartsChart)
