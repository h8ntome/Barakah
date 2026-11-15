import { useState } from "react";
import { Coins } from "lucide-react";
import {
  IconBadge,
  Notice,
  RequestState,
  ScreenHeader,
  SectionHeader,
} from "../components/ui.jsx";
import {
  ActionForm,
  Empty,
  Field,
  RecordList,
  today,
} from "../components/forms.jsx";
import {
  AmountField,
  CurrencyField,
  Pagination,
} from "../components/FinancialForms.jsx";
import { useResource } from "../services/useResource.js";
import * as api from "../services/index.js";
import { money } from "../utils/finance.js";
import {
  createZakatDraft,
  validatePaymentHistory,
} from "../utils/zakatDraft.js";

const assetLabels = {
  cash: "Cash and bank balances (excluding savings)",
  savings: "Savings balances",
  other: "Other eligible assets",
  investments: "Eligible investments",
  gold: "Gold value",
  silver: "Silver value",
  business: "Business assets",
  liabilities: "Deductible liabilities",
};
function ProfileForm({ initial, onSaved }) {
  const [draft, setDraft] = useState(() => createZakatDraft(initial, today()));
  const set = (key, value) => setDraft({ ...draft, [key]: value });
  return (
    <ActionForm
      label="Save and calculate zakat"
      success="Profile saved. The estimate below is calculated by the server."
      onSubmit={async () => {
        await api.saveZakatProfile({
          ...draft,
          haul_start: draft.haul_start || null,
          manual_nisab:
            draft.nisab_method === "manual" ? draft.manual_nisab : null,
          gold_price_per_gram:
            draft.nisab_method === "gold" ? draft.gold_price_per_gram : null,
          silver_price_per_gram:
            draft.nisab_method === "silver"
              ? draft.silver_price_per_gram
              : null,
        });
        onSaved();
      }}
    >
      <CurrencyField
        value={draft.currency}
        onChange={(value) => set("currency", value)}
      />
      <p className="formula-note">
        Enter all assets in this currency. Changing currency does not convert
        amounts. Enter each asset only once; move savings out of cash if
        previously included there. Account and portfolio values are not added
        automatically.
      </p>
      {Object.entries(assetLabels).map(([key, label]) => (
        <AmountField
          key={key}
          label={label}
          value={draft.assets[key]}
          onChange={(value) => set("assets", { ...draft.assets, [key]: value })}
          allowZero
        />
      ))}
      <Field
        label="Valuation date"
        type="date"
        value={draft.valuation_date}
        onChange={(value) => set("valuation_date", value)}
        required
      />
      <Field
        label="Nisab method"
        options={[
          { value: "manual", label: "Manual threshold" },
          { value: "gold", label: "Gold threshold" },
          { value: "silver", label: "Silver threshold" },
        ]}
        value={draft.nisab_method}
        onChange={(value) => set("nisab_method", value)}
      />
      {draft.nisab_method === "manual" && (
        <AmountField
          label="Manual nisab threshold"
          value={draft.manual_nisab}
          onChange={(value) => set("manual_nisab", value)}
        />
      )}
      {draft.nisab_method === "gold" && (
        <>
          <Field
            label="Gold nisab weight (grams)"
            value={draft.gold_nisab_grams}
            onChange={(value) => set("gold_nisab_grams", value)}
            inputMode="decimal"
            pattern="[0-9]+(\.[0-9]{1,6})?"
            required
            help="Positive grams, up to six decimals. Default 85 g; confirm the weight with your chosen methodology."
          />
          <AmountField
            label="Gold price per gram"
            value={draft.gold_price_per_gram}
            onChange={(value) => set("gold_price_per_gram", value)}
            precision={6}
          />
        </>
      )}
      {draft.nisab_method === "silver" && (
        <>
          <Field
            label="Silver nisab weight (grams)"
            value={draft.silver_nisab_grams}
            onChange={(value) => set("silver_nisab_grams", value)}
            inputMode="decimal"
            pattern="[0-9]+(\.[0-9]{1,6})?"
            required
            help="Positive grams, up to six decimals. Default 595 g; confirm the weight with your chosen methodology."
          />
          <AmountField
            label="Silver price per gram"
            value={draft.silver_price_per_gram}
            onChange={(value) => set("silver_price_per_gram", value)}
            precision={6}
          />
        </>
      )}
      <Field
        label="Price or threshold source"
        value={draft.price_source}
        onChange={(value) => set("price_source", value)}
        required
        maxLength={200}
        help="Describe where you obtained this dated, manually entered value. No live prices are supplied."
      />
      <Field
        label="Zakat rate (fraction)"
        value={draft.rate}
        onChange={(value) => set("rate", value)}
        inputMode="decimal"
        pattern="[0-9]+(\.[0-9]{1,6})?"
        required
        help="0.025 means 2.5%. Confirm the appropriate rate with a qualified scholar."
      />
      <Field
        label="Haul start date (optional)"
        type="date"
        value={draft.haul_start}
        onChange={(value) => set("haul_start", value)}
        max={draft.valuation_date}
      />
      <label className="check-field">
        <input
          type="checkbox"
          checked={draft.haul_complete}
          onChange={(event) => set("haul_complete", event.target.checked)}
        />
        <span>
          I attest that the required holding period (haul) is complete. A start
          date alone does not confirm eligibility.
        </span>
      </label>
    </ActionForm>
  );
}
export function GivingRecordForm({
  label,
  save,
  histories = [],
  onSaved,
  initial,
}) {
  const [draft, setDraft] = useState(
    initial || {
      amount: "",
      currency: "USD",
      paid_on: today(),
      category: "general",
      recipient: "",
      note: "",
      history_id: "",
    },
  );
  return (
    <ActionForm
      label={label}
      success="Record saved. No payment was processed."
      onSubmit={async () => {
        const { history_id, ...body } = draft;
        validatePaymentHistory(histories, draft.currency, history_id);
        await save({ ...body, ...(history_id ? { history_id } : {}) });
        onSaved();
        setDraft({ ...draft, amount: "", note: "" });
      }}
    >
      <AmountField
        label="Recorded amount"
        value={draft.amount}
        onChange={(amount) => setDraft({ ...draft, amount })}
      />
      <CurrencyField
        value={draft.currency}
        onChange={(currency) =>
          setDraft({ ...draft, currency, history_id: "" })
        }
      />
      <Field
        label="Date given"
        type="date"
        value={draft.paid_on}
        onChange={(paid_on) => setDraft({ ...draft, paid_on })}
        required
      />
      <Field
        label="Giving category"
        value={draft.category}
        onChange={(category) => setDraft({ ...draft, category })}
        required
        maxLength={80}
      />
      <Field
        label="Recipient"
        value={draft.recipient}
        onChange={(recipient) => setDraft({ ...draft, recipient })}
        required
        maxLength={120}
      />
      <Field
        label="Record note"
        value={draft.note}
        onChange={(note) => setDraft({ ...draft, note })}
        maxLength={500}
      />
      {(histories.length > 0 || draft.history_id) && (
        <Field
          label="Link calculation (optional)"
          value={draft.history_id}
          onChange={(history_id) => setDraft({ ...draft, history_id })}
          options={[
            { value: "", label: "No linked calculation" },
            ...(draft.history_id &&
            !histories.some(
              (item) =>
                item.id === draft.history_id &&
                item.estimate.currency === draft.currency,
            )
              ? [
                  {
                    value: draft.history_id,
                    label: "Selected calculation unavailable — reload choices",
                  },
                ]
              : []),
            ...histories
              .filter((item) => item.estimate.currency === draft.currency)
              .map((item) => ({
                value: item.id,
                label: `${item.estimate.valuation_date} · ${money(item.estimate.estimated_due, item.estimate.currency)}`,
              })),
          ]}
        />
      )}
    </ActionForm>
  );
}
export default function Zakat({ navigate, onChanged }) {
  const profile = useResource(api.getZakatProfile);
  const estimate = useResource(api.getZakatEstimate);
  const [offset, setOffset] = useState(0);
  const history = useResource(api.getZakatHistory, { offset, limit: 50 });
  const historyChoices = useResource(api.getZakatHistoryChoices);
  const [paymentOffset, setPaymentOffset] = useState(0);
  const payments = useResource(api.getZakatPayments, {
    offset: paymentOffset,
    limit: 50,
  });
  const result = estimate.data;
  return (
    <div className="screen-content inner-screen">
      <ScreenHeader title="Zakat calculator" onBack={() => navigate("home")} />
      <RequestState resource={estimate} label="zakat estimate">
        {result ? (
          <>
            <section className="estimate-hero">
              <IconBadge icon={Coins} large />
              <h3>Estimated zakat due</h3>
              <div className="large-amount">
                {money(result.estimated_due, result.currency)}
              </div>
              <p>
                {result.eligible
                  ? "Nisab and attested haul conditions met"
                  : "Eligibility conditions not met"}
              </p>
            </section>
            <div className="breakdown">
              <div>
                <span>Total entered assets</span>
                <strong>{money(result.total_assets, result.currency)}</strong>
              </div>
              <div>
                <span>Eligible base</span>
                <strong>{money(result.eligible_base, result.currency)}</strong>
              </div>
              <div>
                <span>Nisab threshold</span>
                <strong>{money(result.nisab, result.currency)}</strong>
              </div>
              <div>
                <span>Haul attestation</span>
                <strong>
                  {result.haul_complete ? "Complete" : "Not complete"}
                </strong>
              </div>
            </div>
            <p className="formula-note">
              Valued {result.valuation_date} · Source: {result.price_source}
            </p>
            <Notice>{result.methodology}</Notice>
            <ActionForm
              label="Save calculation to history"
              success="Calculation snapshot saved."
              onSubmit={async () => {
                await api.saveZakatHistory();
                history.retry();
                historyChoices.retry();
              }}
            />
          </>
        ) : (
          <Empty>
            No zakat profile yet. Enter your assets and methodology below to
            calculate an estimate.
          </Empty>
        )}
      </RequestState>
      <Notice>
        Educational estimate, not a religious ruling. Asset qualification,
        deductible debt and haul require your judgment and qualified guidance.
        Prices and attestations are user supplied.
      </Notice>
      <SectionHeader title="Assets and methodology" />
      <RequestState resource={profile} label="zakat profile">
        <ProfileForm
          initial={profile.data}
          onSaved={() => {
            estimate.retry();
            onChanged();
          }}
        />
      </RequestState>
      <details className="details-section">
        <summary>Calculation history</summary>
        <RequestState resource={history} label="calculation history">
          <RecordList
            items={history.data}
            empty="Save a calculation above to preserve its dated methodology."
          >
            {(item) => (
              <>
                <strong>
                  {money(item.estimate.estimated_due, item.estimate.currency)} ·{" "}
                  {item.estimate.valuation_date}
                </strong>
                <p>
                  {item.profile.nisab_method} · {item.estimate.price_source}
                </p>
                <p>
                  Base{" "}
                  {money(item.estimate.eligible_base, item.estimate.currency)} ·
                  Nisab {money(item.estimate.nisab, item.estimate.currency)} ·
                  Haul {item.estimate.haul_complete ? "complete" : "incomplete"}
                </p>
                <p>{item.estimate.methodology}</p>
                <p>
                  Recorded paid{" "}
                  {money(item.paid_amount, item.estimate.currency)} · Remaining{" "}
                  {money(item.remaining_amount, item.estimate.currency)}
                </p>
              </>
            )}
          </RecordList>
          <Pagination
            offset={offset}
            onChange={setOffset}
            count={history.data?.length || 0}
          />
        </RequestState>
      </details>
      <details className="details-section">
        <summary>Record a zakat payment</summary>
        <Notice>
          Record a payment made elsewhere. Barakah does not transfer money or
          issue payment receipts.
        </Notice>
        <RequestState resource={historyChoices} label="calculation choices" />
        <GivingRecordForm
          label="Save zakat payment record"
          save={api.createZakatPayment}
          histories={historyChoices.data || []}
          onSaved={() => {
            payments.retry();
            history.retry();
            onChanged();
          }}
        />
      </details>
      <details className="details-section">
        <summary>Zakat payment history</summary>
        <RequestState resource={payments} label="payment records">
          <RecordList
            items={payments.data}
            empty="No payments recorded. Add a manual record after giving elsewhere."
          >
            {(item) => (
              <>
                <strong>
                  {item.recipient} · {money(item.amount, item.currency)}
                </strong>
                <p>{item.paid_on} · Manual record</p>
                <p>{item.note}</p>
              </>
            )}
          </RecordList>
          <Pagination
            offset={paymentOffset}
            onChange={setPaymentOffset}
            count={payments.data?.length || 0}
          />
        </RequestState>
      </details>
    </div>
  );
}
