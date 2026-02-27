from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from streamlit_echarts import (
    EMPTY_SELECTION,
    JsCode,
    _serialize_options,
    st_echarts,
    st_pyecharts,
)

JS_PLACEHOLDER = "--x_x--0_0--"


class TestJsCode:
    def test_str(self):
        js = JsCode("function(x) { return x; }")
        assert str(js) == f"{JS_PLACEHOLDER}function(x) {{ return x; }}{JS_PLACEHOLDER}"

    def test_repr(self):
        js = JsCode("x => x")
        assert repr(js) == f"JsCode({JS_PLACEHOLDER}x => x{JS_PLACEHOLDER})"

    def test_js_code_attribute(self):
        code = "function(a, b) { return a + b; }"
        js = JsCode(code)
        assert js.js_code == f"{JS_PLACEHOLDER}{code}{JS_PLACEHOLDER}"


class TestSerializeOptions:
    def test_jscode_at_top_level(self):
        js = JsCode("x => x")
        result = _serialize_options(js)
        assert result == js.js_code

    def test_jscode_nested_in_dict(self):
        opts = {
            "tooltip": {
                "formatter": JsCode("(params) => params.name"),
            },
            "title": "plain string",
        }
        result = _serialize_options(opts)
        assert result["title"] == "plain string"
        assert JS_PLACEHOLDER in result["tooltip"]["formatter"]

    def test_jscode_inside_list(self):
        opts = {
            "series": [
                {"symbolSize": JsCode("(val) => val[2] * 10")},
                {"symbolSize": 20},
            ]
        }
        result = _serialize_options(opts)
        assert JS_PLACEHOLDER in result["series"][0]["symbolSize"]
        assert result["series"][1]["symbolSize"] == 20

    def test_plain_values_unchanged(self):
        opts = {"a": 1, "b": "hello", "c": [1, 2], "d": {"nested": True}}
        assert _serialize_options(opts) == opts


class TestStEchartsSelection:
    """Tests for on_select / selection_mode parameters."""

    @patch("streamlit_echarts.out")
    def test_ignore_mode_no_selection(self, mock_out: MagicMock):
        mock_out.return_value = {}
        st_echarts(options={"series": []}, on_select="ignore")

        call_kwargs = mock_out.call_args
        data = call_kwargs.kwargs["data"]
        assert data["selectionActive"] is False
        assert data["selectionMode"] == []
        assert "on_selection_change" not in call_kwargs.kwargs
        assert call_kwargs.kwargs["default"] == {}

    @patch("streamlit_echarts.out")
    def test_rerun_mode_registers_selection(self, mock_out: MagicMock):
        mock_out.return_value = {"selection": EMPTY_SELECTION}
        st_echarts(options={"series": []}, on_select="rerun")

        call_kwargs = mock_out.call_args
        data = call_kwargs.kwargs["data"]
        assert data["selectionActive"] is True
        assert set(data["selectionMode"]) == {"points", "box", "lasso"}
        assert "on_selection_change" in call_kwargs.kwargs
        assert call_kwargs.kwargs["default"] == {"selection": EMPTY_SELECTION}

    @patch("streamlit_echarts.out")
    def test_callable_forwarded_as_on_selection_change(self, mock_out: MagicMock):
        mock_out.return_value = {}
        callback = MagicMock()
        st_echarts(options={"series": []}, on_select=callback)

        call_kwargs = mock_out.call_args
        assert call_kwargs.kwargs["on_selection_change"] is callback

    @patch("streamlit_echarts.out")
    def test_invalid_selection_mode_raises(self, mock_out: MagicMock):
        with pytest.raises(ValueError, match="Invalid selection_mode"):
            st_echarts(
                options={"series": []},
                on_select="rerun",
                selection_mode=["points", "invalid"],
            )

    @patch("streamlit_echarts.out")
    def test_selection_mode_string_normalized_to_list(self, mock_out: MagicMock):
        mock_out.return_value = {}
        st_echarts(
            options={"series": []},
            on_select="rerun",
            selection_mode="points",
        )

        call_kwargs = mock_out.call_args
        data = call_kwargs.kwargs["data"]
        assert data["selectionMode"] == ["points"]

    @patch("streamlit_echarts.out")
    def test_invalid_on_select_raises(self, mock_out: MagicMock):
        with pytest.raises(ValueError, match="on_select must be"):
            st_echarts(options={"series": []}, on_select="invalid")


