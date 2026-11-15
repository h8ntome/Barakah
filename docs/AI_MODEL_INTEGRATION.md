# Future AI integration

The current application intentionally has **no connected AI**, mock advice generator or inference transport. `AI_MODE=unavailable` is the only accepted runtime value. Do not set legacy `mock`/`local` modes.

The authoritative contract, privacy boundaries, superseded test rationale and future implementation seam are documented in [audit/AI_INTEGRATION.md](../audit/AI_INTEGRATION.md).

When the separately trained Liquid AI LFM3-1.7B model is ready, a future approved change can implement `backend/app/ai.py`'s typed request/result interface using local hosting or a private inference service. Verify exact checkpoint/tokenizer/chat-template/runtime compatibility with the model team. Add bounded authenticated transport, timeout/cancellation, consent, minimized owned context, safety review, and transactional conversation persistence. Do not infer runtime compatibility or quality from the model name.

No model weights, benchmark artifacts or training code were modified by this application audit.
