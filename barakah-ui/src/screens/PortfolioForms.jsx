import { useState } from "react";
import { ActionForm, Field, RecordList, today } from "../components/forms.jsx";
import { Notice, RequestState } from "../components/ui.jsx";
import { AmountField, Pagination } from "../components/FinancialForms.jsx";
import { useResource } from "../services/useResource.js";
import * as api from "../services/index.js";
export function ScreeningForm({ holding, onSaved }) {
  const saved = holding.screening_assessment;
  const [draft, setDraft] = useState({
    prohibited_business:
      saved?.prohibited_business === true
        ? "yes"
        : saved?.prohibited_business === false
          ? "no"
          : "",
    debt_to_assets: saved?.debt_to_assets ?? "",
    interest_income_to_revenue: saved?.interest_income_to_revenue ?? "",
    interest_assets_to_assets: saved?.interest_assets_to_assets ?? "",
    debt_threshold: saved?.debt_threshold ?? "0.30",
    income_threshold: saved?.income_threshold ?? "0.05",
    interest_assets_threshold: saved?.interest_assets_threshold ?? "0.30",
    source: saved?.source || "",
    methodology_source:
      saved?.methodology_source ||
      "Illustrative configurable educational checks, not a scholarly standard",
    assessed_on: saved?.assessed_on || today(),
    max_age_days: saved?.max_age_days ?? 90,
    notes: saved?.notes || "",
  });
  const set = (key, value) => setDraft({ ...draft, [key]: value });
  return (
    <>
      <Notice>
        The server evaluates your evidence against the thresholds you choose.
        Missing inputs yield uncertainty, not approval. These illustrative
        checks are not a named scholarly standard or certification.
      </Notice>
      <ActionForm
        label="Evaluate screening"
        success="Server screening assessment saved."
        onSubmit={async () => {
          await api.updateScreening(holding.id, {
            ...draft,
            max_age_days: Number(draft.max_age_days),
            prohibited_business:
              draft.prohibited_business === ""
                ? null
                : draft.prohibited_business === "yes",
            debt_to_assets: draft.debt_to_assets || null,
            interest_income_to_revenue:
              draft.interest_income_to_revenue || null,
            interest_assets_to_assets: draft.interest_assets_to_assets || null,
          });
          onSaved();
        }}
      >
        <Field
          label="Prohibited business activity"
          value={draft.prohibited_business}
          onChange={(value) => set("prohibited_business", value)}
          options={[
            { value: "", label: "Unknown / not assessed" },
            { value: "no", label: "No, based on my evidence" },
            { value: "yes", label: "Yes, identified in my evidence" },
          ]}
        />
        {[
          ["debt_to_assets", "Debt to assets ratio"],
          ["interest_income_to_revenue", "Interest income to revenue ratio"],
          ["interest_assets_to_assets", "Interest-bearing assets ratio"],
        ].map(([key, label]) => (
          <Field
            key={key}
            label={label}
            value={draft[key]}
            onChange={(value) => set(key, value)}
            inputMode="decimal"
            pattern="[0-9]+(\.[0-9]{1,6})?"
            help="Fraction, not percent: 0.20 means 20%. Leave blank if unknown."
          />
        ))}
        <details>
          <summary>Configure methodology thresholds</summary>
          {[
            ["debt_threshold", "Debt ratio threshold"],
            ["income_threshold", "Interest income threshold"],
            ["interest_assets_threshold", "Interest-bearing assets threshold"],
          ].map(([key, label]) => (
            <Field
              key={key}
              label={label}
              value={draft[key]}
              onChange={(value) => set(key, value)}
              inputMode="decimal"
              pattern="[0-9]+(\.[0-9]{1,6})?"
              required
              help="Fraction between 0 and 1; not a universal religious rule."
            />
          ))}
          <Field
            label="Methodology source"
            value={draft.methodology_source}
            onChange={(value) => set("methodology_source", value)}
            required
            maxLength={200}
          />
        </details>
        <Field
          label="Screening evidence source"
          value={draft.source}
          onChange={(value) => set("source", value)}
          required
          maxLength={200}
        />
        <Field
          label="Screening assessment date"
          type="date"
          max={today()}
          value={draft.assessed_on}
          onChange={(value) => set("assessed_on", value)}
          required
        />
        <Field
          label="Screening evidence validity days"
          type="number"
          value={draft.max_age_days}
          onChange={(value) => set("max_age_days", value)}
          min={1} max={3660} step={1} required
          help="After this many days the result needs re-evaluation; this is not a scholarly ruling."
        />
        <Field
          label="Screening notes and limitations"
          type="textarea"
          value={draft.notes}
          onChange={(value) => set("notes", value)}
          maxLength={1000}
        />
      </ActionForm>
    </>
  );
}
export function PortfolioManager({ portfolios, onChanged }) {
  const [name, setName] = useState("");
  const [editing, setEditing] = useState(null);
  const [editName, setEditName] = useState("");
  return (
    <details className="details-section">
      <summary>Create or manage portfolios</summary>
      <ActionForm
        label="Create portfolio"
        onSubmit={async () => {
          await api.createPortfolio({ name });
          setName("");
          onChanged();
        }}
      >
        <Field
          label="Portfolio name"
          value={name}
          onChange={setName}
          required
          maxLength={80}
        />
      </ActionForm>
      <RequestState resource={portfolios} label="portfolios">
        <RecordList
          items={portfolios.data}
          empty="Create a named portfolio, then add holdings."
        >
          {(item) => (
            <>
              <strong>{item.name}</strong>
              <button
                className="text-button"
                onClick={() => {
                  setEditing(item.id);
                  setEditName(item.name);
                }}
              >
                Rename portfolio
              </button>
              {editing === item.id && (
                <ActionForm
                  label="Save portfolio name"
                  onSubmit={async () => {
                    await api.updatePortfolio(item.id, { name: editName });
                    setEditing(null);
                    onChanged();
                  }}
                >
                  <Field
                    label="Updated portfolio name"
                    value={editName}
                    onChange={setEditName}
                    required
                    maxLength={80}
                  />
                </ActionForm>
              )}
              <details>
                <summary>Delete empty portfolio</summary>
                <p>Portfolios with holdings cannot be deleted.</p>
                <ActionForm
                  label="Confirm delete portfolio"
                  onSubmit={async () => {
                    await api.deletePortfolio(item.id);
                    onChanged(item.id);
                  }}
                />
              </details>
            </>
          )}
        </RecordList>
      </RequestState>
    </details>
  );
}

