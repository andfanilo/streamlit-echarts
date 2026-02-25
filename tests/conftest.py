from unittest.mock import MagicMock, patch


def pytest_configure(config):
    """Patch st.components.v2.component before streamlit_echarts is imported.

    The module-level call in __init__.py requires the Streamlit runtime and
    a valid asset_dir on disk. Mocking it lets us unit-test JsCode and
    _serialize_options without building the frontend first.
    """
    patcher = patch(
        "streamlit.components.v2.component",
        return_value=MagicMock(),
    )
    patcher.start()
    # Keep reference so it stays alive for the session
    config._st_component_patcher = patcher


def pytest_unconfigure(config):
    patcher = getattr(config, "_st_component_patcher", None)
    if patcher is not None:
        patcher.stop()
