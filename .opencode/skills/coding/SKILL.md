---
name: coding
description: Use when writing or modifying Python code in TradingAgents. Covers project conventions, style, and patterns.
---

# Coding conventions

## Python style

- Target Python 3.10+ (`requires-python = ">=3.10"`)
- Use modern type annotations: `str | None`, `list[str]` (no `Optional`, no `List` in new code)
- `from __future__ import annotations` at top of new files for deferred eval
- Explicit `encoding="utf-8"` on all `open()` calls (Windows compat)
- Lazy imports for heavy SDKs — import inside the function, not at module level

## LangGraph patterns

- State: `TypedDict` with `Annotated` fields (see `agent_states.py`). Extends `MessagesState`.
- Nodes: plain functions returning a dict (`{"field_name": new_value}`). The dict is merged into state.
- Conditional edges: `ConditionalLogic` class with methods returning the next node name.
- Workflow: `StateGraph(AgentState)`, `add_node`, `add_edge`, `add_conditional_edges`, compile.

## Pydantic schemas

- `BaseModel` with `Field(description=...)` for structured output
- Field descriptions double as the model's output instructions
- `render_*` helper function converts instance back to markdown (see `schemas.py`)
- Shared enums: `PortfolioRating` (5-tier), `TraderAction` (3-tier)

## LLM client pattern

- Extend `BaseLLMClient`, implement `get_llm()` and `validate_model()`
- OpenAI-compatible: go through `_OPENAI_COMPATIBLE` in `factory.py`
- Quirks in `capabilities.py` as `ModelCapabilities` dataclass (not in client code)
- Provider-specific base URLs in `_PROVIDER_BASE_URL` dict in `openai_client.py`
- `NormalizedChatOpenAI` normalizes content to string (handles `[{"type":"text",...}, {"type":"reasoning",...}]`)

## Config

- `DEFAULT_CONFIG` is a plain dict, defined in `default_config.py`
- **Always `.copy()` before mutating** — sub-dicts still shared, beware
- `TRADINGAGENTS_*` env vars override at import via `_apply_env_overrides()` (type-coerced: string/int/bool)
- `backend_url` must stay `None` in defaults — each provider uses its own default endpoint
- `set_config()` syncs the config dict to `dataflows/config.py` module var

## Data vendor pattern

- `dataflows/interface.py` defines the abstract interface
- `y_finance.py` and `alpha_vantage*.py` implement it
- `dataflows/config.py:set_config()` propagates the config to vendor selection
- `tool_vendors` in config overrides `data_vendors` at tool level

## File I/O safety

- `safe_ticker_component()` validates ticker values at every filesystem boundary
- All paths under `~/.tradingagents/` — never outside
- Results in `~/.tradingagents/logs/`, cache in `~/.tradingagents/cache/`

## Do NOT

- Add comments for the sake of comments
- Include `if __name__ == "__main__":` in library code (only in `scripts/`)
- Hardcode provider URLs in config
- Put API keys in source code
- Use `Optional[X]` in new code — prefer `X | None`
