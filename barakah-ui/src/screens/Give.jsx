import { useState } from 'react';
import { Check, Heart, LoaderCircle, Search } from 'lucide-react';
import { CauseCard, DemoTag, IconBadge, InlineError, Modal, Notice, PrimaryButton, RequestState, ScreenHeader, SectionHeader } from '../components/ui.jsx';
import { createDonationIntent, getCauses } from '../services/index.js';
import { useResource } from '../services/useResource.js';
import { money, validGift } from '../utils/finance.js';

export default function Give({ navigate }) {
  const [category, setCategory] = useState('All');
  const [query, setQuery] = useState('');
  const [chosenCause, setChosenCause] = useState(null);
  const causes = useResource(getCauses, { category, query });
  return <div className="screen-content inner-screen">
    <ScreenHeader title="Sadaqah & Giving" onBack={() => navigate('home')} />
    <div className="give-hero"><IconBadge icon={Heart} large /><h3>Give Sadaqah</h3><p>Small acts. Lasting kindness.<br />Make space for the causes you care about.</p></div>
    <label className="search-field"><Search size={19} /><input aria-label="Search causes" type="search" placeholder="Search causes..." maxLength={100} value={query} onChange={event => setQuery(event.target.value)} /></label>
    <div className="category-filters" role="group" aria-label="Cause category">{['All', 'Education', 'Relief', 'Masjid'].map(item => <button key={item} aria-pressed={category === item} className={category === item ? 'active' : ''} onClick={() => setCategory(item)}>{item}</button>)}</div>
    <SectionHeader title="A little good goes a long way" />
    <div className="causes-meta"><DemoTag>Illustrative causes</DemoTag><span aria-live="polite">{causes.data ? `${causes.data.length} found` : ''}</span></div>
    <RequestState resource={causes} label="causes">
      <div className="cause-list">{causes.data?.map(cause => <CauseCard key={cause.id} cause={cause} onClick={() => setChosenCause(cause)} />)}</div>
      {causes.data?.length === 0 && <div className="empty-state"><Search size={28} /><h3>No causes found</h3><p>Try another search or category.</p>{(query || category !== 'All') && <button className="mint-button" onClick={() => { setQuery(''); setCategory('All'); }}>Clear filters</button>}</div>}
    </RequestState>
    <Notice>All causes, funding figures and beneficiaries are illustrative. These are sadaqah examples, not verified zakat-eligible causes. No payment is processed.</Notice>
    {chosenCause && <DonationModal cause={chosenCause} onClose={() => setChosenCause(null)} />}
  </div>;
}

function DonationModal({ cause, onClose }) {
  const [amount, setAmount] = useState('25');
  const [preset, setPreset] = useState(25);
  const [pending, setPending] = useState(false);
  const [confirmation, setConfirmation] = useState(null);
  const [error, setError] = useState('');
  const numericAmount = Number(amount);
  const valid = validGift(numericAmount);
  async function confirm(event) {
    event.preventDefault();
    if (!valid || pending) return;
    setPending(true); setError('');
    try { setConfirmation(await createDonationIntent({ causeId: cause.id, amount: numericAmount, currency: cause.currency })); }
    catch (reason) { setError(reason.message); }
    finally { setPending(false); }
  }
  return <Modal title={confirmation ? 'A little kindness, imagined.' : cause.title} onClose={onClose} busy={pending}>
    {confirmation ? <div className="donation-success" role="status"><IconBadge icon={Check} large /><h3>Thank you for your intention.</h3><p>You explored a <strong>{money(confirmation.amount, confirmation.currency)}</strong> gift to {cause.title}.</p><div className="demo-confirmation"><strong>Demo only — no money moved.</strong><p>No payment was made, and no receipt or real donation was created.</p></div><PrimaryButton onClick={onClose}>Done</PrimaryButton></div> : <>
      <DemoTag>Demo gift · No payment</DemoTag><p>{cause.description}</p>
      <form onSubmit={confirm}><fieldset className="donation-fields" disabled={pending}><legend>Choose a sample gift</legend>
        <div className="amount-presets">{[10, 25, 50, 100].map(value => <button type="button" key={value} aria-pressed={preset === value} className={preset === value ? 'selected' : ''} onClick={() => { setPreset(value); setAmount(String(value)); setError(''); }}>{money(value, cause.currency)}</button>)}</div>
        <label className="custom-amount"><span>Or enter an amount (USD)</span><span className="money-input"><span>$</span><input type="number" inputMode="decimal" min="1" max="100000" step="0.01" value={amount} required onChange={event => { setPreset(null); setAmount(event.target.value); setError(''); }} aria-describedby="gift-amount-help" /></span></label>
        <p id="gift-amount-help" className="field-help">1–100,000 USD. Up to two decimal places.</p>
      </fieldset>
      {error && <InlineError message={error} />}
      <PrimaryButton type="submit" disabled={!valid || pending}>{pending ? <><LoaderCircle size={17} className="spinner" />Confirming demo gift…</> : <><Heart size={17} />{error ? 'Retry demo gift' : 'Confirm demo gift'}{valid ? ` · ${money(numericAmount, cause.currency)}` : ''}</>}</PrimaryButton>
      <p className="modal-note">This records a local demo intention, not a payment.</p></form>
    </>}
  </Modal>;
}
