---
name: add-llm-provider
description: Use when asked to integrate a new LLM provider into TradingAgents. Covers every touch point: factory, client class, API key env var, model catalog, capabilities, CLI integration, docs, and tests.
---

# Adding an LLM Provider

Eight files to touch, in order:

## 1. API key env var — `tradingagents/llm_clients/api_key_env.py`

Add entry to `PROVIDER_API_KEY_ENV`:

```python
"newprovider": "NEWPROVIDER_API_KEY",
```

Dual-region (Qwen/GLM/MiniMax pattern):
```python
"newprovider":    "NEWPROVIDER_API_KEY",
"newprovider-cn": "NEWPROVIDER_CN_API_KEY",
```

`ollama` = `None` (no key). `bedrock` = `"AWS_PROFILE"`.

## 2. Factory — `tradingagents/llm_clients/factory.py`

Lazy imports only — heavy SDKs must not load at module level.

OpenAI-compatible → add to `_OPENAI_COMPATIBLE` tuple:

```python
_OPENAI_COMPATIBLE = (
    "openai", ..., "newprovider", "newprovider-cn",
)
```

Non-OpenAI-compatible → add branch:

```python
if provider_lower == "newprovider":
    from .newprovider_client import NewProviderClient
    return NewProviderClient(model, base_url, **kwargs)
```

## 3. Client class — `tradingagents/llm_clients/<name>_client.py`

Extend `BaseLLMClient`:

- `__init__`: call `super().__init__`, store `self.provider`
- `get_llm()`: read API key via `os.environ.get(get_api_key_env(self.provider))`, return langchain LLM instance
- `warn_if_unknown_model()` called before returning LLM
- For OpenAI-compatible: subclass `NormalizedChatOpenAI` or the base `OpenAIClient`
- Provider-specific quirks → subclass `NormalizedChatOpenAI` with `_get_request_payload` / `_create_chat_result` overrides (see `DeepSeekChatOpenAI`, `MinimaxChatOpenAI` in `openai_client.py`)
- `_PASSTHROUGH_KWARGS` tuple for forwarding user kwargs

If provider has a base URL, add to `_PROVIDER_BASE_URL` in `openai_client.py`.

## 4. Model catalog — `tradingagents/llm_clients/model_catalog.py`

Define model dict:

```python
_NEWPROVIDER_MODELS: Dict[str, List[ModelOption]] = {
    "quick": [
        ("Label - description", "model-id"),
        ("Custom model ID", "custom"),
    ],
    "deep": [
        ("Label - description", "model-id"),
        ("Custom model ID", "custom"),
    ],
}
```

Add to `MODEL_OPTIONS` dict keyed by provider string. Dual-region providers share the same model list:

```python
"newprovider": _NEWPROVIDER_MODELS,
"newprovider-cn": _NEWPROVIDER_MODELS,
```

Dynamic models (OpenRouter): skip, already handled.

## 5. Capabilities — `tradingagents/llm_clients/capabilities.py`

Only if provider has API quirks (tool_choice rejection, no json_mode, no json_schema).

Define `ModelCapabilities` dataclass, add exact-ID entry to `_BY_ID`, regex pattern to `_BY_PATTERN`.

## 6. CLI integration

- **`cli/utils.py`**: add provider to `select_llm_provider()` dropdown
- **`cli/main.py`**: if dual-region, add `ask_{name}_region()` prompt and wire in `get_user_selections()` (see qwen/minimax/glm pattern)
- Special thinking config (OpenAI reasoning_effort, Anthropic effort, Google thinking_level) → add CLI prompt step in `get_user_selections()`

## 7. `.env.example` — document the API key env var(s)

## 8. `.env.enterprise.example` — only if enterprise (Azure pattern)

## 9. Tests — `tests/`

- Add env var to `_API_KEY_ENV_VARS` in `tests/conftest.py`
- Add entry to coverage test `test_every_select_llm_provider_choice_has_an_entry` in `test_api_key_env.py`
- Add parametrized entry to `test_known_providers_resolve` in `test_api_key_env.py`
