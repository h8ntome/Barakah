import { useState } from "react";
import { ActionForm, Field, RecordList, today } from "../components/forms.jsx";
import { Notice, RequestState } from "../components/ui.jsx";
import { Pagination } from "../components/FinancialForms.jsx";
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
              {record.assessment.missing_inputs.join(", ") || "None"}
            </p>
            <p>
              Failed checks:{" "}
              {record.assessment.failed_checks.join(", ") || "None"}
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