class TestStPyecharts:
    """Tests for st_pyecharts wrapper."""

    def _make_mock_chart(self, options: dict | None = None):
        """Create a mock pyecharts chart with dump_options()."""
        import json

        if options is None:
            options = {
                "xAxis": {"type": "category", "data": ["A", "B"]},
                "yAxis": {"type": "value"},
                "series": [{"data": [10, 20], "type": "bar"}],
            }
        chart = MagicMock()
        chart.dump_options.return_value = json.dumps(options)
        return chart, options

    @patch("streamlit_echarts.out")
    def test_basic_call_forwards_to_st_echarts(self, mock_out: MagicMock):
        mock_out.return_value = {}
        chart, options = self._make_mock_chart()

        with patch("streamlit_echarts.st_pyecharts.__module__", "streamlit_echarts"):
            # Mock pyecharts import inside st_pyecharts
            with patch.dict("sys.modules", {"pyecharts": MagicMock(), "pyecharts.charts": MagicMock(), "pyecharts.charts.base": MagicMock()}):
                st_pyecharts(chart)

        chart.dump_options.assert_called_once()
        call_kwargs = mock_out.call_args
        data = call_kwargs.kwargs["data"]
        assert data["options"] == options

    @patch("streamlit_echarts.out")
    def test_forwards_theme_and_dimensions(self, mock_out: MagicMock):
        mock_out.return_value = {}
        chart, _ = self._make_mock_chart()

        with patch.dict("sys.modules", {"pyecharts": MagicMock(), "pyecharts.charts": MagicMock(), "pyecharts.charts.base": MagicMock()}):
            st_pyecharts(chart, theme="dark", height="500px", width="80%")

        data = mock_out.call_args.kwargs["data"]
        assert data["theme"] == "dark"
        assert data["height"] == "500px"
        assert data["width"] == "80%"

    @patch("streamlit_echarts.out")
    def test_forwards_selection_params(self, mock_out: MagicMock):
        mock_out.return_value = {"selection": EMPTY_SELECTION}
        chart, _ = self._make_mock_chart()

        with patch.dict("sys.modules", {"pyecharts": MagicMock(), "pyecharts.charts": MagicMock(), "pyecharts.charts.base": MagicMock()}):
            st_pyecharts(chart, on_select="rerun", selection_mode="points")

        call_kwargs = mock_out.call_args
        data = call_kwargs.kwargs["data"]
        assert data["selectionActive"] is True
        assert data["selectionMode"] == ["points"]

    @patch("streamlit_echarts.out")
    def test_forwards_events(self, mock_out: MagicMock):
        mock_out.return_value = {}
        chart, _ = self._make_mock_chart()
        events = {"click": "function(params) { alert(params.name); }"}

        with patch.dict("sys.modules", {"pyecharts": MagicMock(), "pyecharts.charts": MagicMock(), "pyecharts.charts.base": MagicMock()}):
            st_pyecharts(chart, events=events)

        data = mock_out.call_args.kwargs["data"]
        assert "click" in data["onEvents"]

    def test_import_error_without_pyecharts(self):
        chart = MagicMock()
        chart.dump_options.return_value = "{}"

        with patch.dict("sys.modules", {"pyecharts": None, "pyecharts.charts": None, "pyecharts.charts.base": None}):
            with pytest.raises(ImportError, match="pip install streamlit-echarts\\[pyecharts\\]"):
                st_pyecharts(chart)

    @patch("streamlit_echarts.out")
    def test_returns_component_value(self, mock_out: MagicMock):
        expected = {"selection": {"points": [{"name": "A"}]}}
        mock_out.return_value = expected
        chart, _ = self._make_mock_chart()

        with patch.dict("sys.modules", {"pyecharts": MagicMock(), "pyecharts.charts": MagicMock(), "pyecharts.charts.base": MagicMock()}):
            result = st_pyecharts(chart)

        assert result == expected
