from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from streamlit_echarts import EMPTY_SELECTION, JsCode, _serialize_options, st_echarts

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
