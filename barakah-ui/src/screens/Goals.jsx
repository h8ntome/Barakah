import { useState } from "react";
import { ActionForm, Field, RecordList } from "../components/forms.jsx";
import {
  AmountField,
  CurrencyField,
  Pagination,
} from "../components/FinancialForms.jsx";
import { Notice, RequestState } from "../components/ui.jsx";
import { useResource } from "../services/useResource.js";
import * as api from "../services/index.js";
import { money } from "../utils/finance.js";

const emptyGoal = () => ({
  name: "",
  currency: "USD",
  target_amount: "",
  target_date: "",
});
function GoalFields({ draft, setDraft, prefix = "" }) {
  return (
    <>
      <Field
        label={`${prefix}Goal name`}
        value={draft.name}
        onChange={(name) => setDraft({ ...draft, name })}
        required
        maxLength={80}
      />
      <CurrencyField
        label={`${prefix}Goal currency`}
        value={draft.currency}
        onChange={(currency) => setDraft({ ...draft, currency })}
      />
      <AmountField
        label={`${prefix}Goal target amount`}
        value={draft.target_amount}
        onChange={(target_amount) => setDraft({ ...draft, target_amount })}
      />
      <Field
        label={`${prefix}Goal target date (optional)`}
        type="date"
        value={draft.target_date}
        onChange={(target_date) => setDraft({ ...draft, target_date })}
      />
    </>
  );
}
function Contributions({ goal, onChanged }) {
  const [amount, setAmount] = useState("");
  const [offset, setOffset] = useState(0);
  const history = useResource(api.getGoalContributions, goal.id, {
    offset,
    limit: 50,
  });
  return (
    <>
      <ActionForm
        label={`Record contribution to ${goal.name}`}
        success="Manual contribution recorded. No money was transferred."
        onSubmit={async () => {
          await api.createGoalContribution(goal.id, { amount });
          setAmount("");
          history.retry();
          onChanged("Manual contribution recorded. No money was transferred.");
        }}
      >
        <AmountField
          label={`Contribution amount for ${goal.name}`}
          value={amount}
          onChange={setAmount}
        />
      </ActionForm>
      <RequestState resource={history} label="goal contributions">
        <RecordList
          items={history.data}
          empty="No contributions recorded for this goal."
        >
          {(item) => (
            <>
              <strong>{money(item.amount, goal.currency)}</strong>
              <p>Manual progress record</p>
            </>
          )}
        </RecordList>
        <Pagination
          offset={offset}
          onChange={setOffset}
          count={history.data?.length || 0}
        />
      </RequestState>
    </>
  );
}
function GoalRecord({ goal, onChanged }) {
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState({
    name: goal.name,
    currency: goal.currency,
    target_amount: goal.target_amount,
    target_date: goal.target_date || "",
  });
  const [showContributions, setShowContributions] = useState(false);
  return (
    <>
      <strong>{goal.name}</strong>
      <p>
        Recorded progress {money(goal.saved_amount, goal.currency)} · Target{" "}
        {money(goal.target_amount, goal.currency)}
      </p>
      <p>
        {goal.target_date
          ? `Target date ${goal.target_date}`
          : "No target date"}
      </p>
      <button className="text-button" onClick={() => setEditing(true)}>
        Edit goal {goal.name}
      </button>
      {editing && (
        <ActionForm
          label="Save goal changes"
          onSubmit={async () => {
            await api.updateGoal(goal.id, {
              ...draft,
              target_date: draft.target_date || null,
            });
            setEditing(false);
            onChanged("Goal updated.");
          }}
        >
          <GoalFields draft={draft} setDraft={setDraft} prefix="Edit " />
          <p className="formula-note">
            Currency cannot change after contributions. Changing a target does
            not convert or transfer funds.
          </p>
          <button
            className="text-button"
            type="button"
            onClick={() => setEditing(false)}
          >
            Cancel goal editing
          </button>
        </ActionForm>
      )}
      <details
        onToggle={(event) => setShowContributions(event.currentTarget.open)}
      >
        <summary>Contributions to {goal.name}</summary>
        {showContributions && (
          <Contributions goal={goal} onChanged={onChanged} />
        )}
      </details>
      <details>
        <summary>Delete goal {goal.name}</summary>
        <p>
          This removes the goal and its contribution records, not any payment
          made elsewhere.
        </p>
        <ActionForm
          label={`Confirm delete goal ${goal.name}`}
          onSubmit={async () => {
            await api.deleteGoal(goal.id);
            onChanged("Goal and its contribution records deleted.");
          }}
        />
      </details>
    </>
  );
}
export default function Goals({ onChanged }) {
  const [offset, setOffset] = useState(0);
  const goals = useResource(api.getGoals, { offset, limit: 50 });
  const [draft, setDraft] = useState(emptyGoal);
  const [notice, setNotice] = useState("");
  const refresh = (message = "") => {
    setNotice(message);
    goals.retry();
    onChanged();
  };
  return (
    <details className="details-section">
      <summary>Charitable goals</summary>
      <Notice>
        Plan your giving and record progress manually. Contributions do not move
        money, create a donation record or count as payment receipts.
      </Notice>
      <ActionForm
        label="Create charitable goal"
        onSubmit={async () => {
          await api.createGoal({
            ...draft,
            target_date: draft.target_date || null,
          });
          setDraft(emptyGoal());
          refresh();
        }}
      >
        <GoalFields draft={draft} setDraft={setDraft} />
      </ActionForm>
      {notice && (
        <p className="save-status" role="status">
          {notice}
        </p>
      )}
      <RequestState resource={goals} label="charitable goals">
        <RecordList
          items={goals.data}
          empty="Create a charitable goal to begin planning your giving."
        >
          {(goal) => <GoalRecord goal={goal} onChanged={refresh} />}
        </RecordList>
        <Pagination
          offset={offset}
          onChange={setOffset}
          count={goals.data?.length || 0}
        />
      </RequestState>
    </details>
  );
}
