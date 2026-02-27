import type { ECharts, EChartsOption } from "echarts";

// --- Types ---

export interface SelectionPoint {
  point_index: number;
  series_index: number;
  series_name: string;
  x: number | string | null;
  y: number | string | null;
  value: number | string | null;
  name: string | null;
}

export interface SelectionBox {
  x_range: [number, number];
  y_range: [number, number];
}

export interface SelectionLasso {
  coordinates: [number, number][];
}

export interface SelectionData {
  points: SelectionPoint[];
  point_indices: number[];
  series_point_indices: Record<string, number[]>;
  box: SelectionBox[];
  lasso: SelectionLasso[];
}

export const EMPTY_SELECTION: SelectionData = {
  points: [],
  point_indices: [],
  series_point_indices: {},
  box: [],
  lasso: [],
};

// --- Click → Selection ---

export function transformClickToSelection(params: any): SelectionData {
  if (
    params.dataIndex == null ||
    params.componentType !== "series"
  ) {
    return EMPTY_SELECTION;
  }

  const point: SelectionPoint = buildPointFromDataItem(
    params.data,
    params.dataIndex,
    params.seriesIndex ?? 0,
    params.seriesName ?? "",
  );

  return {
    points: [point],
    point_indices: [params.dataIndex],
    series_point_indices: { [params.seriesName ?? ""]: [params.dataIndex] },
    box: [],
    lasso: [],
  };
}

// --- Brush → Selection ---

export function transformBrushToSelection(
  cachedBatch: any[],
  brushEndAreas: any[],
  chart: ECharts,
): SelectionData {
  const chartOption = chart.getOption() as EChartsOption;

  // Phase 1: Extract selected points from brushSelected batch
  const points: SelectionPoint[] = [];
  const flatIndices = new Set<number>();
  const seriesPointIndices: Record<string, number[]> = {};

  for (const batchItem of cachedBatch) {
    const selected: { seriesIndex: number; dataIndex: number[] }[] =
      batchItem.selected ?? [];

    for (const sel of selected) {
      const seriesIdx = sel.seriesIndex;
      const seriesArr = Array.isArray(chartOption.series)
        ? chartOption.series
        : [];
      const seriesName =
        (seriesArr[seriesIdx] as any)?.name ?? String(seriesIdx);

      for (const dataIdx of sel.dataIndex) {
        const dataItem = resolveDataItem(chartOption, seriesIdx, dataIdx);
        if (dataItem != null) {
          points.push(
            buildPointFromDataItem(dataItem, dataIdx, seriesIdx, seriesName),
          );
        }

        flatIndices.add(dataIdx);
        if (!seriesPointIndices[seriesName]) {
          seriesPointIndices[seriesName] = [];
        }
        seriesPointIndices[seriesName].push(dataIdx);
      }
    }
  }

  // Phase 2: Convert brush areas from pixel to axis coordinates
  const boxes: SelectionBox[] = [];
  const lassos: SelectionLasso[] = [];

  for (const area of brushEndAreas) {
    if (area.brushType === "rect") {
      const converted = convertRectArea(area, chart, chartOption);
      if (converted) boxes.push(converted);
    } else if (area.brushType === "polygon") {
      const converted = convertPolygonArea(area, chart, chartOption);
      if (converted) lassos.push(converted);
    }
  }

  return {
    points,
    point_indices: [...flatIndices].sort((a, b) => a - b),
    series_point_indices: seriesPointIndices,
    box: boxes,
    lasso: lassos,
  };
}

// --- Brush option builder ---

export function buildBrushOption(
  selectionMode: string[],
): Record<string, any> {
  const hasBrush =
    selectionMode.includes("box") || selectionMode.includes("lasso");

  if (!hasBrush) {
    return {
      brush: [],
      toolbox: { feature: { brush: undefined } },
    };
  }

  const shapeTypes: string[] = [];
  if (selectionMode.includes("box")) shapeTypes.push("rect");
  if (selectionMode.includes("lasso")) shapeTypes.push("polygon");

  return {
    brush: {
      toolbox: [...shapeTypes, "clear"],
      xAxisIndex: "all",
      yAxisIndex: "all",
      throttleType: "debounce",
      throttleDelay: 200,
      brushStyle: {
        borderWidth: 1,
        color: "rgba(120,140,180,0.15)",
        borderColor: "rgba(120,140,180,0.5)",
      },
    },
    toolbox: {
      feature: {
        brush: {
          type: shapeTypes,
        },
      },
    },
  };
}

