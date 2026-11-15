import { useState } from "react";
import {
  Notice,
  RequestState,
  ScreenHeader,
  SectionHeader,
  SegmentedControl,
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
import { ScreeningForm, PortfolioManager } from "./PortfolioForms.jsx";
import SponsoredAd from "../components/SponsoredAd.jsx";
import { useResource } from "../services/useResource.js";
import * as api from "../services/index.js";
import { money } from "../utils/finance.js";
function HoldingEditor({ holding, onSaved }) {
  const [quote, setQuote] = useState({
    price: holding.quote_price || "",
    as_of: holding.quote_date || today(),
    source: holding.quote_source || "",
  });
  return (
    <>
      <details>
        <summary>Update manual valuation for {holding.symbol}</summary>
        <ActionForm
          label="Save manual valuation"
          onSubmit={async () => {
            await api.updateQuote(holding.id, quote);
            onSaved();
          }}
        >
          <AmountField
            label="Quoted price per unit"
            value={quote.price}
            onChange={(price) => setQuote({ ...quote, price })}
            precision={6}
          />
          <Field
            label="Quote date"
            type="date"
            value={quote.as_of}
            onChange={(as_of) => setQuote({ ...quote, as_of })}
            required
          />
          <Field
            label="Quote source"
            value={quote.source}
            onChange={(source) => setQuote({ ...quote, source })}
            required
            maxLength={200}
          />
        </ActionForm>
      </details>
      <details>
        <summary>Screen {holding.symbol}</summary>
        <ScreeningForm holding={holding} onSaved={onSaved} />
      </details>
    </>
  );
}
export default function Invest({ navigate, onChanged }) {
  const [view, setView] = useState("portfolio");
  const [portfolioId, setPortfolioId] = useState("");
  const portfolio = useResource(api.getPortfolio, {
    portfolio_id: portfolioId,
  });
  const portfolios = useResource(api.getPortfolioChoices);
  const education = useResource(api.getInvestmentEducation);
  const [offset, setOffset] = useState(0);
  const trades = useResource(api.getTrades, { offset, limit: 50 });
  const [holding, setHolding] = useState({
    portfolio_id: "",
    symbol: "",
    name: "",
    currency: "USD",
  });
  const [trade, setTrade] = useState({
    holding_id: "",
    side: "buy",
    quantity: "",
    price: "",
    fees: "0.00",
    traded_on: today(),
  });
  const refresh = () => {
    portfolio.retry();
    portfolios.retry();
    trades.retry();
    onChanged();
  };
  return (
    <div className="screen-content inner-screen">
      <ScreenHeader title="Investments" onBack={() => navigate("home")} />
      <SegmentedControl
        label="Investment view"
        options={[
          { id: "portfolio", label: "My portfolio" },
          { id: "education", label: "Learn" },
        ]}
        value={view}
        onChange={setView}
      />
      <div hidden={view !== "portfolio"}>
        <Notice>
          Manual portfolio tracking, not brokerage execution. Trades do not move
          account balances. Valuations and screening are user reported, not live
          or certified.
        </Notice>
        <Field
          label="View portfolio"
          value={portfolioId}
          onChange={setPortfolioId}
          options={[
            { value: "", label: "All portfolios" },
            ...(portfolios.data || []).map((item) => ({
              value: item.id,
              label: item.name,
            })),
          ]}
        />
        <PortfolioManager
          portfolios={portfolios}
          onChanged={(deletedId) => {
            if (deletedId === portfolioId) setPortfolioId("");
            if (deletedId === holding.portfolio_id)
              setHolding({ ...holding, portfolio_id: "" });
            refresh();
          }}
        />
        <RequestState resource={portfolio} label="portfolio">
          {portfolio.data?.by_currency.length ? (
            portfolio.data.by_currency.map((item) => (
              <section key={item.currency} className="portfolio-summary">
                <div>
                  <p className="secondary">Recorded value · {item.currency}</p>
                  <strong className="large-amount">
                    {item.market_value === null
                      ? "Not valued"
                      : money(item.market_value, item.currency)}
                  </strong>
                  <p className="formula-note">
                    {item.valuation_complete
                      ? "Based on dated manual quotes"
                      : "Incomplete valuation: add missing quotes"}
                  </p>
                  <dl className="metric-grid">
                    <div>
                      <dt>Cost basis</dt>
                      <dd>{money(item.cost_basis, item.currency)}</dd>
                    </div>
                    <div>
                      <dt>Realized gain / loss</dt>
                      <dd>{money(item.realized_gain, item.currency)}</dd>
                    </div>
                    <div>
                      <dt>Unrealized gain / loss</dt>
                      <dd>
                        {item.unrealized_gain === null
                          ? "Unavailable"
                          : money(item.unrealized_gain, item.currency)}
                      </dd>
                    </div>
                  </dl>
                </div>
              </section>
            ))
          ) : (
            <Empty>
              No holdings yet. Add a holding and record a purchase below.
            </Empty>
          )}
          <SectionHeader title="Holdings" />
          <RecordList
            items={portfolio.data?.holdings}
            empty="Your holdings will appear here."
          >
            {(item) => (
              <>
                <strong>
                  {item.symbol} · {item.name}
                </strong>
                <p>
                  {item.quantity} units · {item.currency} · Cost{" "}
                  {money(item.cost_basis, item.currency)}
                </p>
                <p>
                  Value:{" "}
                  {item.market_value === null
                    ? "Unavailable — add a quote"
                    : money(item.market_value, item.currency)}
                </p>
                <p>
                  Quote: {item.quote_date || "Not provided"} ·{" "}
                  {item.quote_source || "No source"}
                </p>
                <p>
                  Screening: {item.screening_status.replaceAll("_", " ")} ·{" "}
                  {item.screening_date || "Not dated"}
                </p>
                <p>
                  {item.screening_source} {item.screening_notes}
                </p>
                {item.screening_assessment && (
                  <>
                    <p>
                      Methodology:{" "}
                      {item.screening_assessment.methodology_source} ·{" "}
                      {item.screening_assessment.methodology_version}
                    </p>
                    <p>
                      Missing inputs:{" "}
                      {item.screening_assessment.missing_inputs.join(", ") ||
                        "None"}
                    </p>
                    <p>
                      Failed checks:{" "}
                      {item.screening_assessment.failed_checks.join(", ") ||
                        "None"}
                    </p>
                    <p>{item.screening_assessment.disclaimer}</p>
                  </>
                )}
                <HoldingEditor holding={item} onSaved={refresh} />
              </>
            )}
          </RecordList>
        </RequestState>
        <details className="details-section">
          <summary>Add a holding</summary>
          <ActionForm
            label="Create holding"
            onSubmit={async () => {
              await api.createHolding(holding);
              refresh();
              setHolding({ ...holding, symbol: "", name: "" });
            }}
          >
            <Field
              label="Holding portfolio"
              value={holding.portfolio_id}
              onChange={(portfolio_id) =>
                setHolding({ ...holding, portfolio_id })
              }
              required
              options={[
                { value: "", label: "Choose a portfolio" },
                ...(portfolios.data || []).map((item) => ({
                  value: item.id,
                  label: item.name,
                })),
              ]}
            />
            <Field
              label="Holding symbol"
              value={holding.symbol}
              onChange={(symbol) =>
                setHolding({ ...holding, symbol: symbol.toUpperCase() })
              }
              pattern="[A-Z0-9.\-]{1,20}"
              required
              maxLength={20}
            />
            <Field
              label="Holding name"
              value={holding.name}
              onChange={(name) => setHolding({ ...holding, name })}
              required
              maxLength={80}
            />
            <CurrencyField
              value={holding.currency}
              onChange={(currency) => setHolding({ ...holding, currency })}
            />
          </ActionForm>
        </details>
        <details className="details-section">
          <summary>Record a buy or sell</summary>
          <ActionForm
            label="Record trade"
            onSubmit={async () => {
              await api.createTrade(trade);
              refresh();
              setTrade({ ...trade, quantity: "", price: "" });
            }}
          >
            <Field
              label="Trade holding"
              value={trade.holding_id}
              onChange={(holding_id) => setTrade({ ...trade, holding_id })}
              required
              options={[
                { value: "", label: "Choose a holding" },
                ...(portfolio.data?.holdings || []).map((item) => ({
                  value: item.id,
                  label: `${item.symbol} (${item.currency})`,
                })),
              ]}
            />
            <Field
              label="Trade side"
              value={trade.side}
              onChange={(side) => setTrade({ ...trade, side })}
              options={["buy", "sell"]}
            />
            <AmountField
              label="Quantity"
              value={trade.quantity}
              onChange={(quantity) => setTrade({ ...trade, quantity })}
              precision={6}
            />
            <AmountField
              label="Trade price per unit"
              value={trade.price}
              onChange={(price) => setTrade({ ...trade, price })}
              precision={6}
            />
            <AmountField
              label="Trade fees"
              value={trade.fees}
              onChange={(fees) => setTrade({ ...trade, fees })}
              allowZero
            />
            <Field
              label="Trade date"
              type="date"
              value={trade.traded_on}
              onChange={(traded_on) => setTrade({ ...trade, traded_on })}
              required
            />
          </ActionForm>
        </details>
        <details className="details-section">
          <summary>Trade history</summary>
          <RequestState resource={trades} label="trades">
            <RecordList items={trades.data} empty="No trades recorded.">
              {(item) => (
                <>
                  <strong>
                    {item.side} ·{" "}
                    {portfolio.data?.holdings.find(
                      (holding) => holding.id === item.holding_id,
                    )?.symbol || item.holding_id}
                  </strong>
                  <p>
                    {item.quantity} units at {item.price} · Fees {item.fees}
                  </p>
                  <p>{item.traded_on}</p>
                </>
              )}
            </RecordList>
            <Pagination
              offset={offset}
              onChange={setOffset}
              count={trades.data?.length || 0}
            />
          </RequestState>
        </details>
      </div>
      <div hidden={view !== "education"}>
        <SectionHeader title="Invest with understanding" />
        <RequestState resource={education} label="investment education">
          <RecordList items={education.data}>
            {(item) => (
              <>
                <strong>{item.title}</strong>
                <p>{item.description}</p>
              </>
            )}
          </RecordList>
        </RequestState>
        <Notice>
          Assess business activities, financial ratios and the date and source
          of evidence. Unverified or uncertain is not the same as compliant.
          Consult a qualified adviser.
        </Notice>
        <SponsoredAd context="education" />
      </div>
    </div>
  );
}
