/** Connected API shapes. Decimal strings are never converted for financial arithmetic.
 * Backend OpenAPI and docs/backend-api.md are the transport authority.
 * Legacy mockAdapter fixtures are intentionally NOT represented by these types.
 */
export type DecimalString = string;
export type Currency = "USD" | "EUR" | "GBP" | "PKR" | "SAR" | "AED";
export type ISODate = string;
export type ISODateTime = string;
export interface User {
  id: string;
  email: string;
  display_name: string;
  created_at: ISODateTime | null;
  updated_at: ISODateTime | null;
  ai_consent: boolean;
  is_admin: boolean;
  is_demo: boolean;
  demo_expires_at: ISODateTime | null;
  country: string | null;
  timezone: string;
  language: string;
  currency: Currency;
}
export interface Session {
  access_token: string;
  token_type: "bearer";
  user: User;
}
export interface ApiErrorEnvelope {
  error: { code: string; message: string };
}
export interface Page {
  limit?: number;
  offset?: number;
}
export interface Account {
  id: string;
  name: string;
  account_type: "cash" | "bank" | "savings" | "investment";
  currency: Currency;
  balance: DecimalString;
}
export interface AccountCreate
  extends Pick<Account, "name" | "account_type" | "currency"> {
  opening_balance: DecimalString;
}
export interface TransactionInput {
  account_id: string;
  kind: "income" | "expense";
  amount: DecimalString;
  category: string;
  description: string;
  occurred_on: ISODate;
}
export interface Transaction extends Omit<TransactionInput, "kind"> {
  id: string;
  currency: Currency;
  kind: TransactionInput["kind"] | "transfer_in" | "transfer_out";
  transfer_id: string | null;
}
export interface TransactionFilters extends Page {
  account_id?: string;
  category?: string;
  query?: string;
  start_date?: ISODate;
  end_date?: ISODate;
}
export interface BudgetInput {
  category: string;
  currency: Currency;
  amount: DecimalString;
  month: string;
}
export interface Budget extends BudgetInput {
  id: string;
  spent: DecimalString;
  remaining: DecimalString;
  exceeded_amount: DecimalString;
  utilization_percent: DecimalString;
}
export interface DashboardCurrency {
  currency: Currency;
  balance: DecimalString;
  income: DecimalString;
  expenses: DecimalString;
  savings: DecimalString;
  savings_rate_percent: DecimalString | null;
  expense_categories: Record<string, DecimalString>;
  expense_category_percent: Record<string, DecimalString>;
  portfolio_value: DecimalString | null;
  total_assets: DecimalString | null;
  liabilities: DecimalString;
  net_worth: DecimalString | null;
  valuation_complete: boolean;
}
export interface Dashboard {
  display_name: string;
  month: string;
  by_currency: DashboardCurrency[];
  recent_transactions: Transaction[];
  budgets: Budget[];
  goals: Goal[];
  zakat: ZakatEstimate | null;
  latest_zakat_record: ZakatHistory | null;
  asset_basis: string;
}
export interface Assets {
  cash: DecimalString;
  savings: DecimalString;
  other: DecimalString;
  investments: DecimalString;
  gold: DecimalString;
  silver: DecimalString;
  business: DecimalString;
  liabilities: DecimalString;
}
export interface ZakatProfile {
  currency: Currency;
  assets: Assets;
  nisab_method: "manual" | "gold" | "silver";
  manual_nisab: DecimalString | null;
  gold_nisab_grams: DecimalString;
  silver_nisab_grams: DecimalString;
  gold_price_per_gram: DecimalString | null;
  silver_price_per_gram: DecimalString | null;
  price_source: string;
  valuation_date: ISODate;
  haul_start: ISODate | null;
  classification_notes: string;
  haul_complete: boolean;
  rate: DecimalString;
}
export interface ZakatEstimate {
  currency: Currency;
  total_assets: DecimalString;
  eligible_base: DecimalString;
  nisab: DecimalString;
  haul_complete: boolean;
  eligible: boolean;
  estimated_due: DecimalString;
  methodology: string;
  valuation_date: ISODate;
  price_source: string;
}
export interface ZakatHistory {
  id: string;
  profile: ZakatProfile;
  estimate: ZakatEstimate;
  created_at: ISODateTime;
  paid_amount: DecimalString;
  remaining_amount: DecimalString;
}
export interface GivingInput {
  amount: DecimalString;
  currency: Currency;
  paid_on: ISODate;
  category: string;
  recipient: string;
  note: string;
  history_id?: string;
}
export interface Giving extends GivingInput {
  id: string;
  payment_processed?: false;
}
export interface GivingSummary {
  currency: Currency;
  total: DecimalString;
  monthly_total: DecimalString;
  annual_total: DecimalString;
  donation_count: number;
  by_recipient: Record<string, DecimalString>;
  by_category: Record<string, DecimalString>;
}
export interface GivingFilters extends Page {
  category?: string;
  start_date?: ISODate;
  end_date?: ISODate;
}
export interface Cause {
  id: string;
  title: string;
  category: string;
  description: string;
  currency: Currency;
}
export interface DonationIntent {
  id: string;
  cause_id: string;
  amount: DecimalString;
  currency: Currency;
  status: "recorded";
  payment_processed: false;
}
export interface NamedPortfolio {
  id: string;
  name: string;
}
export interface ScreeningInput {
  prohibited_business: boolean | null;
  debt_to_assets: DecimalString | null;
  interest_income_to_revenue: DecimalString | null;
  interest_assets_to_assets: DecimalString | null;
  debt_threshold: DecimalString;
  income_threshold: DecimalString;
  interest_assets_threshold: DecimalString;
  source: string;
  methodology_source: string;
  assessed_on: ISODate;
  max_age_days: number;
  notes: string;
}
export interface ScreeningAssessment extends ScreeningInput {
  status:
    | "non_compliant"
    | "uncertain"
    | "compliant_under_selected_methodology";
  methodology_version: string;
  missing_inputs: string[];
  failed_checks: string[];
  disclaimer: string;
}
export interface Holding {
  id: string;
  portfolio_id: string;
  symbol: string;
  name: string;
  currency: Currency;
  quantity: DecimalString;
  cost_basis: DecimalString;
  average_cost: DecimalString;
  quote_price: DecimalString | null;
  quote_date: ISODate | null;
  quote_source: string | null;
  market_value: DecimalString | null;
  unrealized_gain: DecimalString | null;
  realized_gain: DecimalString;
  allocation_percent?: DecimalString | null;
  unrealized_return_percent?: DecimalString | null;
  needs_reevaluation: boolean;
  screening_status: string;
  screening_source: string | null;
  screening_date: ISODate | null;
  screening_notes: string | null;
  screening_assessment: ScreeningAssessment | null;
}
export interface PortfolioCurrency {
  currency: Currency;
  cost_basis: DecimalString;
  market_value: DecimalString | null;
  realized_gain: DecimalString;
  unrealized_gain: DecimalString | null;
  valuation_complete: boolean;
}
export interface Portfolio {
  holdings: Holding[];
  by_currency: PortfolioCurrency[];
}
export interface TradeInput {
  holding_id: string;
  side: "buy" | "sell";
  quantity: DecimalString;
  price: DecimalString;
  fees: DecimalString;
  traded_on: ISODate;
}
export interface Trade extends TradeInput {
  id: string;
  sequence: number | null;
  can_correct: boolean;
  correction_unavailable_reason: 'legacy_trade' | 'not_latest_trade' | null;
  realized_gain: DecimalString;
}
export interface AdvisorMessage {
  id: string;
  conversation_id: string;
  role: "user" | "assistant";
  text: string;
  created_at: ISODateTime;
  is_demo: boolean;
  generation_metadata: AIResult['metadata'] | null;
}
export interface Conversation {
  id: string;
  created_at: ISODateTime;
}
export interface AIResult {
  conversation_id: string | null;
  response: { role: 'assistant'; text: string } | null;
  error: { code: 'ai_unavailable' | 'ai_timeout' | 'ai_failed' | 'ai_invalid_key' | 'ai_provider_limited' | 'ai_model_rejected'; message: string } | null;
  metadata?: {
    model: 'h8notme/barakah1';
    revision: '912a5697cf9d85adf065ee512f509cfa236459d4';
    prompt_sha256: string;
    template_sha256: string;
    input_tokens: number;
    output_tokens: number;
    generation_seconds: number;
  } | {
    source: 'user_provider';
    provider: 'openai' | 'custom';
    model: string; // Provider-reported, not independently verified.
    configured_model: string;
    input_tokens: number | null;
    output_tokens: number | null;
  };
}
export interface AIConnection {
  mode: 'disabled' | 'local' | 'external';
  provider: 'openai' | 'custom' | null;
  base_url: string | null;
  model_id: string | null;
  revision: string | null;
  has_key: boolean;
  local_available: boolean;
  external_available: boolean;
  custom_enabled: boolean;
  consent_saved: boolean;
  test_status: 'untested' | 'success' | 'failed';
  tested_at: ISODateTime | null;
  test_error: string | null;
  requests_per_minute: number;
  requests_per_day: number;
}
export interface AdvisorContext {
  status: 'unavailable' | 'configured';
  provider: 'unavailable' | 'http' | 'openai' | 'custom';
  model: string | null;
  connection_revision: string | null;
  welcome_message: Pick<AdvisorMessage, "role" | "text" | "is_demo">;
  starter_questions: string[];
}
export interface SponsoredAd {
  id: string;
  title: string;
  body: string;
  url: string;
  context: "dashboard" | "giving" | "education";
  sponsored: true;
  advertiser_name: string;
}

export interface GoalInput {
  name: string;
  currency: Currency;
  target_amount: DecimalString;
  target_date: ISODate | null;
}
export interface Goal extends GoalInput {
  id: string;
  saved_amount: DecimalString;
  remaining_amount: DecimalString;
  progress_percent: DecimalString;
}
export interface GoalContribution {
  id: string;
  goal_id: string;
  amount: DecimalString;
  created_at: ISODateTime;
}

export interface ScreeningRecord {
  id: string;
  holding_id: string;
  assessment: ScreeningAssessment;
  created_at: ISODateTime;
}
