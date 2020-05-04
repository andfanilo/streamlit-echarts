import React from "react"
import {ComponentProps, StreamlitComponent, withStreamlitConnection} from "./streamlit"

import ReactEcharts from "echarts-for-react";

class EchartsChart extends StreamlitComponent {
    public constructor(props: ComponentProps) {
        super(props);
    }

    public render = (): React.ReactNode => {

        const options = this.props.args["options"]
        return (
            <ReactEcharts option={options} />
        )
    }
}

export default withStreamlitConnection(EchartsChart)
