/**
 * https://stackoverflow.com/questions/25333918/js-deep-map-function
 */
import { isObject, transform } from "lodash"

/**
 * Run function through every nested value of an object
 * @param obj object
 * @param iterator in our case, very certainly evaluate string to function
 * @param context initial value
 * @returns object with all value passed through function
 */
function deepMap(obj: any, iterator: Function, context: any) {
  return transform(obj, function (result: any, val, key) {
    result[key] = isObject(val)
      ? deepMap(val, iterator, context)
      : iterator.call(context, val, key, obj)
  })
}

export default deepMap
