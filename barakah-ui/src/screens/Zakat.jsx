import { useState } from 'react';
import { BarChart3, Check, Coins, Landmark, LoaderCircle, Pencil, Wallet } from 'lucide-react';
import { AssetRow, DemoTag, InlineError, Modal, Notice, PrimaryButton, ScreenHeader, SectionHeader, IconBadge } from '../components/ui.jsx';
import { saveZakatProfile } from '../services/index.js';
import { displayDate, estimateZakat, maxAmount, money, validateAssets } from '../utils/finance.js';

const fields = [
  { key: 'cash', label: 'Cash & bank balances', icon: Wallet },
  { key: 'investments', label: 'Eligible investments', icon: BarChart3 },
  { key: 'gold', label: 'Gold & silver', icon: Coins },
  { key: 'business', label: 'Business assets', icon: Landmark },
  { key: 'liabilities', label: 'Deductible liabilities', icon: Wallet },
];

export default function Zakat({ profile, summary, navigate, editAssets }) {
  const currency = profile.currency;
  return <div className="screen-content inner-screen">
    <ScreenHeader title="Zakat Calculator" onBack={() => navigate('home')} />
    <div className="estimate-hero"><IconBadge icon={Coins} large /><h3>Your Estimated Zakat</h3><div className="large-amount">{money(summary.estimatedDue, currency, true)}</div><p>From the assets and liabilities you entered.</p><button className="mint-button" onClick={editAssets}><Pencil size={16} />Edit assets</button></div>
    <div className="breakdown">
      <div><span>Total assets</span><strong>{money(summary.totalAssets, currency)}</strong></div>
      <div><span>Deductible liabilities</span><strong>−{money(summary.liabilities, currency)}</strong></div>
      <div><span>Illustrative nisab <small>(not live)</small></span><strong>{money(profile.illustrativeNisab, currency)}</strong></div>
      <div><span>Illustrative rate</span><strong>{profile.illustrativeRate * 100}%</strong></div>
      <div className="breakdown-total"><strong>Estimated Zakat Due</strong><strong>{money(summary.estimatedDue, currency, true)}</strong></div>
    </div>
    <p className="formula-note">Simplified example: max(0, assets − liabilities) × 2.5%. This demo does not test nisab or holding-period eligibility.</p>
    <SectionHeader title="Your entered assets" action="Edit" onAction={editAssets} />
    <div className="asset-list">{fields.slice(0, 4).map(field => <AssetRow key={field.key} icon={field.icon} label={field.label} value={profile.assets[field.key]} currency={currency} />)}</div>
    <Notice>Educational estimate, not a fatwa. Real eligibility depends on dated precious-metal rates, lunar holding period (haul), asset categories, debt treatment and scholarly methodology. The nisab shown is a nonlive example, not a current regional threshold. Consult a qualified scholar for a definitive ruling.</Notice>
    <p className="screen-footnote"><DemoTag>USD prototype</DemoTag> Updated {displayDate(profile.updatedAt)}</p>
  </div>;
}

export function AssetModal({ profile, onSaved, onClose }) {
  const [draft, setDraft] = useState(Object.fromEntries(fields.map(({ key }) => [key, String(profile.assets[key])])));
  const [pending, setPending] = useState(false);
  const [error, setError] = useState('');
  const [validation, setValidation] = useState('');
  const values = Object.fromEntries(Object.entries(draft).map(([key, value]) => [key, Number(value)]));
  let preview = null;
  try { if (Object.values(draft).every(value => value !== '')) preview = estimateZakat(values, profile.illustrativeRate); } catch { /* Invalid drafts stay editable. */ }
  async function save(event) {
    event.preventDefault();
    try {
      if (Object.values(draft).some(value => value === '')) throw new Error('Enter an amount in every field. Use 0 if none.');
      validateAssets(values);
      setValidation('');
    } catch (reason) { setValidation(reason.message); return; }
    setPending(true); setError('');
    try {
      const updated = await saveZakatProfile({ currency: profile.currency, assets: values });
      onSaved(updated);
    } catch (reason) { setError(reason.message); }
    finally { setPending(false); }
  }
  return <Modal title="Edit your assets" onClose={onClose} busy={pending}>
    <p>Use sample amounts in USD. Nothing is connected to your bank, and this demo resets on refresh.</p>
    <form onSubmit={save}>
      <fieldset disabled={pending} className="asset-fields"><legend className="visually-hidden">Assets and liabilities in USD</legend>
        {fields.map(({ key, label }) => <label className="asset-field" key={key}><span>{label}</span><span className="money-input"><span>$</span><input aria-label={label} type="number" inputMode="decimal" min="0" max={maxAmount} step="0.01" required value={draft[key]} onChange={event => { setDraft(current => ({ ...current, [key]: event.target.value })); setValidation(''); }} /></span></label>)}
      </fieldset>
      {preview && <div className="estimate-preview"><span>Preview estimate</span><strong>{money(preview.estimatedDue, profile.currency, true)}</strong></div>}
      {validation && <InlineError message={validation} />}
      {error && <InlineError message={error} />}
      <PrimaryButton type="submit" disabled={pending}>{pending ? <><LoaderCircle size={17} className="spinner" />Saving assets…</> : <><Check size={17} />{error ? 'Retry saving assets' : 'Save assets'}</>}</PrimaryButton>
      <p className="modal-note">Provisional 2.5% illustration, not a religious ruling.</p>
    </form>
  </Modal>;
}