// --- Helpers ---

export function resolveDataItem(
  chartOption: EChartsOption,
  seriesIdx: number,
  dataIdx: number,
): any {
  const seriesArr = Array.isArray(chartOption.series)
    ? chartOption.series
    : [];
  const series = seriesArr[seriesIdx] as any;

  // Try series.data first
  if (series?.data && Array.isArray(series.data) && series.data[dataIdx] != null) {
    return series.data[dataIdx];
  }

  // Try dataset
  const datasetIndex = series?.datasetIndex ?? 0;
  const datasets = Array.isArray(chartOption.dataset)
    ? chartOption.dataset
    : chartOption.dataset
      ? [chartOption.dataset]
      : [];
  const dataset = datasets[datasetIndex] as any;
  if (dataset?.source && Array.isArray(dataset.source) && dataset.source[dataIdx] != null) {
    return dataset.source[dataIdx];
  }

  return null;
}

export function buildPointFromDataItem(
  dataItem: any,
  dataIdx: number,
  seriesIdx: number,
  seriesName: string,
): SelectionPoint {
  // Array format: [x, y] or [x, y, ...]
  if (Array.isArray(dataItem)) {
    return {
      point_index: dataIdx,
      series_index: seriesIdx,
      series_name: seriesName,
      x: dataItem[0] ?? null,
      y: dataItem[1] ?? null,
      value: dataItem[1] ?? dataItem[0] ?? null,
      name: null,
    };
  }

  // Object format: { name, value, ... }
  if (typeof dataItem === "object" && dataItem !== null) {
    return {
      point_index: dataIdx,
      series_index: seriesIdx,
      series_name: seriesName,
      x: dataItem.x ?? null,
      y: dataItem.y ?? null,
      value: dataItem.value ?? null,
      name: dataItem.name ?? null,
    };
  }

  // Scalar format
  return {
    point_index: dataIdx,
    series_index: seriesIdx,
    series_name: seriesName,
    x: dataIdx,
    y: dataItem,
    value: dataItem,
    name: null,
  };
}

function buildFinder(
  area: any,
  chartOption: EChartsOption,
): Record<string, any> {
  // Check for geo chart
  const geo = (chartOption as any).geo;
  if (geo && (Array.isArray(geo) ? geo.length > 0 : true)) {
    return { geoIndex: 0 };
  }

  // Parse grid index from area
  const gridIndex =
    area.panelId != null ? parseInt(String(area.panelId), 10) : 0;
  return { gridIndex: isNaN(gridIndex) ? 0 : gridIndex };
}

function convertRectArea(
  area: any,
  chart: ECharts,
  chartOption: EChartsOption,
): SelectionBox | null {
  const range = area.range;
  if (!range || !Array.isArray(range) || range.length < 2) return null;

  const finder = buildFinder(area, chartOption);

  try {
    const min = chart.convertFromPixel(finder, [range[0][0], range[1][0]]);
    const max = chart.convertFromPixel(finder, [range[0][1], range[1][1]]);
    return {
      x_range: [min[0], max[0]],
      y_range: [min[1], max[1]],
    };
  } catch {
    // Fallback to raw pixel coordinates for unsupported coord systems
    return {
      x_range: [range[0][0], range[0][1]],
      y_range: [range[1][0], range[1][1]],
    };
  }
}

function convertPolygonArea(
  area: any,
  chart: ECharts,
  chartOption: EChartsOption,
): SelectionLasso | null {
  const range = area.range;
  if (!range || !Array.isArray(range)) return null;

  const finder = buildFinder(area, chartOption);

  try {
    const coordinates: [number, number][] = range.map(
      (point: number[]) =>
        chart.convertFromPixel(finder, point) as [number, number],
    );
    return { coordinates };
  } catch {
    // Fallback to raw pixel coordinates
    return { coordinates: range as [number, number][] };
  }
}
