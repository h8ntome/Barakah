import { useState } from "react";
import { ActionForm, Field, RecordList, today } from "../components/forms.jsx";
import { Notice, RequestState } from "../components/ui.jsx";
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
