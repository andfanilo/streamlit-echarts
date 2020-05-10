import React from "react"
import { ComponentProps, Streamlit, withStreamlitConnection } from "./streamlit"
import * as _ from "lodash"

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
    if (_.isObject(themeProp)) {
      echarts.registerTheme(customThemeName, themeProp)
    }
    return _.isObject(props.args["theme"])
      ? customThemeName
      : props.args["theme"]
  }
  const themeName = getThemeName(props.args["theme"])

  /*
  const mapFunctions = (obj: object) => {
    // Map over all strings in options, cast as functions when found
    let funcReg = /function *\(([^()]*)\)[ \n\t]*{(.*)}/gim

    return deepMapValues(obj, function(v: string) {
      let match = funcReg.exec(v.replace(/\n/g, " "))
      if (match) {
        // @ts-ignore
        return new Function(match[1].split(","), match[2])
      }
      return v
      //return _.isFunction(v) ? new Function("return " + v)() : v
    })
  }

  let fn = options["series"][0]["itemStyle"]["color"]
  fn = new Function("return " + fn)()
  options["series"][1]["itemStyle"]["color"] = fn
   */
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
