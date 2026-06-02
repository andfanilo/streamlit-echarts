// Loaded via events={"click": Path(".../click_handler.js")}. Must be a single
// function expression — the loader evaluates `return (<file contents>)`. It's a
// NAMED function so a standalone .js file stays valid: a bare `function (...)`
// declaration needs a name, which is why VSCode reported "Identifier expected".
// `chart` and `echarts` are injected at runtime, in scope like an inline handler.
function clickHandler(params) {
  return {
    name: params.name,
    value: params.value,
    formatted: echarts.format.addCommas(params.value),
  };
}
