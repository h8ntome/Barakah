import { useState } from 'react';
import { ArrowUpRight, BarChart3, BookOpen, Leaf, ShieldCheck } from 'lucide-react';
import { DemoTag, IconBadge, Notice, PortfolioLegend, PrimaryButton, RequestState, ScreenHeader, SectionHeader, SegmentedControl, Sparkline } from '../components/ui.jsx';
import { getInvestmentEducation, getPortfolio } from '../services/index.js';
import { useResource } from '../services/useResource.js';
import { money } from '../utils/finance.js';

export default function Invest({ navigate }) {
  const [segment, setSegment] = useState('portfolio');
  const portfolio = useResource(getPortfolio);
  const education = useResource(getInvestmentEducation);
  const data = portfolio.data;
  let stop = 0;
  const donut = data?.allocations.map(item => { const from = stop; stop += item.percent; return `${item.color} ${from}% ${stop}%`; }).join(', ');
  return <div className="screen-content inner-screen">
    <ScreenHeader title="Halal Investing" onBack={() => navigate('home')} extra={<span className="header-symbol"><Leaf size={21} /></span>} />
    <SegmentedControl label="Investment view" value={segment} onChange={setSegment} options={[{ id: 'portfolio', label: 'My portfolio' }, { id: 'explore', label: 'Explore' }]} />
    {segment === 'portfolio' ? <RequestState resource={portfolio} label="your sample portfolio">{data && <>
      {data.holdings.length ? <>
        <section className="portfolio-summary"><div><p className="secondary">Portfolio value <DemoTag /></p><div className="large-amount">{money(data.value, data.currency)}</div><p className="growth"><ArrowUpRight size={15} />+{data.sampleChangePercent}% <span>({data.samplePeriodDays}d sample)</span></p></div><Sparkline values={data.trend} /></section>
        <div className="trust-banner"><ShieldCheck size={26} /><div><strong>Let your values guide you.</strong><p>Verify each security with a reputable, current Sharia screening method.</p></div></div>
        <SectionHeader title="Your allocation" /><div className="allocation"><div className="donut" style={{ background: `conic-gradient(${donut})` }} role="img" aria-label={`Sample allocation: ${data.allocations.map(item => item.label + ' ' + item.percent + '%').join(', ')}`}><div><strong>{money(data.value, data.currency)}</strong><span>Total sample</span></div></div><PortfolioLegend allocations={data.allocations} /></div>
        <SectionHeader title="Sample holdings" /><p className="section-description">Fictional baskets, not real tickers.</p><div className="holdings">{data.holdings.map(holding => <div key={holding.id} className="holding"><span className="holding-mark">{holding.name.slice(0, 1)}</span><div><strong>{holding.name}</strong><span>{holding.category} · Fictional</span></div><strong>{money(holding.value, data.currency)}</strong></div>)}</div>
      </> : <div className="empty-state"><BarChart3 size={28} /><h3>No sample holdings</h3><p>Start by learning what to review before investing.</p></div>}
      <PrimaryButton onClick={() => setSegment('explore')}><BookOpen size={18} />Explore investment criteria</PrimaryButton>
      <Notice>Illustrative portfolio and returns; no verified screening, live prices or trades. The sample portfolio is separate from your zakat investment entry. Investments carry risk; returns are never guaranteed.</Notice>
    </>}</RequestState> : <RequestState resource={education} label="investment education"><div className="education-hero"><IconBadge icon={Leaf} large /><h3>Grow your understanding.</h3><p>Three things to review before choosing an investment.</p></div><div className="education-list">{education.data?.map((item, index) => { const Icon = [Leaf, BarChart3, ShieldCheck][index % 3]; return <article key={item.id}><Icon size={23} /><div><h3>{item.title}</h3><p>{item.description}</p></div></article>; })}</div><Notice>These are general educational concepts, not a compliance certificate, fatwa or personalized financial advice. Methodologies differ and screening status changes over time.</Notice></RequestState>}
  </div>;
}
