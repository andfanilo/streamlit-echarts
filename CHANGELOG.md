# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
