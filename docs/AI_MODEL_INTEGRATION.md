# AI integration

The current contract is [opt-in local AI](local-ai.md). Default and public deployment use `AI_MODE=unavailable`; no fake answer or failed send is persisted. Explicit `AI_MODE=http` connects a private authenticated loopback service with saved consent, pinned model identity, bounded conversation history and atomic successful persistence. It never loads financial records for the model or changes them from model text.

[Release evidence](RELEASE_AUDIT.md) separates actual local inference from mocked transport tests and neutral-prompt offline evaluations. The model has observed arithmetic/context and product-suitability failures; no advice-quality, Sharia or safety certification is claimed.

[The earlier unavailable-only report](../audit/AI_INTEGRATION.md) is preserved as historical evidence, not current configuration guidance. No model weights were changed for this integration.
