from __future__ import annotations

from streamlit_echarts import JsCode, _serialize_options

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
