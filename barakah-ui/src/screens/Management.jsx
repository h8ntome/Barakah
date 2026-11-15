import { useState } from "react";
import { ActionForm, Field, RecordList, today } from "../components/forms.jsx";
import {
  AmountField,
  CurrencyField,
  Pagination,
} from "../components/FinancialForms.jsx";
import { Notice, RequestState, SectionHeader } from "../components/ui.jsx";
import { useResource } from "../services/useResource.js";
import * as api from "../services/index.js";
import { money } from "../utils/finance.js";

export function Accounts({ onChanged, version }) {
  const [offset, setOffset] = useState(0);
  const accounts = useResource(api.getAccounts, { offset, limit: 50 }, version);
  const [draft, setDraft] = useState({
    name: "",
    account_type: "cash",
    currency: "USD",
    opening_balance: "0.00",
  });
  const [editing, setEditing] = useState(null);
  const [name, setName] = useState("");
  return (
    <section>
      <SectionHeader title="Accounts" />
      <Notice>
        Manual balances and ledger entries. No bank connection or currency
        conversion.
      </Notice>
      <ActionForm
        label="Add account"
        onSubmit={async () => {
          await api.createAccount(draft);
          accounts.retry();
          onChanged();
          setDraft({ ...draft, name: "", opening_balance: "0.00" });
        }}
      >
        <Field
          label="Account name"
          value={draft.name}
          onChange={(name) => setDraft({ ...draft, name })}
          required
          maxLength={80}
        />
        <Field
          label="Account type"
          value={draft.account_type}
          onChange={(account_type) => setDraft({ ...draft, account_type })}
          options={["cash", "bank", "savings", "investment"]}
        />
        <CurrencyField
          value={draft.currency}
          onChange={(currency) => setDraft({ ...draft, currency })}
        />
        <AmountField
          label="Opening balance"
          value={draft.opening_balance}
          onChange={(opening_balance) =>
            setDraft({ ...draft, opening_balance })
          }
          allowZero
        />
      </ActionForm>
      <RequestState resource={accounts} label="accounts">
        <RecordList
          items={accounts.data}
          empty="Add your first account to start recording income and expenses."
        >
          {(account) => (
            <>
              <strong>{account.name}</strong>
              <p>
                {money(account.balance, account.currency)} ·{" "}
                {account.account_type}
              </p>
              <button
                className="text-button"
                onClick={() => {
                  setEditing(account.id);
                  setName(account.name);
                }}
              >
                Rename {account.name}
              </button>
              {editing === account.id && (
                <ActionForm
                  label="Save account name"
                  onSubmit={async () => {
                    await api.updateAccount(account.id, { name });
                    accounts.retry();
                    onChanged();
                    setEditing(null);
                  }}
                >
                  <Field
                    label="Updated account name"
                    value={name}
                    onChange={setName}
                    required
                    maxLength={80}
                  />
                  <button
                    className="text-button"
                    type="button"
                    onClick={() => setEditing(null)}
                  >
                    Cancel rename
                  </button>
                </ActionForm>
              )}
              <details>
                <summary>Delete account</summary>
                <p>Only accounts without ledger entries can be deleted.</p>
                <ActionForm
                  label={`Confirm delete ${account.name}`}
                  onSubmit={async () => {
                    await api.deleteAccount(account.id);
                    accounts.retry();
                    onChanged();
                  }}
                />
              </details>
            </>
          )}
        </RecordList>
        <Pagination
          offset={offset}
          onChange={setOffset}
          count={accounts.data?.length || 0}
        />
      </RequestState>
    </section>
  );
}
function TransactionFields({ draft, setDraft, options, prefix = "" }) {
  const change = (key, value) => setDraft({ ...draft, [key]: value });
  return (
    <>
      <Field
        label={`${prefix}Transaction account`}
        options={options}
        value={draft.account_id}
        onChange={(value) => change("account_id", value)}
        required
      />
      <Field
        label={`${prefix}Transaction type`}
        options={["income", "expense"]}
        value={draft.kind}
        onChange={(value) => change("kind", value)}
      />
      <AmountField
        label={`${prefix}Transaction amount`}
        value={draft.amount}
        onChange={(value) => change("amount", value)}
      />
      <Field
        label={`${prefix}Category`}
        value={draft.category}
        onChange={(value) => change("category", value)}
        required
        maxLength={80}
      />
      <Field
        label={`${prefix}Description`}
        value={draft.description}
        onChange={(value) => change("description", value)}
        maxLength={500}
      />
      <Field
        label={`${prefix}Transaction date`}
        type="date"
        value={draft.occurred_on}
        onChange={(value) => change("occurred_on", value)}
        required
      />
    </>
  );
}
export function Transactions({ onChanged, version }) {
  const accounts = useResource(api.getAccountChoices, version);
  const [filters, setFilters] = useState({
    account_id: "",
    category: "",
    query: "",
    start_date: "",
    end_date: "",
  });
  const [offset, setOffset] = useState(0);
  const transactions = useResource(api.getTransactions, {
    ...filters,
    offset,
    limit: 50,
  });
  const [draft, setDraft] = useState({
    account_id: "",
    kind: "expense",
    amount: "",
    category: "",
    description: "",
    occurred_on: today(),
  });
  const [editing, setEditing] = useState(null);
  const [editDraft, setEditDraft] = useState(null);
  const [transfer, setTransfer] = useState({
    from_account_id: "",
    to_account_id: "",
    amount: "",
    occurred_on: today(),
  });
  const options = [
    { value: "", label: "Choose an account" },
    ...(accounts.data || []).map((account) => ({
      value: account.id,
      label: `${account.name} (${account.currency})`,
    })),
  ];
  const refresh = () => {
    transactions.retry();
    onChanged();
  };
  const filter = (key, value) => {
    setFilters({ ...filters, [key]: value });
    setOffset(0);
  };
  return (
    <section>
      <SectionHeader title="Transactions" />
      {accounts.error && (
        <Notice>
          Account choices are unavailable. Retry below before recording a
          transaction.
        </Notice>
      )}
      <RequestState resource={accounts} label="account choices">
        <ActionForm
          label="Record transaction"
          onSubmit={async () => {
            await api.createTransaction(draft);
            refresh();
            setDraft({ ...draft, amount: "", description: "" });
          }}
        >
          <TransactionFields
            draft={draft}
            setDraft={setDraft}
            options={options}
          />
        </ActionForm>
      </RequestState>
      <details className="details-section">
        <summary>Transfer between accounts</summary>
        <Notice>
          Transfers are recorded between same-currency accounts, not sent to a
          bank. Transfer ledger entries cannot be individually edited or
          deleted.
        </Notice>
        <ActionForm
          label="Record transfer"
          onSubmit={async () => {
            await api.createTransfer(transfer);
            refresh();
            setTransfer({ ...transfer, amount: "" });
          }}
        >
          <Field
            label="Transfer from"
            value={transfer.from_account_id}
            onChange={(from_account_id) =>
              setTransfer({ ...transfer, from_account_id })
            }
            options={options}
            required
          />
          <Field
            label="Transfer to"
            value={transfer.to_account_id}
            onChange={(to_account_id) =>
              setTransfer({ ...transfer, to_account_id })
            }
            options={options}
            required
          />
          <AmountField
            label="Transfer amount"
            value={transfer.amount}
            onChange={(amount) => setTransfer({ ...transfer, amount })}
          />
          <Field
            label="Transfer date"
            type="date"
            value={transfer.occurred_on}
            onChange={(occurred_on) =>
              setTransfer({ ...transfer, occurred_on })
            }
            required
          />
        </ActionForm>
      </details>
      <SectionHeader title="Transaction history" />
      <Field
        label="Search transaction descriptions"
        type="search"
        value={filters.query}
        onChange={(value) => filter("query", value)}
        maxLength={100}
      />
      <Field
        label="Filter by account"
        value={filters.account_id}
        onChange={(value) => filter("account_id", value)}
        options={[{ value: "", label: "All accounts" }, ...options.slice(1)]}
      />
      <Field
        label="Filter transaction category"
        value={filters.category}
        onChange={(value) => filter("category", value)}
        maxLength={80}
      />
      <div className="form-grid">
        <Field
          label="Transactions from date"
          type="date"
          value={filters.start_date}
          onChange={(value) => filter("start_date", value)}
        />
        <Field
          label="Transactions to date"
          type="date"
          value={filters.end_date}
          onChange={(value) => filter("end_date", value)}
        />
      </div>
      <RequestState resource={transactions} label="transactions">
        <RecordList
          items={transactions.data}
          empty="No transactions match these filters. Record income or an expense above."
        >
          {(item) => (
            <>
              <strong>
                {item.category} · {item.kind}
              </strong>
              <p>
                {money(item.amount, item.currency)} · {item.occurred_on}
              </p>
              <p>{item.description}</p>
              {!item.transfer_id && (
                <>
                  <button
                    className="text-button"
                    onClick={() => {
                      setEditing(item.id);
                      const {
                        account_id,
                        kind,
                        amount,
                        category,
                        description,
                        occurred_on,
                      } = item;
                      setEditDraft({
                        account_id,
                        kind,
                        amount,
                        category,
                        description,
                        occurred_on,
                      });
                    }}
                  >
                    Edit transaction
                  </button>
                  {editing === item.id && (
                    <ActionForm
                      label="Save transaction changes"
                      onSubmit={async () => {
                        await api.updateTransaction(item.id, editDraft);
                        setEditing(null);
                        refresh();
                      }}
                    >
                      <TransactionFields
                        draft={editDraft}
                        setDraft={setEditDraft}
                        options={options}
                        prefix="Edit "
                      />
                      <button
                        className="text-button"
                        type="button"
                        onClick={() => setEditing(null)}
                      >
                        Cancel editing
                      </button>
                    </ActionForm>
                  )}
                  <details>
                    <summary>Delete transaction</summary>
                    <p>
                      The server will reverse this entry's account impact.
                      Deletion can be rejected if it would overdraw an account.
                    </p>
                    <ActionForm
                      label="Confirm delete transaction"
                      onSubmit={async () => {
                        await api.deleteTransaction(item.id);
                        refresh();
                      }}
                    />
                  </details>
                </>
              )}
            </>
          )}
        </RecordList>
        <Pagination
          offset={offset}
          onChange={setOffset}
          count={transactions.data?.length || 0}
        />
      </RequestState>
    </section>
  );
}
function BudgetFields({ draft, setDraft, prefix = "" }) {
  return (
    <>
      <Field
        label={`${prefix}Budget category`}
        value={draft.category}
        onChange={(category) => setDraft({ ...draft, category })}
        required
        maxLength={80}
      />
      <CurrencyField
        label={`${prefix}Budget currency`}
        value={draft.currency}
        onChange={(currency) => setDraft({ ...draft, currency })}
      />
      <AmountField
        label={`${prefix}Budget limit`}
        value={draft.amount}
        onChange={(amount) => setDraft({ ...draft, amount })}
      />
      <Field
        label={`${prefix}Budget month`}
        type="month"
        value={draft.month}
        onChange={(month) => setDraft({ ...draft, month })}
        required
      />
    </>
  );
}
export function Budgets({ onChanged, version }) {
  const [offset, setOffset] = useState(0);
  const budgets = useResource(api.getBudgets, { offset, limit: 50 }, version);
  const [draft, setDraft] = useState({
    category: "",
    currency: "USD",
    amount: "",
    month: today().slice(0, 7),
  });
  const [editing, setEditing] = useState(null);
  const [editDraft, setEditDraft] = useState(null);
  return (
    <section>
      <SectionHeader title="Monthly budgets" />
      <Notice>
        Spending and remaining amounts come from the server ledger for each
        category, currency and month.
      </Notice>
      <ActionForm
        label="Add budget"
        onSubmit={async () => {
          await api.createBudget(draft);
          budgets.retry();
          onChanged();
        }}
      >
        <BudgetFields draft={draft} setDraft={setDraft} />
      </ActionForm>
      <RequestState resource={budgets} label="budgets">
        <RecordList
          items={budgets.data}
          empty="Set a monthly limit for a spending category."
        >
          {(item) => (
            <>
              <strong>
                {item.category} · {item.month}
              </strong>
              <p>
                Limit {money(item.amount, item.currency)} · Spent{" "}
                {money(item.spent, item.currency)}
              </p>
              <p>
                Remaining {money(item.remaining, item.currency)} · Utilization{" "}
                {item.utilization_percent}%
              </p>
              <progress aria-label={`${item.category} budget progress`} max="100" value={Math.min(100, Number(item.utilization_percent))} />
              {Number(item.utilization_percent) > 100 && <p>Exceeded by {money(item.exceeded_amount, item.currency)}</p>}
              <button
                className="text-button"
                onClick={() => {
                  setEditing(item.id);
                  const { category, currency, amount, month } = item;
                  setEditDraft({ category, currency, amount, month });
                }}
              >
                Edit budget
              </button>
              {editing === item.id && (
                <ActionForm
                  label="Save budget changes"
                  onSubmit={async () => {
                    await api.updateBudget(item.id, editDraft);
                    setEditing(null);
                    budgets.retry();
                    onChanged();
                  }}
                >
                  <BudgetFields
                    draft={editDraft}
                    setDraft={setEditDraft}
                    prefix="Edit "
                  />
                  <button
                    className="text-button"
                    type="button"
                    onClick={() => setEditing(null)}
                  >
                    Cancel editing
                  </button>
                </ActionForm>
              )}
              <details>
                <summary>Delete budget</summary>
                <ActionForm
                  label="Confirm delete budget"
                  onSubmit={async () => {
                    await api.deleteBudget(item.id);
                    budgets.retry();
                    onChanged();
                  }}
                />
              </details>
            </>
          )}
        </RecordList>
        <Pagination
          offset={offset}
          onChange={setOffset}
          count={budgets.data?.length || 0}
        />
      </RequestState>
    </section>
  );
}
