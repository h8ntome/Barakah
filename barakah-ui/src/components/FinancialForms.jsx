import { Field } from "./forms.jsx";
export const currencies = ["USD", "EUR", "GBP", "PKR", "SAR", "AED"];
export function CurrencyField({ value, onChange, label = "Currency" }) {
  return (
    <Field
      label={label}
      value={value}
      onChange={onChange}
      options={currencies}
    />
  );
}
export function AmountField({
  label = "Amount",
  value,
  onChange,
  allowZero = false,
  precision = 2,
}) {
  return (
    <Field
      label={label}
      value={value}
      onChange={onChange}
      inputMode="decimal"
      required
      pattern={`[0-9]+(\\.[0-9]{1,${precision}})?`}
      help={`${allowZero ? "Zero or positive" : "Positive"} decimal amount; up to ${precision} decimal places.`}
    />
  );
}
export function Tabs({ value, onChange, options, label }) {
  return (
    <div className="management-tabs" role="group" aria-label={label}>
      {options.map((option) => (
        <button
          key={option.id}
          aria-pressed={value === option.id}
          onClick={() => onChange(option.id)}
        >
          {option.label}
        </button>
      ))}
    </div>
  );
}
export function Pagination({ offset, onChange, count, limit = 50 }) {
  return (
    <div className="record-actions">
      <button
        className="text-button"
        disabled={offset === 0}
        onClick={() => onChange(Math.max(0, offset - limit))}
      >
        Previous page
      </button>
      <button
        className="text-button"
        disabled={count < limit}
        onClick={() => onChange(offset + limit)}
      >
        Next page
      </button>
    </div>
  );
}
