# Opt-in local AI chat

Default `AI_MODE=unavailable` remains unchanged: no provider calls, no history or financial-context loading on send, no generated advice, and no new conversations/messages. Other financial tools work independently. This document supersedes historical unavailable-only AI integration notes **only for the explicit opt-in below**. No live model/browser validation is claimed by the implementation tests.

## Exact checkpoint and runtime

Use the **full checkpoint** `h8notme/barakah1` at revision `912a5697cf9d85adf065ee512f509cfa236459d4` (base architecture LiquidAI/LFM3-1.7B). There is no PEFT adapter or base-model fallback. `scripts/serve-local-ai.py` pins weights, tokenizer and custom-code revision. Inspect and trust that pinned model code before running. Weights remain outside the repository in the operator's Hugging Face cache; never commit weights, tokens, private hostnames or cache paths.

Use an existing compatible PyTorch/Transformers environment (the model needs LFM3/custom-code support). No new paid dependencies or installed system service are required. The service uses standard-library HTTP, SDPA, BF16 on a ROCm GPU (`torch.cuda` is also the ROCm API), or float32 on CPU. Generation is greedy, one beam, at most 384 new tokens, with `enable_thinking=False`. Do not replace this with a generic OpenAI endpoint: the response identity/metadata protocol is deliberate.

On the model host, from a checkout containing the script:

```sh
# Use the existing model runtime's Python. Run once; share this secret with the
# backend securely, not in command arguments, chat, browser code or version control.
export AI_TOKEN="$(python -c 'import secrets; print(secrets.token_urlsafe(48))')"
# Point HF_HUB_CACHE to your existing external cache if not the default.
export HF_HUB_OFFLINE=1  # complete pinned snapshot/custom code must already be cached
export AI_PORT=8765
export AI_GENERATION_TIMEOUT=75
python scripts/serve-local-ai.py
```

Warmup must succeed before the listener starts. The listener always binds **127.0.0.1**, never a public interface; there is no bind-address option. No prompt, response or authorization logging is implemented. The startup message contains only port and pinned identity. Keep infrastructure/proxy debug logs off too.

The authenticated POST `/generate` accepts only `{message,history:[{role,text}]}`. Limits: message 1,000 characters, 12 history entries / 12,000 history characters, 65,536 request bytes, 4,096 input tokens, 384 output tokens / 6,000 output characters. Oversized or invalid requests fail; they are not silently expanded or retried. A nonblocking lock returns 503 `busy` instead of queueing another generation. Deadlines are checked between generation steps, not a safe hard interruption of a stuck GPU kernel. A timed-out request never returns partial output; the model remains locked until its work actually exits. Restart the manually managed process if the runtime hangs. CPU warmup may require a longer timeout (maximum 290 seconds).

## Backend connection (same host or private SSH tunnel)

If the backend is elsewhere, run an SSH tunnel on the **backend host**, leaving both endpoints loopback-only:

```sh
ssh -N -o ExitOnForwardFailure=yes -o ServerAliveInterval=30 \
  -L 127.0.0.1:8765:127.0.0.1:8765 user@model-host
```

Use your privately configured SSH host/key; do not expose the model port or disable host-key verification. SSH must be available from the backend runtime. A stateless hosted function without this tunnel is **not** connected merely by setting `AI_MODE`.

Backend environment (see `backend/.env.example`):

```dotenv
AI_MODE=http
AI_URL=http://127.0.0.1:8765/generate
# AI_TOKEN must match the model service's randomly generated environment secret.
AI_TIMEOUT_SECONDS=90
```

Set `AI_TOKEN` securely, then restart the backend. Configuration rejects non-loopback URLs, URL credentials/query strings, weak/malformed tokens and timeouts outside 1–300 seconds. The backend does not follow redirects, use environment HTTP proxies or retry model calls. HTTPX timeouts bound individual network operations; elapsed response checks additionally reject slow streams (not an independent hard process deadline). Keep the service generation deadline below the backend timeout and configure upstream request timeouts accordingly. To disable, restore `AI_MODE=unavailable` and restart; no model connection then occurs.

## Consent, persistence and verification

1. Log in and inspect Chat. `/ai/health` and `/advisor/context` report **configured**, not ready/healthy: neither probes the model. An actual successful reply is needed to demonstrate inference.
2. In Settings, explicitly enable AI consent and **Save settings**. Without saved consent, no question/history is sent. Only the user's question and bounded recent history of their selected owned conversation leave the backend. Financial records are never loaded or added; `include_financial_context:true` is rejected in HTTP mode. Text manually entered by the user may itself be sensitive.
3. Send a question, then a follow-up. Successful replies are plain React text, never HTML, and are labeled non-authoritative. Verify the response in browser Network: HTTP 200, `response`, `conversation_id`, and `metadata` containing exact `model`/`revision`, SHA-256 of the fully rendered prompt (including system/history/template) and template, input/output token counts, and generation seconds. These are authenticated service attestations, not cryptographic proof of execution. Hashes can disclose guessable prompt equality: treat captured evidence as private.
4. Only after validated success are conversation + user/assistant messages committed atomically. The backend releases its DB transaction before inference, then rechecks account/session expiry and revocation, saved consent/profile version, conversation ownership/existence and history snapshot. An in-flight profile or conversation change rejects the result rather than overwriting new history. Concurrent generation may waste work but cannot append a stale follow-up.
5. Timeout, busy, malformed output or identity mismatch saves nothing. UI keeps the draft; sends are never automatically replayed, including after a 401. If a session expires, refresh/sign in and explicitly send again. After an ambiguous browser disconnect, reload history before manually retrying: the server may already have committed. Unchecking consent and saving stops future sends and rejects in-flight persistence, but cannot recall text already transmitted.

Metadata is returned with a successful send, not retained as a new database audit schema; save private evidence separately if needed. History is intentionally bounded, so older turns may not be seen. The model is educational, may hallucinate, and is not a scholar, financial authority or a source of financial-record mutations. No content safety guarantee, distributed admission control, hard GPU cancellation or production hosting readiness is claimed.

## Implementation checks (no weights needed)

```sh
cd backend
python -m pytest tests/test_ai_http.py tests/test_local_ai_service.py \
  tests/test_advisor_ads.py tests/test_review_regressions.py -q
cd ../barakah-ui
npm test
npm run build
```

Tests use mocked transport and a fake model for local HTTP protocol checks. They cover consent, owner isolation, bounded history, follow-ups, identity/errors, no writes on failures, in-flight mutation/session/consent revalidation, atomic rollback, loopback-service authentication, serialization/busy, and timeout lock release. Real inference and browser verification must be performed separately against the pinned runtime; retain exact configuration/response metadata and runtime versions as evidence without publishing user text or credentials.
