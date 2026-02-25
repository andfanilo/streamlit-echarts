/**
 * https://stackoverflow.com/questions/25333918/js-deep-map-function
 */

/**
 * Run function through every nested value of an object
 * @param obj object
 * @param iterator in our case, very certainly evaluate string to function
 * @param context initial value
 * @returns object with all value passed through function
 */
function deepMap(obj: any, iterator: Function, context: any): any {
  if (Array.isArray(obj)) {
    return obj.map((val, idx) =>
      typeof val === "object" && val !== null
        ? deepMap(val, iterator, context)
        : iterator.call(context, val, idx, obj),
    );
  }

  const result: any = {};
  for (const key of Object.keys(obj)) {
    const val = obj[key];
    result[key] =
      typeof val === "object" && val !== null
        ? deepMap(val, iterator, context)
        : iterator.call(context, val, key, obj);
  }
  return result;
}

export default deepMap;
