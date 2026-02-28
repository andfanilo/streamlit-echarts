import { describe, expect, test, vi } from "vitest";
import {
  transformClickToSelection,
  transformBrushToSelection,
  buildBrushOption,
  EMPTY_SELECTION,
  resolveDataItem,
  buildPointFromDataItem,
} from "./selection";

// --- transformClickToSelection ---

describe("transformClickToSelection", () => {
  test("returns selection for a data point click", () => {
    const params = {
      componentType: "series",
      dataIndex: 2,
      seriesIndex: 0,
      seriesName: "Sales",
      data: 150,
    };
    const result = transformClickToSelection(params);

    expect(result.points).toHaveLength(1);
    expect(result.points[0]).toEqual({
      point_index: 2,
      series_index: 0,
      series_name: "Sales",
      x: 2,
      y: 150,
      value: 150,
      name: null,
    });
    expect(result.point_indices).toEqual([2]);
    expect(result.series_point_indices).toEqual({ Sales: [2] });
    expect(result.box).toEqual([]);
    expect(result.lasso).toEqual([]);
  });

  test("returns EMPTY_SELECTION on background click (dataIndex null)", () => {
    const params = { componentType: "series", dataIndex: null };
    const result = transformClickToSelection(params);
    expect(result).toBe(EMPTY_SELECTION);
    // Verify EMPTY_SELECTION shape
    expect(result).toEqual({
      points: [],
      point_indices: [],
      series_point_indices: {},
      box: [],
      lasso: [],
    });
  });

  test("returns EMPTY_SELECTION for non-series component", () => {
    const params = { componentType: "title", dataIndex: 0 };
    expect(transformClickToSelection(params)).toBe(EMPTY_SELECTION);
  });

  test("handles pie chart object data item", () => {
    const params = {
      componentType: "series",
      dataIndex: 1,
      seriesIndex: 0,
      seriesName: "Pie",
      data: { name: "Category A", value: 42 },
    };
    const result = transformClickToSelection(params);

    expect(result.points[0].name).toBe("Category A");
    expect(result.points[0].value).toBe(42);
  });

  test("handles scatter chart array data item", () => {
    const params = {
      componentType: "series",
      dataIndex: 0,
      seriesIndex: 1,
      seriesName: "Scatter",
      data: [10, 20],
    };
    const result = transformClickToSelection(params);

    expect(result.points[0].x).toBe(10);
    expect(result.points[0].y).toBe(20);
    expect(result.points[0].series_index).toBe(1);
  });

  test("handles missing seriesIndex and seriesName", () => {
    const params = {
      componentType: "series",
      dataIndex: 0,
      data: 100,
    };
    const result = transformClickToSelection(params);

    expect(result.points[0].series_index).toBe(0);
    expect(result.points[0].series_name).toBe("");
    expect(result.point_indices).toEqual([0]);
    expect(result.series_point_indices).toEqual({ "": [0] });
  });
});

// --- transformBrushToSelection ---

describe("transformBrushToSelection", () => {
  const mockChart = (series: any[] = [], dataset: any[] = []) => ({
    getOption: vi.fn(() => ({ series, dataset })),
    convertFromPixel: vi.fn((_finder: any, point: number[]) => [
      point[0] * 2,
      point[1] * 2,
    ]),
  });

  test("extracts points from rect brush multi-point selection", () => {
    const chart = mockChart([{ name: "S0", data: [10, 20, 30] }]);
    const batch = [
      {
        selected: [{ seriesIndex: 0, dataIndex: [0, 2] }],
      },
    ];
    const areas = [
      {
        brushType: "rect",
        range: [
          [100, 200],
          [50, 150],
        ],
      },
    ];

    const result = transformBrushToSelection(batch, areas, chart as any);

    expect(result.points).toHaveLength(2);
    expect(result.points[0].value).toBe(10);
    expect(result.points[1].value).toBe(30);
    expect(result.point_indices).toEqual([0, 2]);
    expect(result.series_point_indices).toEqual({ S0: [0, 2] });
    expect(result.box).toHaveLength(1);
  });

  test("handles polygon brush", () => {
    const chart = mockChart([{ name: "S0", data: [5] }]);
    const batch = [{ selected: [{ seriesIndex: 0, dataIndex: [0] }] }];
    const areas = [
      {
        brushType: "polygon",
        range: [
          [10, 20],
          [30, 40],
          [50, 60],
        ],
      },
    ];

    const result = transformBrushToSelection(batch, areas, chart as any);

    expect(result.lasso).toHaveLength(1);
    expect(result.lasso[0].coordinates).toEqual([
      [20, 40],
      [60, 80],
      [100, 120],
    ]);
  });

  test("returns empty on empty batch", () => {
    const chart = mockChart();
    const result = transformBrushToSelection([], [], chart as any);

    expect(result.points).toEqual([]);
    expect(result.box).toEqual([]);
    expect(result.lasso).toEqual([]);
  });

  test("handles multi-series brush selection", () => {
    const chart = mockChart([
      { name: "A", data: [100, 200] },
      { name: "B", data: [300, 400] },
    ]);
    const batch = [
      {
        selected: [
          { seriesIndex: 0, dataIndex: [1] },
          { seriesIndex: 1, dataIndex: [0] },
        ],
      },
    ];

    const result = transformBrushToSelection(batch, [], chart as any);

    expect(result.points).toHaveLength(2);
    expect(result.point_indices).toEqual([0, 1]);
    expect(result.series_point_indices).toEqual({ A: [1], B: [0] });
  });

  test("handles dataset mode via resolveDataItem", () => {
    const chart = mockChart(
      [{ name: "DS", datasetIndex: 0 }],
      [
        {
          source: [
            [1, 2],
            [3, 4],
          ],
        },
      ],
    );
    const batch = [{ selected: [{ seriesIndex: 0, dataIndex: [1] }] }];

    const result = transformBrushToSelection(batch, [], chart as any);

    expect(result.points).toHaveLength(1);
    expect(result.points[0].x).toBe(3);
    expect(result.points[0].y).toBe(4);
  });

  test("handles scalar data items", () => {
    const chart = mockChart([{ name: "Line", data: [42] }]);
    const batch = [{ selected: [{ seriesIndex: 0, dataIndex: [0] }] }];

    const result = transformBrushToSelection(batch, [], chart as any);

    expect(result.points[0].value).toBe(42);
    expect(result.points[0].x).toBe(0);
    expect(result.points[0].y).toBe(42);
  });

  test("skips null data items", () => {
    const chart = mockChart([{ name: "S", data: [null, 10] }]);
    const batch = [{ selected: [{ seriesIndex: 0, dataIndex: [0, 1] }] }];

    const result = transformBrushToSelection(batch, [], chart as any);

    // null item is skipped, only index 1 produces a point
    expect(result.points).toHaveLength(1);
    expect(result.points[0].point_index).toBe(1);
    // Both indices still recorded in point_indices
    expect(result.point_indices).toEqual([0, 1]);
    expect(result.series_point_indices).toEqual({ S: [0, 1] });
  });
});

