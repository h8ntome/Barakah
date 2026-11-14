import { BarChart3, ChevronRight, Coins, Heart, Moon, Sparkles, Sun, Wallet } from 'lucide-react';
import { FinancialOverview, IconBadge, QuickAction, SectionHeader } from '../components/ui.jsx';
import { money } from '../utils/finance.js';

export default function Home({ dashboard, summary, currency, navigate, editAssets }) {
  return <div className="screen-content home-screen">
    <header className="home-hero">
      <div className="hero-art" aria-hidden="true"><Moon className="hero-moon" size={32} strokeWidth={1.2} /><div className="mosque-dome main-dome" /><div className="mosque-dome small-dome" /><div className="minaret one" /><div className="minaret two" /><div className="hero-hill" /></div>
      <div className="hero-copy"><p>Assalamu Alaikum, {dashboard.displayName}</p><h2>Welcome to Barakah.</h2><span>A little intention. A brighter tomorrow.</span></div>
      <span className="profile-monogram" aria-label={`Sample profile: ${dashboard.displayName}`}>{dashboard.displayName.slice(0, 1)}</span>
    </header>
    <div className="home-body">
      <FinancialOverview dashboard={dashboard} summary={summary} currency={currency} />
      <div className="quick-actions">
        <QuickAction icon={Coins} tone="mint" label="Zakat" onClick={() => navigate('zakat')} />
        <QuickAction icon={Heart} tone="peach" label="Sadaqah" onClick={() => navigate('give')} />
        <QuickAction icon={BarChart3} tone="sage" label="Invest" onClick={() => navigate('invest')} />
        <QuickAction icon={Sparkles} tone="blue" label="AI Advisor" onClick={() => navigate('chat')} />
      </div>
      <SectionHeader title="Your priorities" />
      <div className="priority-list">
        <button className="priority-row" onClick={() => navigate('zakat')}><IconBadge icon={Coins} /><span><strong>Estimated zakat</strong><span>{money(summary.estimatedDue, currency, true)} from your entered assets</span></span><ChevronRight size={18} /></button>
        <button className="priority-row" onClick={editAssets}><IconBadge icon={Wallet} tone="blue" /><span><strong>Update your assets</strong><span>A clearer picture starts with your numbers</span></span><ChevronRight size={18} /></button>
      </div>
      <section className="insight-card"><Sun size={25} /><div><h3>Today's Insight</h3><p>{dashboard.insight}</p></div></section>
      <p className="screen-footnote">Your demo workspace · USD · Changes reset on refresh</p>
    </div>
  </div>;
}
