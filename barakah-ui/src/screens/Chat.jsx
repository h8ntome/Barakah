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
export default function Chat({ user, navigate, active }) {
  const context = useResource(api.getAdvisorContext);
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
      setError(failure.message);
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
          label="Conversation"
          value={conversationId}
          onChange={(value) => {
            setConversationId(value);
            setError("");
          }}
          disabled={sending}
          options={[
            { value: "", label: "New conversation" },
            ...(conversations.data || []).map((item) => ({
              value: item.id,
              label: `${item.created_at.slice(0, 16).replace("T", " ")} · ${item.id.slice(0, 6)}`,
            })),
          ]}
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
          Educational guidance, not a fatwa or personalized investment advice.
          Only your current question is sent to the configured model;
          conversation history is stored in your account. Avoid sensitive
          details.
        </Notice>
        {!user.ai_consent && (
          <Notice>
            Enable advisor consent in Home → Settings before sending a question.
            You can still review or delete your conversation history.
          </Notice>
        )}
        {!conversationId && (
          <RequestState resource={context} label="advisor context">
            {context.data && (
              <>
                <div className="message-row assistant">
                  <div className="message-bubble">
                    {context.data.welcome_message.text}
                    <p className="message-meta">
                      {context.data.welcome_message.is_demo
                        ? "Local demonstration response"
                        : "Educational guidance"}
                    </p>
                  </div>
                </div>
                <div className="suggestions">
                  <p>Start with a question</p>
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
                      ? "Local demonstration response"
                      : "Model-generated · May be inaccurate"}
                  </p>
                )}
              </div>
            </div>
          ))}
        </RequestState>
        {sending && (
          <p className="reply-pending" role="status">
            Waiting for the advisor…
          </p>
        )}
        {error && (
          <InlineError
            message={`${error} Your draft is kept. Review the conversation before resending if the connection was interrupted.`}
          />
        )}
        <div ref={bottom} />
      </div>
      <p className="chat-disclaimer">
        Not a substitute for qualified scholarly or financial advice.
      </p>
      <form className="chat-composer" onSubmit={send}>
        <input
          aria-label="Message to advisor"
          value={text}
          onChange={(event) => setText(event.target.value)}
          placeholder="Ask a finance question…"
          maxLength={1000}
          disabled={sending || !user.ai_consent}
          required
        />
        <button
          type="submit"
          aria-label="Send message"
          disabled={sending || !user.ai_consent || !text.trim()}
        >
          <Send size={18} />
        </button>
      </form>
    </div>
  );
}
