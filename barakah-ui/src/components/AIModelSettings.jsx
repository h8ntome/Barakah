import { useEffect, useRef, useState } from "react";
import { ActionForm, Field } from "./forms.jsx";
import { InlineError, Notice, PrimaryButton, RequestState, SectionHeader } from "./ui.jsx";
import { useResource } from "../services/useResource.js";
import * as api from "../services/index.js";

export default function AIModelSettings({ user, active }) {
  const connection = useResource(api.getAIConnection, active);
  const [notice, setNotice] = useState("");
  const [error, setError] = useState("");
  return <section className="ai-settings" aria-label="AI Model">
    <SectionHeader title="AI Model" />
    {error && <InlineError message={error} />}
    <RequestState resource={connection} label="AI connection">
      {connection.data && <ConnectionForm key={connection.data.revision || "default"}
        saved={connection.data} user={user} active={active}
        onError={(message, refresh) => { setError(message); setNotice(""); if (refresh) connection.retry(); }}
        onChanged={(message) => { setError(""); setNotice(message); connection.retry(); }} />}
    </RequestState>
    {notice && <p className="save-status" role="status">{notice}</p>}
  </section>;
}

function ConnectionForm({ saved, user, active, onChanged, onError }) {
  const [mode, setMode] = useState(saved.mode);
  const [provider, setProvider] = useState(saved.provider || "openai");
  const [model, setModel] = useState(saved.mode === "external" ? saved.model_id || "" : "");
  const [base, setBase] = useState(saved.provider === "custom" ? saved.base_url || "" : "");
  const [key, setKey] = useState("");
  const [consent, setConsent] = useState(user.ai_consent);
  const [busy, setBusy] = useState("");
  const lock = useRef(false);
  useEffect(() => { setConsent(user.ai_consent); }, [user.ai_consent]);
  useEffect(() => { if (!active) setKey(""); }, [active]);
  const sameDestination = saved.provider === provider && (provider === "openai" || saved.base_url === base);
  const dirty = mode !== saved.mode || (mode === "external" &&
    (provider !== saved.provider || model !== saved.model_id || !sameDestination || key !== ""));
  async function perform(action) {
    if (lock.current) return;
    lock.current = true; setBusy(action); onError("");
    try {
      if (action === "save") {
        await api.saveAIConnection({ mode, expected_revision: saved.revision,
          ...(mode === "external" ? { provider, model_id: model.trim(),
            ...(provider === "custom" ? { base_url: base.trim() } : {}),
            ...(key ? { api_key: key } : {}) } : {}) });
        onChanged("AI connection saved. Review and save consent before sending or testing.");
      } else if (action === "test") {
        const result = await api.testAIConnection(saved.revision);
        onChanged(result.message);
      } else {
        await api.removeAIConnection(saved.revision);
        onChanged("Saved credential removed. AI is off; existing conversations remain available to review or delete.");
      }
    } catch (failure) {
      onError(failure.message + (action === "save" ? " Re-enter a new key if needed; it is not kept in this form after submitting." : ""), action === "test");
    } finally {
      setKey(""); lock.current = false; setBusy("");
    }
  }
  return <>
    <p className="ai-identity"><strong>Active: </strong>{saved.mode === "disabled" ? "Off — no model connected" :
      saved.mode === "local" ? "Barakah checkpoint · h8notme/barakah1" : `${saved.provider === "openai" ? "OpenAI" : "Custom provider"} · ${saved.model_id}`}</p>
    {saved.mode === "external" && <p className="formula-note">Destination: {saved.base_url}. Your provider, not the Barakah checkpoint. The configured model ID is a request, not independently verified identity.</p>}
    {!saved.external_available && <Notice>{user.is_demo ? "Create a personal account to save a private API key. Never put credentials in this disposable demo." : "User-provider AI needs secure server setup. The operator must enable it and configure a dedicated encryption key. Financial tools still work."}</Notice>}
    <form className="action-form" onSubmit={(event) => { event.preventDefault(); perform("save"); }}>
      <fieldset disabled={Boolean(busy)}>
        <Field label="AI source" value={mode} onChange={(value) => { setMode(value); setKey(""); }} options={[
          { value: "disabled", label: "Off" },
          ...(saved.local_available || saved.mode === "local" ? [{ value: "local", label: "Barakah checkpoint (private server)" }] : []),
          ...(saved.external_available || saved.mode === "external" ? [{ value: "external", label: "My API provider" }] : []),
        ]} />
        {mode === "local" && <p className="formula-note">Pinned checkpoint revision 912a5697cf9d85adf065ee512f509cfa236459d4. Private loopback service; availability is checked on send. No external fallback.</p>}
        {mode === "external" && <>
          <Field label="Provider" value={provider} onChange={(value) => { setProvider(value); setKey(""); }} options={[
            { value: "openai", label: "OpenAI" },
            ...(saved.custom_enabled || saved.provider === "custom" ? [{ value: "custom", label: "Custom OpenAI-compatible (advanced)" }] : []),
          ]} />
          {provider === "custom" && <Field label="Approved base URL" type="url" value={base} onChange={(value) => { setBase(value); setKey(""); }} required maxLength={500}
            placeholder="https://provider.example/v1" help="Exact operator-approved HTTPS destination only. Chat Completions protocol; not native Anthropic or Gemini APIs." />}
          <Field label="Model ID" value={model} onChange={setModel} required maxLength={160}
            placeholder="Exact model ID from your provider" help="Use a model your key can access. No model is selected or substituted automatically." />
          <Field label="API key" type="password" value={key} onChange={setKey} autoComplete="off" autoCapitalize="none" spellCheck={false}
            required={!saved.has_key || !sameDestination} minLength={16} maxLength={4096}
            placeholder={saved.has_key && sameDestination ? "Saved key — leave blank to keep" : "Paste your provider API key"}
            help="Write-only. Stored encrypted on the server; never returned by the API or saved in browser storage. A different destination requires a new key." />
        </>}
        <PrimaryButton type="submit" disabled={!dirty || mode === "external" && !saved.external_available}>
          {busy === "save" ? "Saving connection…" : "Save AI connection"}
        </PrimaryButton>
        <p className="formula-note">Changing the source, model or key resets consent. Changing source or model requires a new conversation. No silent fallback.</p>
        {saved.mode !== "disabled" && <>
          <button type="button" className="text-button" disabled={dirty || !user.ai_consent}
            onClick={() => perform("test")}>{busy === "test" ? "Testing connection…" : "Test saved connection"}</button>
          <p className="formula-note">Save changes and consent first. Testing sends a fixed synthetic question, not your history, and may incur a provider charge. Limits: {saved.requests_per_minute}/minute and {saved.requests_per_day}/day; failed attempts and tests count.</p>
          <p className="formula-note">Last saved test: {saved.test_status === "success" ? "Valid reply received — not a quality or safety certification" : saved.test_status === "failed" ? `Failed (${saved.test_error})` : "Not tested"}{saved.tested_at ? ` · ${new Date(saved.tested_at).toLocaleString()}` : ""}.</p>
          <details className="details-section"><summary>Remove connection{saved.has_key ? " and saved key" : ""}</summary>
            <p className="formula-note">This turns AI off without deleting your conversations. To invalidate the key itself, revoke it with your provider too.</p>
            <button type="button" className="text-button" onClick={() => perform("remove")}>Confirm remove connection</button>
          </details>
        </>}
      </fieldset>
    </form>
    <ActionForm label="Save AI consent" onSubmit={async () => {
      if (lock.current || dirty) throw new Error("Save or discard connection changes before saving consent.");
      lock.current = true; setBusy("consent");
      try { await api.updateProfile({ ai_consent: consent }); }
      finally { lock.current = false; setBusy(""); }
    }}>
      <label className="check-field"><input type="checkbox" checked={consent} disabled={Boolean(busy) || dirty}
        onChange={(event) => setConsent(event.target.checked)} /><span>
        I consent to sending my questions and recent conversation history to the saved AI destination above. Save AI consent before sending. No financial records are included automatically.
        Uncheck and save to stop future sends; this cannot recall text already sent. Consent does not connect a model: when AI is unavailable, no text is sent or saved.
      </span></label>
      <p className="formula-note">External providers receive your text and may retain it under their own policies and bill your account. Do not send private financial data or secrets.</p>
    </ActionForm>
    <p className="formula-note">This project is a prototype and is not financial advice. Islamic-finance answers are educational, not religious certification.</p>
  </>;
}
