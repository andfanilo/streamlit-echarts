import React from "react"
import { ComponentProps, Streamlit, withStreamlitConnection } from "./streamlit"
import { isObject } from "lodash"

import echarts from "echarts"
import ReactEcharts from "echarts-for-react"

import "./streamlit.css"

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
    return isObject(props.args["theme"]) ? customThemeName : props.args["theme"]
  }

  const themeName = getThemeName(props.args["theme"])
  const options = props.args["options"]

  return (
    <>
      <ReactEcharts
        option={options}
        theme={themeName}
        onChartReady={() => {
          Streamlit.setFrameHeight()
        }}
      />
    </>
  )
}

export default withStreamlitConnection(EchartsChart)
