import { useState } from 'react';
import { BottomTabs, DesktopPanel, RequestState } from './components/ui.jsx';
import Home from './screens/Home.jsx';
import Zakat, { AssetModal } from './screens/Zakat.jsx';
import Invest from './screens/Invest.jsx';
import Chat from './screens/Chat.jsx';
import Give from './screens/Give.jsx';
import { getDashboard, getZakatProfile } from './services/index.js';
import { useResource } from './services/useResource.js';
import { estimateZakat } from './utils/finance.js';

function Workspace({ dashboard, initialProfile, activeTab, navigate }) {
  const [profile, setProfile] = useState(initialProfile);
  const [editingAssets, setEditingAssets] = useState(false);
  const [saved, setSaved] = useState(false);
  const summary = estimateZakat(profile.assets, profile.illustrativeRate);
  const editAssets = () => { setSaved(false); setEditingAssets(true); };
  return <>
    <div className="screen-pages">
      <section className="screen-page" hidden={activeTab !== 'home'} aria-label="Home"><Home dashboard={dashboard} summary={summary} currency={profile.currency} navigate={navigate} editAssets={editAssets} /></section>
      <section className="screen-page" hidden={activeTab !== 'zakat'} aria-label="Zakat"><Zakat profile={profile} summary={summary} navigate={navigate} editAssets={editAssets} /></section>
      <section className="screen-page" hidden={activeTab !== 'invest'} aria-label="Invest"><Invest navigate={navigate} /></section>
      <section className="screen-page" hidden={activeTab !== 'chat'} aria-label="AI Chat"><Chat navigate={navigate} active={activeTab === 'chat'} /></section>
      <section className="screen-page" hidden={activeTab !== 'give'} aria-label="Give"><Give navigate={navigate} /></section>
    </div>
    <div className="visually-hidden" role="status">{saved ? 'Assets saved. Your overview and zakat estimate have been updated.' : ''}</div>
    {editingAssets && <AssetModal profile={profile} onClose={() => setEditingAssets(false)} onSaved={updated => { setProfile(updated); setEditingAssets(false); setSaved(true); }} />}
  </>;
}

export default function App() {
  const [activeTab, setActiveTab] = useState('home');
  const dashboard = useResource(getDashboard);
  const profile = useResource(getZakatProfile);
  function navigate(tab) {
    setActiveTab(tab);
    document.title = `Barakah | ${{ home: 'Overview', invest: 'Invest', zakat: 'Zakat', chat: 'AI Guide', give: 'Giving' }[tab]}`;
  }
  return <div className="app-shell"><DesktopPanel activeTab={activeTab} navigate={navigate} />
    <main className="phone-region" aria-label="Barakah interactive demo">
      <div className="phone-frame"><div className="phone-screen">
        <RequestState resource={dashboard} label="your overview"><RequestState resource={profile} label="your assets">{dashboard.data && profile.data && <Workspace dashboard={dashboard.data} initialProfile={profile.data} activeTab={activeTab} navigate={navigate} />}</RequestState></RequestState>
        <BottomTabs activeTab={activeTab} navigate={navigate} />
      </div></div>
      <p className="device-caption">A more intentional financial life.</p>
    </main>
  </div>;
}
