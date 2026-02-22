# Gemini CLI Context: streamlit-echarts

This project is a Streamlit component for integrating [Apache ECharts](https://echarts.apache.org/en/index.html) into Streamlit applications. It uses the Streamlit Components v2 API.

## Project Structure

- `streamlit_echarts/`: Python package source.
    - `__init__.py`: Main entry point defining `st_echarts`, `Map`, and `JsCode`.
    - `frontend/`: React + TypeScript frontend.
- `demo_app.py`: Comprehensive demo application with various ECharts examples.
- `e2e_playwright/`: End-to-end tests using Playwright and snapshot testing.

## Technologies

- **Python**: Streamlit (>= 1.53), uv for environment management.
- **Frontend**: React, TypeScript, Vite, ECharts, echarts-for-react.
- **Testing**: Vitest (Frontend unit tests), Playwright + Pytest (E2E tests).

## Building and Running

### Development Environment

1.  **Python Setup**:
    ```sh
    uv venv
    uv pip install -e .[devel]
    ```

2.  **Frontend Setup**:
    ```sh
    cd streamlit_echarts/frontend
    npm i --legacy-peer-deps
    ```

### Running the Demo

To run the demo app with all features (requires extra dependencies):
```sh
uv pip install pyecharts pandas faker
uv run streamlit run demo_app.py
```

### Building for Production

1.  **Build Frontend**:
    ```sh
    cd streamlit_echarts/frontend
    npm run build
    ```

2.  **Build Python Wheel**:
    ```sh
    uv build
    ```

## Testing

### Unit Tests (Frontend)

Fast tests for JavaScript parsing logic and utilities.
```sh
cd streamlit_echarts/frontend
npm test
# Or in watch mode:
npm run test:watch
```

### E2E Tests (Playwright)

Snapshot tests that verify visual consistency across platforms.
```sh
# Ensure package is installed and frontend is built
uv run pytest e2e_playwright -n auto
```
Note: Snapshots are platform-specific (`win32`, `linux`) and stored in `e2e_playwright/__snapshots__/`.

## Development Conventions

- **Component API**: `st_echarts` accepts a dictionary of ECharts `options`.
- **JS Code Injection**: Use `JsCode` in Python to wrap JavaScript strings. The frontend identifies these by the `--x_x--0_0--` placeholder.
- **Frontend Builds**: The production build is located in `streamlit_echarts/frontend/build`. The Python package is configured to include these files.
- **Formatting**:
    - Frontend: `npm run format` (Prettier).
    - Python: Use `ruff` if available (implied by `.ruff_cache`).
- **Commits**: Follow standard practices. Do not commit large binary files or secrets.
