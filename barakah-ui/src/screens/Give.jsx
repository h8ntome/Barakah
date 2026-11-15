import { useState } from "react";
import { Heart } from "lucide-react";
import {
  IconBadge,
  Notice,
  RequestState,
  ScreenHeader,
  SectionHeader,
} from "../components/ui.jsx";
import { ActionForm, Field, RecordList } from "../components/forms.jsx";
import { AmountField, Pagination } from "../components/FinancialForms.jsx";
import { GivingRecordForm } from "./Zakat.jsx";
import SponsoredAd from "../components/SponsoredAd.jsx";
import { useResource } from "../services/useResource.js";
import * as api from "../services/index.js";
import { money } from "../utils/finance.js";
export default function Give({ navigate, onChanged }) {
  const [query, setQuery] = useState("");
  const [category, setCategory] = useState("");
  const [offset, setOffset] = useState(0);
  const causes = useResource(api.getCauses, {
    query,
    category,
    offset,
    limit: 50,
  });
  const [selected, setSelected] = useState(null);
  const [amount, setAmount] = useState("");
  const [recordOffset, setRecordOffset] = useState(0);
  const donations = useResource(api.getDonations, {
    offset: recordOffset,
    limit: 50,
  });
  const [givingOffset, setGivingOffset] = useState(0);
  const [givingFilters, setGivingFilters] = useState({
    category: "",
    start_date: "",
    end_date: "",
  });
  const sadaqah = useResource(api.getSadaqah, {
    ...givingFilters,
    offset: givingOffset,
    limit: 50,
  });
  const givingSummary = useResource(api.getSadaqahSummary, givingFilters);
  const [editing, setEditing] = useState(null);
  const refreshGiving = () => {
    sadaqah.retry();
    givingSummary.retry();
    onChanged();
  };
  const filterGiving = (key, value) => {
    setGivingFilters({ ...givingFilters, [key]: value });
    setGivingOffset(0);
  };
  return (
    <div className="screen-content inner-screen">
      <ScreenHeader title="Sadaqah & giving" onBack={() => navigate("home")} />
      <section className="give-hero">
        <IconBadge icon={Heart} large />
        <h3>Make room for generosity.</h3>
        <p>Discover approved causes and keep a record of your giving.</p>
      </section>
      <Notice>
        Records and intentions only. No money is collected or transferred here.
        Verify recipients independently before giving elsewhere.
      </Notice>
      <SectionHeader title="Cause directory" />
      <Field
        label="Search causes"
        value={query}
        onChange={(value) => {
          setQuery(value);
          setOffset(0);
        }}
        type="search"
      />
      <Field
        label="Filter cause category"
        value={category}
        onChange={(value) => {
          setCategory(value);
          setOffset(0);
        }}
        help="Leave blank for all categories."
      />
      <RequestState resource={causes} label="approved causes">
        <RecordList
          items={causes.data}
          empty="No approved causes match. Try another search, or record giving to a recipient below."
        >
          {(cause) => (
            <>
              <strong>{cause.title}</strong>
              <p>
                {cause.category} · {cause.currency}
              </p>
              <p>{cause.description}</p>
              <button
                className="mint-button"
                onClick={() => setSelected(cause)}
              >
                Record intention for {cause.title}
              </button>
            </>
          )}
        </RecordList>
        <Pagination
          offset={offset}
          onChange={setOffset}
          count={causes.data?.length || 0}
        />
      </RequestState>
      {selected && (
        <section className="details-section">
          <SectionHeader title={`Giving intention: ${selected.title}`} />
          <p className="section-description">
            {selected.currency} · Not a payment
          </p>
          <ActionForm
            label="Save giving intention"
            success="Intention recorded. No payment was processed."
            onSubmit={async () => {
              await api.createDonation({
                cause_id: selected.id,
                currency: selected.currency,
                amount,
              });
              donations.retry();
              onChanged();
              setAmount("");
            }}
          >
            <AmountField
              label="Intended amount"
              value={amount}
              onChange={setAmount}
            />
          </ActionForm>
          <button className="text-button" onClick={() => setSelected(null)}>
            Close intention form
          </button>
        </section>
      )}
      <details className="details-section">
        <summary>Giving intention history</summary>
        <RequestState resource={donations} label="giving intentions">
          <RecordList
            items={donations.data}
            empty="No giving intentions recorded."
          >
            {(item) => (
              <>
                <strong>{money(item.amount, item.currency)}</strong>
                <p>
                  Cause:{" "}
                  {causes.data?.find((cause) => cause.id === item.cause_id)
                    ?.title || item.cause_id}
                </p>
                <p>
                  {item.status} ·{" "}
                  {item.payment_processed
                    ? "Check server payment status"
                    : "No payment processed"}
                </p>
              </>
            )}
          </RecordList>
          <Pagination
            offset={recordOffset}
            onChange={setRecordOffset}
            count={donations.data?.length || 0}
          />
        </RequestState>
      </details>
      <details className="details-section">
        <summary>Record sadaqah given elsewhere</summary>
        <GivingRecordForm
          label="Save sadaqah record"
          save={api.createSadaqah}
          onSaved={refreshGiving}
        />
      </details>
      <details className="details-section">
        <summary>Sadaqah history</summary>
        <Field
          label="Filter giving category"
          value={givingFilters.category}
          onChange={(value) => filterGiving("category", value)}
          maxLength={80}
        />
        <div className="form-grid">
          <Field
            label="Giving from date"
            type="date"
            value={givingFilters.start_date}
            onChange={(value) => filterGiving("start_date", value)}
          />
          <Field
            label="Giving to date"
            type="date"
            value={givingFilters.end_date}
            onChange={(value) => filterGiving("end_date", value)}
          />
        </div>
        <RequestState resource={givingSummary} label="giving totals">
          <RecordList
            items={givingSummary.data?.map((item) => ({
              ...item,
              id: item.currency,
            }))}
            empty="No giving totals for these filters."
          >
            {(item) => (
              <>
                <strong>
                  Total recorded: {money(item.total, item.currency)}
                </strong>
                <p>All matching records, not just this page.</p>
              </>
            )}
          </RecordList>
        </RequestState>
        <RequestState resource={sadaqah} label="sadaqah records">
          <RecordList
            items={sadaqah.data}
            empty="No sadaqah recorded. Record a gift after giving elsewhere."
          >
            {(item) => (
              <>
                <strong>
                  {item.recipient} · {money(item.amount, item.currency)}
                </strong>
                <p>
                  {item.paid_on} · {item.category} · Manual record
                </p>
                <p>{item.note}</p>
                <button
                  className="text-button"
                  onClick={() => setEditing(item.id)}
                >
                  Edit sadaqah record
                </button>
                {editing === item.id && (
                  <GivingRecordForm
                    key={item.id}
                    label="Save sadaqah changes"
                    initial={{
                      amount: item.amount,
                      currency: item.currency,
                      paid_on: item.paid_on,
                      category: item.category,
                      recipient: item.recipient,
                      note: item.note,
                    }}
                    save={(body) => api.updateSadaqah(item.id, body)}
                    onSaved={() => {
                      setEditing(null);
                      refreshGiving();
                    }}
                  />
                )}
                <details>
                  <summary>Delete sadaqah record</summary>
                  <ActionForm
                    label="Confirm delete sadaqah record"
                    onSubmit={async () => {
                      await api.deleteSadaqah(item.id);
                      refreshGiving();
                    }}
                  />
                </details>
              </>
            )}
          </RecordList>
          <Pagination
            offset={givingOffset}
            onChange={setGivingOffset}
            count={sadaqah.data?.length || 0}
          />
        </RequestState>
      </details>
      <SponsoredAd context="giving" />
    </div>
  );
}