export function ScreeningHistory({ holdingId }) {
  const [offset, setOffset] = useState(0);
  const history = useResource(api.getScreeningHistory, holdingId, {
    offset,
    limit: 50,
  });
  return (
    <RequestState resource={history} label="screening history">
      <RecordList
        items={history.data}
        empty="No screening assessments recorded for this holding."
      >
        {(record) => (
          <>
            <strong>{record.assessment.status.replaceAll("_", " ")}</strong>
            <p>
              Assessed {record.assessment.assessed_on} · Recorded{" "}
              {record.created_at}
            </p>
            <p>Evidence: {record.assessment.source}</p>
            <p>
              Methodology: {record.assessment.methodology_source} ·{" "}
              {record.assessment.methodology_version}
            </p>
            <p>
              Missing inputs:{" "}
              {(Array.isArray(record.assessment.missing_inputs) ? record.assessment.missing_inputs : []).join(", ") || "None"}
            </p>
            <p>
              Failed checks:{" "}
              {(Array.isArray(record.assessment.failed_checks) ? record.assessment.failed_checks : []).join(", ") || "None"}
            </p>
            <p>{record.assessment.notes}</p>
            <p>{record.assessment.disclaimer}</p>
          </>
        )}
      </RecordList>
      <Pagination
        offset={offset}
        onChange={setOffset}
        count={history.data?.length || 0}
      />
    </RequestState>
  );
}

