# AI integration: unavailable-only contract

> Historical pre-opt-in snapshot. See [current release audit](../docs/RELEASE_AUDIT.md) and [local AI setup](../docs/local-ai.md). The public demo still has unavailable AI; local opt-in now has separate real inference evidence. Historical results below are preserved, not overwritten.

## Current behavior

No AI is connected. No model is downloaded, loaded, trained or invoked, and no
local or external inference HTTP request (including health probes) is made.
`backend/app/ai.py` contains only typed request/result values and an unavailable
implementation. The mock advice generator, local HTTP adapter, prompt, generated
arithmetic/disclaimer assembly and provider-selection paths have been removed.

`AI_MODE=unavailable` is the only accepted setting, in development, test and
production. `mock`, `local`, and other values fail configuration validation at
startup. Both `backend/.env.example` and Docker Compose use `unavailable`;
`scripts/start-local.sh` already did so. Obsolete AI model-name, URL, timeout and
conversation-generation-limit settings are removed. Old extra environment values
are ignored by the existing settings policy; they cannot activate inference.
The demo seeding script no longer opts users into AI or sends a fake chat message.

## HTTP and service interface

Existing `/api/v1` routes remain authenticated:

- `GET /ai/health`: `{provider: "unavailable", status: "unavailable", is_demo: false}`.
- `GET /advisor/context`: unavailable status, a clearly identified service notice,
  and example questions, not generated answers.
- `POST /advisor/messages`: retains input `{text, conversation_id?,
  include_financial_context?}`. `text` remains trimmed, nonblank and at most 1,000
  characters; a supplied conversation ID must be a valid UUID owned by the user.
  For a valid authorized request, returns HTTP **503**, not a successful reply:

  ```json
  {
    "conversation_id": null,
    "response": null,
    "error": {
      "code": "ai_unavailable",
      "message": "The AI assistant is not connected yet. No message was saved. Your other financial tools remain available."
    }
  }
  ```

  The conversation ID is echoed only when an existing owned conversation was
  supplied; no new ID is allocated. Request text/history is never echoed.
  Authentication (401), validation (422), ownership (404), and per-user rate
  limiting (429) still apply before this response. Consent is **not** required
  merely to report unavailability. Failed sends count toward the existing rate
  limit. Neither a conversation nor user/assistant messages are inserted.
  `include_financial_context` is retained for compatibility but is inert: no
  dashboard totals or private history are loaded for an unavailable request.
- `GET /advisor/conversations`, `GET /advisor/conversations/{id}/messages`, and
  `DELETE /advisor/conversations/{id}` retain pagination, ownership checks,
  message order, and deletion/cascade behavior. These endpoints expose only
  already-stored history. There is no migration or destructive history purge.

Internal boundary: `AIRequest(message, conversation_id, history)` uses typed
`AIMessage(role, text)` history entries. `send_message` returns
`AIResult(conversation_id, response, error)`, currently always a null response and
`AIError(code="ai_unavailable", message=...)`. This small interface preserves a
future integration seam, not an enabled provider or a configurable plug-in.
The current route intentionally does not hydrate private history. A future AI
integration requires a separately approved implementation and renewed review of
consent, privacy, history/context limits, safety, transport and persistence.

## Chat UI

The existing screen layout, components and visual design are preserved. A notice
is visible before context/history requests finish. The composer and suggestion
buttons are usable without AI consent; submit checks availability and displays
an explicit unavailable error. No optimistic message bubbles or phantom history
are added. The draft is retained on failure, controls unlock for retry, and
loading, empty, context/history error and retry states remain available. Financial
context opt-in is removed because no context is sent to an AI. Drafts live only
in component state and are not promised to survive a reload.

Legacy conversations remain selectable/readable/deletable. A historical-only
notice and historical demonstration/model labels distinguish them from current
service status. Example questions are explicitly labeled as examples for an AI
that is not connected. Chat recognizes `error.code === "ai_unavailable"` and displays safe AI-specific
copy instead of suggesting the whole financial application is offline. Settings
also labels the saved advisor consent preference as inactive; it cannot enable
replies or connect a model. The parent separately owns shared HTTP error handling.

## Superseded tests and retained protections

Tests were changed because generating advice is no longer a supported contract,
not to suppress failing assertions:

| Former contract | Replacement coverage |
| --- | --- |
| Consent enables deterministic mock advice and persists a question/reply | `test_unavailable_send_never_persists_with_or_without_consent`: identical 503 contract with consent on/off, no conversation/message rows |
| Mock-generated history supplies ownership/revocation/delete fixtures | `historical_conversation` fixture seeds explicitly historical records; `test_historical_history_ownership_revocation_delete` checks read pagination/order, cross-user read/send/delete rejection, unchanged history after failed sends, consent revocation and cascades |
| Local HTTP provider success, oversized/failing response rollback | No transport exists; unavailable sends cannot write anything, and `test_unavailable_health_and_send_never_open_provider_transport` forbids creating an HTTP client, even under an in-process legacy mode override |
| Provider selection and generated-conversation size bound | Invalid connected/mock modes are rejected; typed message/history input returns only an unavailable result. There is no growing conversation to bound |
| Financial context is opt-in and owner-only in generated prompts | `test_unavailable_never_loads_financial_context` forbids dashboard access with the flag both true and false |
| Slow-drip inference response has a total deadline | Removed inference transport cannot hang or emit advice; health/send transport-denial test also verifies ordinary financial tools remain available |
| PostgreSQL driver rejects NUL in a saved prompt without leaking it | `test_unavailable_prompt_never_reaches_database_or_logs` captures SQL and verifies no prompt binding, INSERT, response echo or log leak, on every database backend rather than skipping SQLite |
| Account deletion cascades through generated history | Existing password/account/session cascade test now seeds legacy history directly, preserving meaningful cascade assertions |
| Local URL validation prevents remote inference | All connected/mock modes now fail configuration; no URL is consumed by runtime AI code |
| Chat previously disabled input/send without consent | New `Chat.test.js` renders the actual screen without consent and verifies usable input, visible unavailability and loading/empty states; source assertions cover send conditions, suggestions and draft/history/error handling |

Input validation, per-user advisor rate limiting, endpoint authentication, account
ownership and all non-AI tests remain covered. The unrelated legacy frontend mock
adapter regression suite remains intact and test-only; production service
selection tests verify it is not imported by the production UI.

## Validation

From the isolated worktree (shared dependencies, no installs):

- `cd backend && /Users/hadi/Documents/Barakah/backend/.venv/bin/python -m pytest -q`:
  **82 passed**; one pre-existing Starlette/httpx deprecation warning.
- `cd barakah-ui && npm test`: **58 passed**, including new Chat server-render,
  source-contract and unavailable-envelope tests.
- `cd barakah-ui && npm run build`: passed.
- `git diff --check`: passed.

The parent owns browser-journey updates; no e2e files are changed here. The full
interactive journey and PostgreSQL parity run were not executed in this workstream. SSR verifies the
initial notice/input state; source assertions complement it for historical labels,
error/draft handling and enabled send conditions, but are not a browser interaction
substitute. No model/inference or external AI API was used during validation.

This document supersedes older mock/local-provider runtime descriptions. Broader
README/API-documentation reconciliation is owned by the parent integration pass.
