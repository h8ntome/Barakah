# Connecting the fine-tuned model

## What is and is not included

Barakah's default AI is an explicitly labelled **deterministic mock**, not the fine-tuned model. It makes no external inference requests. The LFM3 1.7B checkpoint is being developed separately; neither weights nor benchmark results are changed by this application integration.

The application owns authentication, authorization, conversation persistence, input/history limits, consent and error handling. A provider adapter owns the inference transport. Financial arithmetic belongs to deterministic backend services, not generated text.

## Runtime compatibility gate

Do **not** infer runtime compatibility from the name “LFM3”. Before selecting a runtime, the model team must supply the exact checkpoint/revision, architecture/config, tokenizer and chat template, adapter/base-model relationship, license, supported precision, memory requirements and the runtime/version tested against those artifacts. Compare those with the runtime's published supported architectures and run its official minimal inference example. A successful call to a generic HTTP endpoint does not prove the actual checkpoint loads or performs well.

No claim is made here that Ollama, vLLM, Transformers or a particular accelerator supports the pending checkpoint. If the selected runtime does not implement the configured HTTP contract, implement an adapter rather than changing API routes or browser components. Do not download weights merely to exercise the web application.

## Safe integration checklist

1. Run the model server privately, preferably on loopback or a private network. Do not expose an unauthenticated inference server publicly.
2. Configure the backend's local provider, endpoint, model identifier and finite timeout (see `backend/.env.example`). Keep API credentials on the backend, never in `VITE_*` variables.
3. Run one short non-sensitive question directly against the serving endpoint and verify response shape, model identity and actual model availability.
4. Check `/api/v1/ai/health`. Process liveness is not proof that a model is loaded; perform an authenticated chat smoke test as well.
5. Register an isolated application test account, submit a message through `/api/v1/ai/chat`, then retrieve its stored conversation. Verify provider labeling is no longer mock.
6. Stop the model server and repeat. The application must return a safe unavailable error, preserve the editable draft and never silently fall back to mock text.
7. Verify timeout behavior and a malformed provider response. Review safe operational logs, not private prompts, tokens or full financial context.
8. Rerun the application's AI tests and the browser conversation flow. Model quality/Islamic-finance evaluation is a separate gate owned by `benchmark/` and the model team.

## Privacy and advice boundaries

Only user-requested, minimized aggregate financial context should enter a model request. Raw transactions and other users' data must not be included. External inference requires explicit consent and disclosure; using a local-looking URL does not make a third-party service private. Deployment operators must accurately classify the destination.

Generated text is educational, not a compliance certificate, fatwa, guaranteed return or licensed individualized advice. A model must not fabricate scripture, Hadith, stock data or scholarly consensus. Screening uses the independent deterministic screening service and returns uncertainty for missing evidence.

## Streaming

Streaming is not required for initial integration. Do not enable SSE solely because another model runtime supports it. First verify this exact serving adapter's framing, cancellation, timeout/error behavior and persistence rules. Until implemented and tested, the frontend uses a bounded request with a loading state and one complete response.
