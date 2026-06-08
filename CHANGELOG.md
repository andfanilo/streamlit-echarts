# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.7.0] - 2026-06-08

### Added

- Event handlers now run with live `chart` and `echarts` in scope — call `chart.convertFromPixel(...)`, `chart.dispatchAction(...)`, `echarts.format.addCommas(...)`, etc. directly inside an `events` handler
- New `zr:` prefix binds a handler to ZRender / canvas-wide events (e.g. `zr:click`, `zr:mousemove`), including clicks on the blank canvas, not just on series
- Both `events` values and `JsCode(...)` now accept a `str | Path` pointing at a `.js` / `.mjs` file
- `on_select` accepts a callable that fires when the selection changes
- Double-clicking the blank canvas clears the current point selection
- `just bump X.Y.Z` recipe — syncs the version across the root and inner `pyproject.toml`, `uv.lock`, and the frontend `package.json` / `package-lock.json` in one guarded step

### Changed

- Event handlers that return `undefined` skip the Streamlit rerun (client-only interaction); any other return value — including `null` — is sent back to Python as `result.chart_event`
- `publish-test` now reads `UV_PUBLISH_TOKEN_TEST`
- Demo app reorganized into dedicated `on_select` and `events` pages, with examples for file-loaded handlers, `convertFromPixel`, `dispatchAction`, `echarts.format.addCommas`, `zr:click` / `zr:mousemove`, and editable scatter points

### Fixed

- Content-hash custom theme names so multiple charts on one page no longer collide on theme registration
- Serialize tuples correctly, including tuples that embed `JsCode`
- Preserve x/y coordinates for object-form selection points whose `value` is an array
- Clear the brush/toolbox UI properly when brush selection is disabled or switched to points-only
- Use `echarts.color.modifyAlpha` for the Streamlit "subtle" theme color instead of string-appending `"33"`
- Single-quote SVG export font names to avoid corrupted output

## [0.6.1] - 2026-06-02

### Changed

- Bump ECharts to 6.1.0 and `echarts-gl` to 2.1.0
- Numerous dependency bumps (postcss, vite, pytest, pillow, gitpython, urllib3, idna, requests, tornado, and more)

### Added

- `justfile` with setup, lint/format, test, e2e, build, and publish recipes
- Release pipeline: `tag-release` recipe + guarded `publish` / `publish-test`
- `merge-dependabot` recipe to batch-merge dependency PRs
- Python unit test workflow
- Pin line endings to LF via `.gitattributes`
- Use `bundler` moduleResolution in tsconfig

## [0.6.0] - 2026-03-04

### Added

- Structured selection support via `on_select` and `selection_mode` (`"points"` click, `"box"` rect brush, `"lasso"` polygon brush), returning `result["selection"]`
- `"streamlit"` theme (the new default) for automatic light/dark mode support, plus a `"dark"` theme
- `st_pyecharts` as an optional dependency extra (`streamlit-echarts[pyecharts]`)
- `replace_merge` parameter for `universalTransition` support
- `JsCode` supports arrow functions, and `echarts` is injected into the eval scope (enables `LinearGradient`, etc.)

### Changed

- **BREAKING**: Rewrote the frontend on the native ECharts API (replacing `echarts-for-react`)
- Dispose and re-init the chart on renderer change; preserve entry animations on mount and theme change
- Reorganized the demo app into a multipage gallery

## [0.5.0] - 2026-02-22

### Changed

- **BREAKING**: Migrated to Streamlit Components v2 API
- **BREAKING**: Removed `st_pyecharts` wrapper — use `json.loads(chart.dump_options())` + `st_echarts` instead
- Dropped `pyecharts` and `simplejson` as package dependencies (user installs them separately)
- Upgraded frontend build toolchain from Create React App to Vite + TypeScript
- Upgraded ECharts from v5 to v6
- Event return values now use `result.chart_event` on the Python side

## [0.4.0] - 2021-12-12

### Added

- In `events` argument, on event return value is sent back to Python
- Internal: we now reference the echarts instance so anyone forking the project is able to call it back for further actions.

## [0.3.0] - 2021-04-16

### Added

- Upgraded to echarts v5!
- Added a `map` argument to register a custom geoJSON map

## [0.2.0] - 2021-01-12

### Added

- Add liquidfill and wordcloud extensions

### Changed

- Use streamlit-component-lib package
- Extracted demo examples to their own repo

## [0.1.0] - 2020-07-06

### Added

- Initial release of `st_echarts` and `st_pyecharts`
