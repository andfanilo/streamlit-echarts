import React from "react"
import {
  ComponentProps,
  Streamlit,
  withStreamlitConnection,
} from "streamlit-component-lib"
import { isObject } from "lodash"

import * as echarts from "echarts"
import "echarts-gl"
import "echarts-liquidfill"
import "echarts-wordcloud"
import ReactEcharts from "echarts-for-react"

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
  options: object
  theme: string | object
  onEvents: object
  height: string
  width: string
  renderer: "canvas" | "svg"
  map: Map
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
        // eslint-disable-next-line
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
    map,
  }: PythonArgs = props.args
  const cleanTheme = registerTheme(theme)

  if (isObject(map)) {
   // echarts.registerMap(map.mapName, map.geoJson, map.specialAreas)

  }

  const cleanOptions = convertJavascriptCode(options)
  const cleanOnEvents = convertJavascriptCode(onEvents)

  /*
  add support for event back to python
  usage at python side:
  events={
    "click": "function(params) { return params.name }",
    "dblclick":"function(params) { return params.value }"
  }
  s=st_pyecharts(b,events=events)
   */
  const keys=Object.keys(cleanOnEvents)
  const getReturnOfcleanOnEvents:any={}
  keys.forEach(
    function(key){
      getReturnOfcleanOnEvents[key]=(params:any)=>{            
            const s=cleanOnEvents[key](params)            
            Streamlit.setComponentValue(s)
        }      
    }
  )

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
        onEvents={getReturnOfcleanOnEvents}
        opts={{ renderer: renderer }}
      />
    </>
  )
}

export default withStreamlitConnection(EchartsChart)
