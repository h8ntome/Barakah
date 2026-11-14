import { useEffect, useId, useRef } from 'react';
import {
  ArrowLeft, ArrowRight, ArrowUpRight, BarChart3, BatteryFull, BookOpen,
  ChevronRight, Coins, Droplets, Heart, Home, Info, Landmark, LoaderCircle,
  MessageCircle, RefreshCw, ShieldCheck, Signal, Sparkles, Star, Wifi, X,
} from 'lucide-react';
import { money } from '../utils/finance.js';

export const destinations = [
  { id: 'home', icon: Home, label: 'Home', title: 'Overview' },
  { id: 'invest', icon: BarChart3, label: 'Invest', title: 'Investments' },
  { id: 'zakat', icon: Coins, label: 'Zakat', title: 'Zakat calculator' },
  { id: 'chat', icon: MessageCircle, label: 'AI Chat', title: 'AI financial guide' },
  { id: 'give', icon: Heart, label: 'Give', title: 'Sadaqah & giving' },
];

export function Brand() {
  return <div className="brand"><svg className="brand-mark" viewBox="0 0 48 52" fill="none" aria-hidden="true">
    <path d="M4 46V27C4 16 14 11 24 3c10 8 20 13 20 24v19H4Z" stroke="currentColor" strokeWidth="2" strokeLinejoin="round" />
    <path d="M4 46c9 0 14-6 20-6s11 6 20 6" stroke="currentColor" strokeWidth="2" />
    <path d="M27 19a9 9 0 1 0 7 14 9 9 0 0 1-7-14Z" stroke="currentColor" strokeWidth="1.8" strokeLinejoin="round" />
    <path d="m34 19 1.1 2.8L38 23l-2.9 1.1L34 27l-1.1-2.9L30 23l2.9-1.2L34 19Z" fill="currentColor" />
  </svg><span>Barakah</span></div>;
}

export function DesktopPanel({ activeTab, navigate }) {
  return <aside className="desktop-panel">
    <header><Brand /><p className="brand-tagline">Islamic Finance for a Blessed Tomorrow.</p></header>
    <div className="desktop-story"><h1>Your money.<br />Your values.<br />A blessed tomorrow.</h1>
      <p>A little more clarity. A little more purpose.<br />Make room for what matters in your financial life.</p>
    </div>
    <nav className="desktop-nav" aria-label="Desktop navigation">{destinations.map(({ id, icon: Icon, title }) =>
      <button key={id} onClick={() => navigate(id)} className={activeTab === id ? 'active' : ''} aria-current={activeTab === id ? 'page' : undefined}>
        <Icon size={20} /><span>{title}</span><ArrowRight size={17} />
      </button>)}
    </nav>
    <footer className="desktop-footer"><ShieldCheck size={22} /><p>Made for a more mindful financial life.<br /><span>An educational demo. No accounts or payments connected.</span></p></footer>
  </aside>;
}

