import { useId, useRef, useState } from "react";
import { InlineError, PrimaryButton } from "./ui.jsx";
export function Field({
  label,
  name,
  value,
  onChange,
  options,
  help,
  type = "text",
  ...props
}) {
  const id = useId();
  const control = {
    id,
    name,
    value: value ?? "",
    onChange: (event) => onChange(event.target.value),
    ...props,
  };
  return (
    <label className="form-field" htmlFor={id}>
      <span>{label}</span>
      {options ? (
        <select {...control}>
          {options.map((option) => (
            <option key={option.value ?? option} value={option.value ?? option}>
              {option.label ?? option}
            </option>
          ))}
        </select>
      ) : type === "textarea" ? (
        <textarea {...control} rows={3} />
      ) : (
        <input {...control} type={type} />
      )}
      {help && <small>{help}</small>}
    </label>
  );
}
// Draft values stay in their owning screen when a request fails.
export function ActionForm({
  children,
  onSubmit,
  label = "Save",
  success = "Saved.",
  className = "",
}) {
  const [pending, setPending] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const lock = useRef(false);
  async function submit(event) {
    event.preventDefault();
    if (lock.current) return;
    lock.current = true;
    setPending(true);
    setError("");
    setNotice("");
    try {
      await onSubmit();
      setNotice(success);
    } catch (failure) {
      setError(failure.message);
    } finally {
      lock.current = false;
      setPending(false);
    }
  }
  return (
    <form className={`action-form ${className}`} onSubmit={submit}>
      <fieldset disabled={pending}>
        {children}
        <PrimaryButton type="submit" disabled={pending}>
          {pending ? "Please wait…" : label}
        </PrimaryButton>
      </fieldset>
      {error && <InlineError message={error} />}
      {notice && (
        <p className="save-status" role="status">
          {notice}
        </p>
      )}
    </form>
  );
}
export function Empty({ children }) {
  return <p className="empty-copy">{children}</p>;
}
export function RecordList({ items, children, empty = "No records yet." }) {
  return items?.length ? (
    <ul className="record-list">
      {items.map((item) => (
        <li key={item.id}>{children(item)}</li>
      ))}
    </ul>
  ) : (
    <Empty>{empty}</Empty>
  );
}
export const today = () => new Date().toISOString().slice(0, 10);
export const decimalInput = {
  inputMode: "decimal",
  pattern: "[0-9]+(\\.[0-9]+)?",
  required: true,
};