export function HoldingMetadataForm({ holding, onSaved }) {
  const [draft, setDraft] = useState({ name: holding.name, symbol: holding.symbol });
  const [confirmed, setConfirmed] = useState(false);
  return (
    <>
      <details>
        <summary>Edit holding details for {holding.symbol}</summary>
        <ActionForm
          label="Save holding details"
          onSubmit={async () => {
            await api.updateHolding(holding.id, draft);
            onSaved();
          }}
        >
          <Field
            label="Updated holding name"
            value={draft.name}
            onChange={(name) => setDraft({ ...draft, name })}
            required maxLength={80}
          />
          <Field
            label="Updated holding symbol"
            value={draft.symbol}
            onChange={(symbol) => setDraft({ ...draft, symbol: symbol.toUpperCase() })}
            pattern="[A-Z0-9.\-]{1,20}" required maxLength={20}
            help="Symbol changes are only allowed before any trades, quotes or screening are recorded. Currency and portfolio stay unchanged."
          />
        </ActionForm>
      </details>
      <details>
        <summary>Delete tracked holding {holding.symbol}</summary>
        <ActionForm
          label="Confirm delete tracked holding"
          onSubmit={async () => {
            if (!confirmed) throw new Error("Confirm removal of the holding and its history.");
            await api.deleteHolding(holding.id);
            onSaved(holding.id);
          }}
        >
          <Notice>
            Permanently removes {holding.symbol} and all its tracked holding,
            trade and screening records. This cannot be undone. No investments
            are sold and no money moves.
          </Notice>
          <label className="check-field">
            <input type="checkbox" required checked={confirmed}
              onChange={(event) => setConfirmed(event.target.checked)} />
            <span>I confirm removal of this tracked holding and all its trade and screening records.</span>
          </label>
        </ActionForm>
      </details>
    </>
  );
}

export function TradeEditor({ trade, onSaved }) {
  const [draft, setDraft] = useState({
    side: trade.side, quantity: trade.quantity, price: trade.price,
    fees: trade.fees, traded_on: trade.traded_on,
  });
  const [confirmed, setConfirmed] = useState(false);
  const set = (key, value) => setDraft({ ...draft, [key]: value });
  if (!trade.can_correct) {
    return <p className="secondary">{trade.correction_unavailable_reason === "legacy_trade"
      ? "Legacy trade: correction and removal unavailable because its original accounting snapshot is unknown."
      : "Only the latest recorded trade for this holding can be corrected or removed."}</p>;
  }
  return (
    <>
      <details>
        <summary>Correct latest trade</summary>
        <ActionForm label="Save trade correction" onSubmit={async () => {
          await api.updateTrade(trade.id, draft);
          onSaved();
        }}>
          <p>Cost basis and realized gains are recalculated from the corrected quantity, price and fees.</p>
          <Field label="Corrected trade side" value={draft.side}
            onChange={(value) => set("side", value)} options={["buy", "sell"]} />
          <AmountField label="Corrected quantity" value={draft.quantity} precision={6}
            onChange={(value) => set("quantity", value)} />
          <AmountField label="Corrected price per unit" value={draft.price} precision={6}
            onChange={(value) => set("price", value)} />
          <AmountField label="Corrected fees" value={draft.fees} allowZero
            onChange={(value) => set("fees", value)} />
          <Field label="Corrected trade date" type="date" value={draft.traded_on}
            onChange={(value) => set("traded_on", value)} required />
        </ActionForm>
      </details>
      <details>
        <summary>Remove latest tracked trade</summary>
        <ActionForm label="Confirm remove tracked trade" onSubmit={async () => {
          if (!confirmed) throw new Error("Confirm removal of this tracked trade.");
          await api.deleteTrade(trade.id);
          onSaved();
        }}>
          <p>Removes this trade record and restores the holding's quantity, cost basis and realized gains to their values before it. No order is cancelled or executed; no money moves.</p>
          <label className="check-field">
            <input type="checkbox" required checked={confirmed}
              onChange={(event) => setConfirmed(event.target.checked)} />
            <span>I confirm removal of this tracked trade.</span>
          </label>
        </ActionForm>
      </details>
    </>
  );
}
