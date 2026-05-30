import { describe, expect, test, beforeEach, afterEach } from "vitest";
import * as echarts from "echarts";
import { buildBrushOption } from "./selection";

// Real-echarts verification (SVG renderer works in jsdom without canvas) that
// the brush enable/clear options behave as index.ts relies on. Regression for
// the bug where disabling selection left stale brush component + toolbox UI.
describe("brush enable/clear with real echarts", () => {
  let container: HTMLDivElement;
  let chart: echarts.ECharts;

  beforeEach(() => {
    container = document.createElement("div");
    container.style.width = "400px";
    container.style.height = "300px";
    document.body.appendChild(container);
    chart = echarts.init(container, null, {
      renderer: "svg",
      width: 400,
      height: 300,
    });
    chart.setOption({
      xAxis: { type: "value" },
      yAxis: { type: "value" },
      series: [
        {
          type: "scatter",
          data: [
            [1, 2],
            [3, 4],
          ],
        },
      ],
    });
  });

  afterEach(() => {
    chart.dispose();
    container.remove();
  });

  test("enabling adds brush component + toolbox brush button", () => {
    chart.setOption(buildBrushOption(["box", "lasso"]), { notMerge: false });
    const opt = chart.getOption() as any;

    expect(opt.brush?.length).toBeGreaterThan(0);
    expect(opt.toolbox?.[0]?.feature?.brush?.type).toEqual([
      "rect",
      "polygon",
      "clear",
    ]);
  });

  test("disabling via replaceMerge removes brush component + toolbox button", () => {
    chart.setOption(buildBrushOption(["box", "lasso"]), { notMerge: false });
    // Clear path used by index.ts when no brush mode is wanted.
    chart.setOption(buildBrushOption([]), { replaceMerge: ["brush"] });
    const opt = chart.getOption() as any;

    expect(opt.brush ?? []).toEqual([]);
    expect(opt.toolbox?.[0]?.feature?.brush).toBeUndefined();
  });

  test("plain merge clear leaves brush component stale (documents why replaceMerge)", () => {
    chart.setOption(buildBrushOption(["box"]), { notMerge: false });
    chart.setOption(buildBrushOption([]), { notMerge: false });
    const opt = chart.getOption() as any;

    // A plain merge does NOT remove the brush component — hence replaceMerge.
    expect(opt.brush?.length).toBeGreaterThan(0);
  });

  test("clearing preserves user-defined toolbox features", () => {
    chart.setOption({ toolbox: { feature: { saveAsImage: {} } } });
    chart.setOption(buildBrushOption(["box"]), { notMerge: false });
    chart.setOption(buildBrushOption([]), { replaceMerge: ["brush"] });
    const opt = chart.getOption() as any;

    expect(opt.toolbox?.[0]?.feature?.saveAsImage).toBeTruthy();
    expect(opt.toolbox?.[0]?.feature?.brush).toBeUndefined();
  });
});
