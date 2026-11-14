import { useEffect, useRef, useState } from 'react';
import { ArrowUpRight, LoaderCircle, Send, Sparkles } from 'lucide-react';
import { DemoTag, InlineError, RequestState, ScreenHeader } from '../components/ui.jsx';
import { getAdvisorContext, sendAdvisorMessage } from '../services/index.js';
import { useResource } from '../services/useResource.js';

export default function Chat({ navigate, active }) {
  const context = useResource(getAdvisorContext);
  return <div className="chat-screen">
    <ScreenHeader title="AI Financial Advisor" onBack={() => navigate('home')} extra={<span className="header-symbol"><Sparkles size={21} /></span>} />
    <div className="chat-status"><Sparkles size={15} /><strong>Your Barakah guide</strong><DemoTag>Local demo</DemoTag></div>
    <RequestState resource={context} label="your guide">{context.data && <Conversation context={context.data} active={active} />}</RequestState>
  </div>;
}

function Conversation({ context, active }) {
  const [messages, setMessages] = useState([context.welcomeMessage]);
  const [draft, setDraft] = useState('');
  const [pending, setPending] = useState(false);
  const [failedText, setFailedText] = useState('');
  const [error, setError] = useState('');
  const scrollRef = useRef(null);
  const inputRef = useRef(null);
  useEffect(() => {
    if (!active) return;
    const scroll = scrollRef.current;
    scroll?.scrollTo({ top: scroll.scrollHeight, behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth' });
  }, [messages, pending, error, active]);

  async function send(text, retry = false) {
    const question = text.trim();
    if (!question || pending || question.length > 1000) return;
    if (!retry) {
      setMessages(current => [...current, { id: crypto.randomUUID(), role: 'user', text: question, createdAt: new Date().toISOString(), isDemo: true }]);
      setDraft('');
    }
    setPending(true); setError(''); setFailedText('');
    try {
      const reply = await sendAdvisorMessage({ text: question, conversationId: 'conversation-demo-001' });
      setMessages(current => [...current, reply]);
    } catch (reason) { setError(reason.message); setFailedText(question); }
    finally { setPending(false); }
  }
  return <>
    <div className="chat-scroll" ref={scrollRef}>
      <p className="chat-privacy">Example responses, not a live AI model.<br />Please don’t share sensitive financial information.</p>
      <div className="conversation" role="log" aria-label="Demo advisor conversation" aria-live="polite">
        {messages.map(message => <div className={`message-row ${message.role}`} key={message.id}>{message.role === 'assistant' && <span className="assistant-avatar" aria-hidden="true"><Sparkles size={16} /></span>}<div className="message-bubble"><span className="visually-hidden">{message.role === 'assistant' ? 'Barakah guide: ' : 'You: '}</span>{message.text}</div></div>)}
      </div>
      {messages.length === 1 && <div className="suggestions"><p>A place to start</p>{context.starterQuestions.map(question => <button key={question} onClick={() => send(question)}>{question}<ArrowUpRight size={15} /></button>)}</div>}
      {pending && <p className="reply-pending" role="status"><LoaderCircle size={16} className="spinner" />Preparing a local example…</p>}
      {error && <><InlineError message={error} onRetry={() => send(failedText, true)} /><button className="text-button edit-question" onClick={() => { setDraft(failedText); setFailedText(''); setError(''); setMessages(current => current.slice(0, -1)); inputRef.current?.focus(); }}>Edit question instead</button></>}
    </div>
    <p className="chat-disclaimer">Educational examples, not financial advice or a fatwa.</p>
    <form className="chat-composer" onSubmit={event => { event.preventDefault(); send(draft); }}>
      <input ref={inputRef} aria-label="Ask about Islamic finance" placeholder="Ask about Islamic finance..." value={draft} maxLength={1000} disabled={pending || !!failedText} onChange={event => setDraft(event.target.value)} />
      <button type="submit" aria-label="Send message" disabled={!draft.trim() || pending || !!failedText}><Send size={19} /></button>
    </form>
  </>;
}
