# Environment Configuration

| Variable | Purpose | Required | Example |
| :--- | :--- | :--- | :--- |
| **APP_ENV** | Runtime environment (local, dev, prod) | Yes | `local` |
| **LLM_PROVIDER** | AI model provider (openai, anthropic, ollama) | Yes | `openai` |
| **LLM_MODEL** | Specific model variant | Yes | `gpt-4o-mini` |
| **LLM_API_KEY** | Provider authentication key | No (if mocked) | `sk-...` |
| **GRAPH_RUNTIME_URL**| URL of the LangGraph runtime service | Yes | `http://localhost:8001`|
| **CHECKPOINT_STORE_URL**| Postgres URL for workflow persistence | Yes | `postgresql://...` |
| **AUTH_MODE** | Authentication level (local-dev, oauth2) | Yes | `local-dev` |
| **ENABLE_MOCK_SERVICES**| Use stubs for external systems | Yes | `true` |

## Setup
1. Copy `.env.example` to `.env`.
2. Fill in the `LLM_API_KEY` if using a live provider.
3. Ensure service URLs match your local deployment ports.