export function StatusBar() {
  return <div className="status-bar" aria-hidden="true"><span>9:41</span><div><Signal size={14} /><Wifi size={14} /><BatteryFull size={20} /></div></div>;
}
export function BottomTabs({ activeTab, navigate }) {
  return <nav className="bottom-nav" aria-label="Main navigation">{destinations.map(({ id, icon: Icon, label }) =>
    <button key={id} className={activeTab === id ? 'selected' : ''} aria-current={activeTab === id ? 'page' : undefined} onClick={() => navigate(id)}>
      <Icon size={21} strokeWidth={activeTab === id ? 2.2 : 1.8} /><span>{label}</span>
    </button>)}
  </nav>;
}
export function ScreenHeader({ title, onBack, extra }) {
  return <header className="screen-header"><button className="icon-button" aria-label="Back to Home" onClick={onBack}><ArrowLeft size={21} /></button><h2>{title}</h2>{extra || <span className="header-spacer" />}</header>;
}
export function PrimaryButton({ children, className = '', type = 'button', ...props }) {
  return <button type={type} className={`primary-button ${className}`} {...props}>{children}</button>;
}
export function IconBadge({ icon: Icon, tone = 'mint', large = false }) {
  return <span className={`icon-badge ${tone} ${large ? 'large' : ''}`}><Icon size={large ? 32 : 22} strokeWidth={1.9} /></span>;
}
export function DemoTag({ children = 'Sample data' }) { return <span className="demo-tag">{children}</span>; }
export function Notice({ children }) { return <div className="notice"><Info size={17} /><p>{children}</p></div>; }
export function SectionHeader({ title, action, onAction }) {
  return <div className="section-header"><h3>{title}</h3>{action && <button className="text-button" onClick={onAction}>{action}<ChevronRight size={15} /></button>}</div>;
}
export function SegmentedControl({ options, value, onChange, label }) {
  return <div className="segmented-control" role="group" aria-label={label}>{options.map(option => <button key={option.id} aria-pressed={value === option.id} className={value === option.id ? 'selected' : ''} onClick={() => onChange(option.id)}>{option.label}</button>)}</div>;
}
export function QuickAction({ icon, tone, label, onClick }) {
  return <button className="quick-action" onClick={onClick}><IconBadge icon={icon} tone={tone} /><span>{label}</span></button>;
}
export function Sparkline({ values, label = 'Illustrative trend, not live market data' }) {
  const id = useId();
  const min = Math.min(...values), range = Math.max(...values) - min || 1;
  const points = values.map((value, index) => `${4 + index * 132 / (values.length - 1)},${56 - (value - min) * 47 / range}`).join(' ');
  return <svg className="sparkline" viewBox="0 0 140 66" role="img" aria-label={label}>
    <defs><linearGradient id={id} x1="0" y1="0" x2="0" y2="1"><stop stopColor="#10965A" stopOpacity=".18" /><stop offset="1" stopColor="#10965A" stopOpacity="0" /></linearGradient></defs>
    <polygon points={`4,66 ${points} 136,66`} fill={`url(#${id})`} /><polyline points={points} fill="none" stroke="#0B7750" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
  </svg>;
}
export function FinancialOverview({ summary, dashboard, currency }) {
  return <section className="overview-card" aria-label="Your Financial Overview"><div className="overview-heading"><h3>Your Financial Overview</h3><DemoTag /></div>
    <p className="secondary">Total net worth</p><div className="overview-figure"><strong className="financial-amount">{money(summary.netWorth, currency)}</strong><Sparkline values={dashboard.trend} /></div>
    <p className="growth"><ArrowUpRight size={15} />+{dashboard.sampleChangePercent}% <span>({dashboard.samplePeriodDays}d sample)</span></p>
  </section>;
}
export function AssetRow({ icon: Icon, label, value, currency }) {
  return <div className="asset-row"><span><Icon size={19} />{label}</span><strong>{money(value, currency)}</strong></div>;
}
export function PortfolioLegend({ allocations }) {
  return <ul className="portfolio-legend">{allocations.map(item => <li key={item.id}><span className="color-dot" style={{ background: item.color }} /><span>{item.label}</span><strong>{item.percent}%</strong></li>)}</ul>;
}
const causeIcons = { water: Droplets, care: Heart, masjid: Landmark, school: BookOpen };
export function CauseCard({ cause, onClick }) {
  const Icon = causeIcons[cause.illustration] || Heart;
  const percent = Math.min(100, cause.raised / cause.goal * 100);
  return <button className="cause-card" onClick={onClick}><span className={`cause-art ${cause.illustration}`} aria-hidden="true"><Icon size={34} strokeWidth={1.6} /><span className="art-ground" /><Star className="art-star" size={10} /></span>
    <span className="cause-info"><strong>{cause.title}</strong><span>{money(cause.raised, cause.currency)} <span className="secondary">of {money(cause.goal, cause.currency)}</span></span><span className="progress-track" role="img" aria-label={`${Math.round(percent)}% of sample goal`}><span style={{ width: `${percent}%` }} /></span></span><ChevronRight size={18} />
  </button>;
}
export function RequestState({ resource, label = 'your information', children }) {
  if (resource.loading) return <div className="request-state" role="status"><LoaderCircle className="spinner" size={25} /><strong>Loading {label}…</strong><span>Preparing your local demo</span><div className="skeleton" /><div className="skeleton short" /></div>;
  if (resource.error) return <div className="request-state error" role="alert"><Info size={26} /><strong>We couldn’t load {label}</strong><p>{resource.error}</p><PrimaryButton onClick={resource.retry}><RefreshCw size={17} />Try again</PrimaryButton></div>;
  return children;
}
export function InlineError({ message, onRetry }) {
  return <div className="inline-error" role="alert"><p>{message}</p>{onRetry && <button className="text-button" onClick={onRetry}><RefreshCw size={15} />Try again</button>}</div>;
}
export function Modal({ title, children, onClose, busy = false }) {
  const ref = useRef(null);
  const titleId = useId();
  useEffect(() => {
    const dialog = ref.current;
    const trigger = document.activeElement;
    dialog.showModal();
    return () => {
      dialog.close();
      if (trigger instanceof HTMLElement && trigger.isConnected) trigger.focus({ preventScroll: true });
    };
  }, []);
  return <dialog ref={ref} className="modal" aria-labelledby={titleId} aria-busy={busy} onKeyDown={event => {
    if (event.key !== 'Tab') return;
    const controls = [...event.currentTarget.querySelectorAll('button:not(:disabled), input:not(:disabled)')];
    const first = controls[0], last = controls.at(-1);
    if (!first) { event.preventDefault(); return; }
    if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
    else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
  }} onCancel={event => { event.preventDefault(); if (!busy) onClose(); }} onClick={event => {
    if (event.target !== event.currentTarget || busy) return;
    const box = event.currentTarget.getBoundingClientRect();
    if (event.clientX < box.left || event.clientX > box.right || event.clientY < box.top || event.clientY > box.bottom) onClose();
  }}><div className="modal-header"><h2 id={titleId}>{title}</h2><button type="button" className="icon-button" aria-label="Close dialog" onClick={onClose} disabled={busy}><X size={21} /></button></div>{children}</dialog>;
}
