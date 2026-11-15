import { useEffect, useRef, useState } from "react";
import { Send, Sparkles } from "lucide-react";
import {
  InlineError,
  Notice,
  RequestState,
  ScreenHeader,
} from "../components/ui.jsx";
import { ActionForm, Empty, Field } from "../components/forms.jsx";
import { Pagination } from "../components/FinancialForms.jsx";
import { useResource } from "../services/useResource.js";
import * as api from "../services/index.js";
import { conversationOptions } from "../utils/conversationOptions.js";
export default function Chat({ navigate, active }) {
  const context = useResource(api.getAdvisorContext);
  const configured = context.data?.status === "configured";
  const [offset, setOffset] = useState(0);
  const conversations = useResource(api.getConversations, {
    offset,
    limit: 50,
  });
  const [conversationId, setConversationId] = useState("");
  const messages = useResource(api.getMessages, conversationId);
  const [drafts, setDrafts] = useState({});
  const text = drafts[conversationId || "new"] || "";
  const setText = (value) =>
    setDrafts((previous) => ({
      ...previous,
      [conversationId || "new"]: value,
    }));
  const [sending, setSending] = useState(false);
  const [error, setError] = useState("");
  const lock = useRef(false);
  const bottom = useRef(null);
  useEffect(() => {
    if (active) bottom.current?.scrollIntoView({ block: "nearest" });
  }, [messages.data, active]);
  async function send(event) {
    event.preventDefault();
    if (lock.current || !text.trim()) return;
    lock.current = true;
    setSending(true);
    setError("");
    try {
      const reply = await api.sendMessage({
        text: text.trim(),
        ...(conversationId ? { conversation_id: conversationId } : {}),
      });
      setText("");
      if (reply.conversation_id !== conversationId)
        setConversationId(reply.conversation_id);
      else messages.retry();
      conversations.retry();
    } catch (failure) {
      setError(failure.code === "ai_unavailable"
        ? "AI assistant unavailable — no model is connected. No message was saved."
        : failure.message);
    } finally {
      lock.current = false;
      setSending(false);
    }
  }
  return (
    <div className="chat-screen">
      <ScreenHeader
        title="AI financial guide"
        onBack={() => navigate("home")}
        extra={
          <span className="header-symbol">
            <Sparkles size={19} />
          </span>
        }
      />
      <div className="chat-toolbar">
        <Field
          label="Conversation history"
          value={conversationId}
          onChange={(value) => {
            setConversationId(value);
            setError("");
          }}
          disabled={sending}
          options={conversationOptions(conversations.data || [], conversationId)}
        />
        <div className="conversation-actions">
          <button
            className="text-button"
            disabled={sending}
            onClick={() => {
              setConversationId("");
              setError("");
            }}
          >
            New conversation
          </button>
          {conversationId && (
            <details>
              <summary>Delete conversation</summary>
              <ActionForm
                label="Confirm delete conversation"
                success=""
                onSubmit={async () => {
                  if (sending)
                    throw new Error("Wait for your message to finish.");
                  await api.deleteConversation(conversationId);
                  setDrafts((previous) => {
                    const next = { ...previous };
                    delete next[conversationId];
                    return next;
                  });
                  setConversationId("");
                  conversations.retry();
                }}
              />
            </details>
          )}
        </div>
        {conversations.error && (
          <InlineError
            message={conversations.error}
            onRetry={conversations.retry}
          />
        )}
        {(offset > 0 || conversations.data?.length === 50) && (
          <Pagination
            offset={offset}
            onChange={setOffset}
            count={conversations.data?.length || 0}
          />
        )}
      </div>
      <div className="chat-scroll">
        <Notice>
          {!context.data
            ? "AI configuration not yet verified. Sending checks availability; your financial tools remain available."
            : configured
              ? "AI endpoint configured — availability is checked on send. Save consent in Settings first: your question and recent conversation history will be sent, never your financial records automatically. Responses may be inaccurate and are not authoritative."
              : "AI assistant unavailable — no model is connected. You can try sending a question to check availability; no advice is generated and no new messages are saved. Your financial tools remain available."}
        </Notice>
        {conversationId && context.data?.status === "unavailable" && (
          <Notice>
            Historical conversation only. These saved messages are not new advice
            or evidence of a connected AI. You can review or delete this history.
          </Notice>
        )}
        {!conversationId && (
          <Empty>No messages yet. {configured ? "Messages are saved only after a successful AI reply." : "Drafts are not saved to your account."}</Empty>
        )}
        {!conversationId && (
          <RequestState resource={context} label="advisor context">
            {context.data && (
              <>
                <div className="message-row assistant">
                  <div className="message-bubble">
                    {context.data.welcome_message.text}
                    <p className="message-meta">
                      Service status · Not an AI response
                    </p>
                  </div>
                </div>
                <div className="suggestions">
                  <p>{configured ? "Example questions · Not advice" : "Example questions · AI not connected"}</p>
                  {context.data.starter_questions.map((question) => (
                    <button
                      key={question}
                      disabled={sending}
                      onClick={() => setText(question)}
                    >
                      {question}
                    </button>
                  ))}
                </div>
              </>
            )}
          </RequestState>
        )}
        <RequestState resource={messages} label="conversation">
          {conversationId && !messages.data?.length && (
            <Empty>No messages in this conversation.</Empty>
          )}
          {messages.data?.map((message) => (
            <div
              key={message.id}
              className={`message-row ${message.role === "user" ? "user" : "assistant"}`}
            >
              <div className="message-bubble">
                {message.text}
                {message.role === "assistant" && (
                  <p className="message-meta">
                    {message.is_demo
                      ? "Historical demonstration · Not AI advice"
                      : "Model response · May be inaccurate, not authoritative"}
                  </p>
                )}
              </div>
            </div>
          ))}
        </RequestState>
        {sending && (
          <p className="reply-pending" role="status">
            {configured ? "Generating a response…" : "Checking AI availability…"}
          </p>
        )}
        {error && (
          <InlineError
            message={`${error} Your draft is kept; you can try again.`}
          />
        )}
        <div ref={bottom} />
      </div>
      <p className="chat-disclaimer">
        Model suggestions are not Sharia-screened. Verify calculations independently.
        Not a substitute for qualified scholarly or financial advice.
      </p>
      <form className="chat-composer" onSubmit={send}>
        <input
          aria-label="Message to advisor"
          value={text}
          onChange={(event) => setText(event.target.value)}
          placeholder="Ask a finance question…"
          maxLength={1000}
          disabled={sending}
          required
        />
        <button
          type="submit"
          aria-label="Send message"
          disabled={sending || !text.trim()}
        >
          <Send size={18} />
        </button>
      </form>
    </div>
  );
}
