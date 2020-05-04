import React from "react"
import {
  ComponentProps,
  StreamlitComponent,
  withStreamlitConnection,
} from "./streamlit"
import { isObject } from "lodash"

import echarts from "echarts"
import ReactEcharts from "echarts-for-react"

class EchartsChart extends StreamlitComponent {
  private customThemeName = "custom_theme"
  public constructor(props: ComponentProps) {
    super(props)

    const themeProp = props.args["theme"]
    if (isObject(themeProp)) {
      echarts.registerTheme(this.customThemeName, themeProp)
    }
  }

  public render = (): React.ReactNode => {
    const options = this.props.args["options"]
    const themeName = isObject(this.props.args["theme"])
      ? this.customThemeName
      : this.props.args["theme"]

    return <ReactEcharts option={options} theme={themeName} />
  }
}

export default withStreamlitConnection(EchartsChart)
