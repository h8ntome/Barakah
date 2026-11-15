import { useEffect, useState } from "react";
import { BottomTabs, DesktopPanel, RequestState } from "./components/ui.jsx";
import Home from "./screens/Home.jsx";
import Zakat from "./screens/Zakat.jsx";
import Invest from "./screens/Invest.jsx";
import Chat from "./screens/Chat.jsx";
import Give from "./screens/Give.jsx";
import Auth from "./screens/Auth.jsx";
import {
  getSession,
  refreshSession,
  subscribeSession,
} from "./services/index.js";
function Workspace({ user, activeTab, navigate }) {
  const [version, setVersion] = useState(0);
  const onChanged = () => setVersion((value) => value + 1);
  return (
    <div className="screen-pages">
      <section
        className="screen-page"
        hidden={activeTab !== "home"}
        aria-label="Home"
      >
        <Home
          user={user}
          navigate={navigate}
          version={version}
          onChanged={onChanged}
        />
      </section>
      <section
        className="screen-page"
        hidden={activeTab !== "zakat"}
        aria-label="Zakat"
      >
        <Zakat navigate={navigate} onChanged={onChanged} />
      </section>
      <section
        className="screen-page"
        hidden={activeTab !== "invest"}
        aria-label="Invest"
      >
        <Invest navigate={navigate} onChanged={onChanged} />
      </section>
      <section
        className="screen-page"
        hidden={activeTab !== "chat"}
        aria-label="AI Chat"
      >
        <Chat user={user} navigate={navigate} active={activeTab === "chat"} />
      </section>
      <section
        className="screen-page"
        hidden={activeTab !== "give"}
        aria-label="Give"
      >
        <Give navigate={navigate} onChanged={onChanged} />
      </section>
    </div>
  );
}
export default function App({ initialResetToken = "" }) {
  const [resetToken, setResetToken] = useState(initialResetToken);
  const [user, setUser] = useState(getSession);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [attempt, setAttempt] = useState(0);
  const [activeTab, setActiveTab] = useState("home");
  useEffect(() => subscribeSession(setUser), []);
  useEffect(() => {
    let current = true;
    setLoading(true);
    setError(null);
    if (
      initialResetToken ||
      !document.cookie
        .split("; ")
        .some((cookie) => cookie.startsWith("csrf_token="))
    ) {
      setLoading(false);
      return;
    }
    refreshSession()
      .catch((failure) => {
        if (current && failure.status !== 401) setError(failure.message);
      })
      .finally(() => {
        if (current) setLoading(false);
      });
    return () => {
      current = false;
    };
  }, [attempt]);
  function navigate(tab) {
    setActiveTab(tab);
    document.title = `Barakah | ${{ home: "Overview", invest: "Invest", zakat: "Zakat", chat: "AI Guide", give: "Giving" }[tab]}`;
  }
  return (
    <div className="app-shell">
      <DesktopPanel activeTab={activeTab} navigate={navigate} />
      <main className="phone-region" aria-label="Barakah workspace">
        <div className="phone-frame">
          <div className="phone-screen">
            <RequestState
              resource={{
                loading,
                error,
                retry: () => setAttempt((value) => value + 1),
              }}
              label="your session"
            >
              {user ? (
                <Workspace
                  key={user.id}
                  user={user}
                  activeTab={activeTab}
                  navigate={navigate}
                />
              ) : (
                <Auth
                  initialResetToken={resetToken}
                  onResetComplete={() => setResetToken("")}
                />
              )}
            </RequestState>
            <BottomTabs activeTab={activeTab} navigate={navigate} />
          </div>
        </div>
        <p className="device-caption">A more intentional financial life.</p>
      </main>
    </div>
  );
}