// --- buildBrushOption ---

describe("buildBrushOption", () => {
  test("box-only returns rect brush", () => {
    const result = buildBrushOption(["points", "box"]);

    expect(result.brush.toolbox).toEqual(["rect", "clear"]);
    expect(result.toolbox.feature.brush.type).toEqual(["rect"]);
  });

  test("lasso-only returns polygon brush", () => {
    const result = buildBrushOption(["lasso"]);

    expect(result.brush.toolbox).toEqual(["polygon", "clear"]);
  });

  test("box + lasso returns both brush types", () => {
    const result = buildBrushOption(["box", "lasso"]);

    expect(result.brush.toolbox).toEqual(["rect", "polygon", "clear"]);
    expect(result.toolbox.feature.brush.type).toEqual(["rect", "polygon"]);
  });

  test("points-only clears brush config", () => {
    const result = buildBrushOption(["points"]);

    expect(result.brush).toEqual([]);
    expect(result.toolbox.feature.brush).toBeUndefined();
  });
});

// --- Coordinate conversion ---

describe("coordinate conversion", () => {
  test("rect conversion uses convertFromPixel", () => {
    const chart = {
      getOption: vi.fn(() => ({ series: [{ data: [] }] })),
      convertFromPixel: vi.fn((_f: any, p: number[]) => [p[0] + 1, p[1] + 1]),
    };
    const batch: any[] = [];
    const areas = [
      {
        brushType: "rect",
        range: [
          [10, 20],
          [30, 40],
        ],
      },
    ];

    const result = transformBrushToSelection(batch, areas, chart as any);

    expect(result.box[0].x_range).toEqual([11, 21]);
    expect(result.box[0].y_range).toEqual([31, 41]);
  });

  test("polygon conversion maps all coordinates", () => {
    const chart = {
      getOption: vi.fn(() => ({ series: [] })),
      convertFromPixel: vi.fn((_f: any, p: number[]) => [p[0] * 10, p[1] * 10]),
    };

    const areas = [
      {
        brushType: "polygon",
        range: [
          [1, 2],
          [3, 4],
        ],
      },
    ];

    const result = transformBrushToSelection([], areas, chart as any);

    expect(result.lasso[0].coordinates).toEqual([
      [10, 20],
      [30, 40],
    ]);
  });

  test("falls back to raw pixels when convertFromPixel throws", () => {
    const chart = {
      getOption: vi.fn(() => ({ series: [] })),
      convertFromPixel: vi.fn(() => {
        throw new Error("Unsupported coord system");
      }),
    };

    const areas = [
      {
        brushType: "rect",
        range: [
          [100, 200],
          [50, 150],
        ],
      },
    ];

    const result = transformBrushToSelection([], areas, chart as any);

    expect(result.box[0].x_range).toEqual([100, 200]);
    expect(result.box[0].y_range).toEqual([50, 150]);
  });
});

// --- resolveDataItem ---

describe("resolveDataItem", () => {
  test("returns series data when available", () => {
    const option = { series: [{ data: [10, 20, 30] }] };
    expect(resolveDataItem(option, 0, 1)).toBe(20);
  });

  test("falls back to dataset source", () => {
    const option = {
      series: [{ datasetIndex: 0 }],
      dataset: [
        {
          source: [
            [1, 2],
            [3, 4],
          ],
        },
      ],
    };
    expect(resolveDataItem(option, 0, 0)).toEqual([1, 2]);
  });

  test("returns null when data not found", () => {
    const option = { series: [{}] };
    expect(resolveDataItem(option, 0, 5)).toBeNull();
  });
});

// --- buildPointFromDataItem ---

describe("buildPointFromDataItem", () => {
  test("handles array data", () => {
    const point = buildPointFromDataItem([10, 20], 0, 0, "S");
    expect(point.x).toBe(10);
    expect(point.y).toBe(20);
  });

  test("handles object data", () => {
    const point = buildPointFromDataItem(
      { name: "Mon", value: 42, x: 1, y: 2 },
      0,
      0,
      "S",
    );
    expect(point.name).toBe("Mon");
    expect(point.value).toBe(42);
    expect(point.x).toBe(1);
    expect(point.y).toBe(2);
  });

  test("handles scalar data", () => {
    const point = buildPointFromDataItem(99, 3, 1, "Line");
    expect(point.x).toBe(3);
    expect(point.y).toBe(99);
    expect(point.value).toBe(99);
  });
});
