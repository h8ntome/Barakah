// Database NUMERIC values may include padding zeros; never round an input or use floats.
export function decimalInput(value, precision = 2) {
  const text = String(value ?? "");
  const parts = text.split(".");
  if (parts.length === 2 && parts[1].length > precision && /^0+$/.test(parts[1].slice(precision)))
    return `${parts[0]}.${parts[1].slice(0, precision)}`;
  return text;
}
