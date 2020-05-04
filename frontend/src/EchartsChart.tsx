import React from "react"
import {ComponentProps, StreamlitComponent, withStreamlitConnection} from "./streamlit"

import ReactEcharts from "echarts-for-react";

class EchartsChart extends StreamlitComponent {
    public constructor(props: ComponentProps) {
        super(props);
    }

    public render = (): React.ReactNode => {

        const options = this.props.args["options"]
        const theme = this.props.args["theme"]
        return (
            <ReactEcharts
              option={options}
              theme={theme}
            />
        )
    }
}

export default withStreamlitConnection(EchartsChart)
