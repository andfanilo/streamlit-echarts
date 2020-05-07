function deepMapValues(obj, fn) {
  /*
  https://stackoverflow.com/a/35056218/13405289
   */
  let out = {}

  Object.keys(obj).forEach(function (k) {
    let val

    if (obj[k] !== null && typeof obj[k] === "object") {
      val = deepMapValues(obj[k], fn)
    } else {
      val = fn(obj[k])
    }

    out[k] = val
  })

  return out
}

export default deepMapValues
