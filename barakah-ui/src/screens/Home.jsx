import { useState } from "react";
import {
  BarChart3,
  Coins,
  Heart,
  Moon,
  Settings as SettingsIcon,
  Sparkles,
} from "lucide-react";
import { QuickAction, RequestState, SectionHeader } from "../components/ui.jsx";
import { Tabs } from "../components/FinancialForms.jsx";
import { Empty, Field, today } from "../components/forms.jsx";
import { Accounts, Budgets, Transactions } from "./Management.jsx";
import Settings from "./Settings.jsx";
import SponsoredAd from "../components/SponsoredAd.jsx";
import { getDashboard } from "../services/index.js";
import { useResource } from "../services/useResource.js";
import { money } from "../utils/finance.js";
export default function Home({ user, navigate, version, onChanged }) {
  const [section, setSection] = useState("overview");
  const [month, setMonth] = useState(today().slice(0, 7));
  const dashboard = useResource(getDashboard, { month }, version);
  return (
    <div className="screen-content home-screen">
      <header className="home-hero">
        <div className="hero-art" aria-hidden="true">
          <Moon className="hero-moon" size={32} strokeWidth={1.2} />
          <div className="mosque-dome main-dome" />
          <div className="mosque-dome small-dome" />
          <div className="minaret one" />
          <div className="minaret two" />
          <div className="hero-hill" />
        </div>
        <div className="hero-copy">
          <p>Assalamu Alaikum, {user.display_name}</p>
          <h2>Welcome to Barakah.</h2>
          <span>A little intention. A brighter tomorrow.</span>
        </div>
        <button
          className="profile-monogram"
          aria-label="Open settings"
          onClick={() => setSection("settings")}
        >
          <SettingsIcon size={19} />
        </button>
      </header>
      <div className="home-body">
        <section className="overview-card" aria-label="Your financial overview">
          <div className="overview-heading">
            <h3>Your financial overview</h3>
          </div>
          <Field
            label="Overview month"
            type="month"
            value={month}
            onChange={setMonth}
            required
          />
          <RequestState resource={dashboard} label="financial overview">
            {dashboard.data?.by_currency.length ? (
              dashboard.data.by_currency.map((item) => (
                <div key={item.currency}>
                  <p className="secondary">Net worth · {item.currency}</p>
                  <div className="overview-figure">
                    <strong className="financial-amount">
                      {item.net_worth === null
                        ? "Valuation incomplete"
                        : money(item.net_worth, item.currency)}
                    </strong>
                  </div>
                  <dl className="metric-grid">
                    <div>
                      <dt>Monthly income</dt>
                      <dd>{money(item.income, item.currency)}</dd>
                    </div>
                    <div>
                      <dt>Monthly expenses</dt>
                      <dd>{money(item.expenses, item.currency)}</dd>
                    </div>
                    <div>
                      <dt>Monthly savings</dt>
                      <dd>{money(item.savings, item.currency)}</dd>
                    </div>
                    <div>
                      <dt>Monthly savings rate</dt>
                      <dd>
                        {item.savings_rate_percent === null
                          ? "Not applicable — no income"
                          : item.savings_rate_percent === undefined
                            ? "Unavailable"
                            : `${item.savings_rate_percent}%`}
                      </dd>
                    </div>
                    <div>
                      <dt>Account balance</dt>
                      <dd>{money(item.balance, item.currency)}</dd>
                    </div>
                    <div>
                      <dt>Total assets</dt>
                      <dd>
                        {item.total_assets === null
                          ? "Incomplete"
                          : money(item.total_assets, item.currency)}
                      </dd>
                    </div>
                    <div>
                      <dt>Liabilities</dt>
                      <dd>{money(item.liabilities, item.currency)}</dd>
                    </div>
                  </dl>
                  <SectionHeader title="Monthly expenses by category" />
                  {Object.keys(item.expense_categories || {}).length ? (
                    <dl className="metric-grid">
                      {Object.entries(item.expense_categories).map(
                        ([category, amount]) => (
                          <div key={category}>
                            <dt>{category}</dt>
                            <dd>{money(amount, item.currency)}</dd>
                          </div>
                        ),
                      )}
                    </dl>
                  ) : (
                    <Empty>No expenses recorded for this month.</Empty>
                  )}
                </div>
              ))
            ) : (
              <Empty>No balances yet. Add an account below to begin.</Empty>
            )}
          </RequestState>
          <p className="screen-footnote">
            {dashboard.data?.asset_basis ||
              "Manual records, separated by currency. No live bank feed."}
          </p>
        </section>
        <div className="quick-actions">
          <QuickAction
            icon={Coins}
            tone="mint"
            label="Zakat"
            onClick={() => navigate("zakat")}
          />
          <QuickAction
            icon={Heart}
            tone="peach"
            label="Sadaqah"
            onClick={() => navigate("give")}
          />
          <QuickAction
            icon={BarChart3}
            tone="sage"
            label="Invest"
            onClick={() => navigate("invest")}
          />
          <QuickAction
            icon={Sparkles}
            tone="blue"
            label="AI Advisor"
            onClick={() => navigate("chat")}
          />
        </div>
        <Tabs
          label="Home management"
          value={section}
          onChange={setSection}
          options={[
            { id: "overview", label: "Overview" },
            { id: "accounts", label: "Accounts" },
            { id: "transactions", label: "Transactions" },
            { id: "budgets", label: "Budgets" },
            { id: "settings", label: "Settings" },
          ]}
        />
        <div hidden={section !== "overview"}>
          <p className="empty-copy">
            Keep your records current. Add accounts, record transactions and set
            monthly budgets using the sections above.
          </p>
          <SponsoredAd context="dashboard" />
        </div>
        <div hidden={section !== "accounts"}>
          <Accounts onChanged={onChanged} version={version} />
        </div>
        <div hidden={section !== "transactions"}>
          <Transactions onChanged={onChanged} version={version} />
        </div>
        <div hidden={section !== "budgets"}>
          <Budgets onChanged={onChanged} version={version} />
        </div>
        <div hidden={section !== "settings"}>
          <Settings user={user} />
        </div>
      </div>
    </div>
  );
}
