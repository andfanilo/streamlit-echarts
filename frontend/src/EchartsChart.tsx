import React from "react"
import { ComponentProps, StreamlitComponent, withStreamlitConnection } from "./streamlit"
import * as _ from "lodash"
import deepMapValues from "./utils"

import echarts from "echarts"
import ReactEcharts from "echarts-for-react"

class EchartsChart extends StreamlitComponent {
  private customThemeName = "custom_theme"

  private mapFunctions = (obj: object) => {
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

  public constructor(props: ComponentProps) {
    super(props)

    const themeProp = props.args["theme"]
    if (_.isObject(themeProp)) {
      echarts.registerTheme(this.customThemeName, themeProp)
    }
  }

  public render = (): React.ReactNode => {
    const options = this.props.args["options"]
    const themeName = _.isObject(this.props.args["theme"])
      ? this.customThemeName
      : this.props.args["theme"]

    /*
    let fn = options["series"][0]["itemStyle"]["color"]
    fn = new Function("return " + fn)()
    options["series"][1]["itemStyle"]["color"] = fn
     */
    return <ReactEcharts option={options} theme={themeName}/>
  }
}

export default withStreamlitConnection(EchartsChart)
