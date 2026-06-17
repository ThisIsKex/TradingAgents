# TradingAgents — repo guide

## Entry points

| Surface | Command / Import |
|---|---|
| CLI | `tradingagents` or `python -m cli.main` |
| Python API | `TradingAgentsGraph` from `tradingagents.graph.trading_graph` |
| Smoke test | `python scripts/smoke_structured_output.py <provider>` (e.g. `openai`, `anthropic`, `deepseek`) |

## Install

```bash
pip install .
# or Docker:
docker compose run --rm tradingagents
docker compose --profile ollama run --rm tradingagents-ollama
```

## Tests

```bash
pytest                           # all (no API keys needed — conftest injects placeholders)
pytest -m unit                   # fast isolated tests only
pytest tests/test_env_overrides.py  # single file
```

Markers: `unit`, `integration`, `smoke` (defined in `pyproject.toml`).

## Key structure

| Directory | Owns |
|---|---|
| `tradingagents/graph/` | LangGraph workflow, nodes, edges, propagation, reflection, signal processing, checkpointing |
| `tradingagents/agents/` | Agent nodes (analysts, researchers, trader, risk, portfolio manager) + Pydantic structured-output schemas |
| `tradingagents/llm_clients/` | Per-provider LLM client implementations + factory + capabilities table + model catalog |
| `tradingagents/dataflows/` | Data vendors: yfinance, Alpha Vantage |
| `cli/` | Interactive CLI with Rich TUI |

## Pipeline order

Market / Sentiment / News / Fundamentals Analysts → Bull/Bear Researchers → Research Manager → Trader → Aggressive/Neutral/Conservative Risk analysts → Portfolio Manager

Selected analysts controlled via `TradingAgentsGraph(selected_analysts=["market", "social", "news", "fundamentals"])`. The `"social"` key maps to `sentiment_analyst` backend (back-compat; `AnalystType.SOCIAL = "social"` preserved).

## LLM providers

`openai`, `google`, `anthropic`, `xai`, `deepseek`, `qwen`, `qwen-cn`, `glm`, `glm-cn`, `minimax`, `minimax-cn`, `openrouter`, `ollama`, `azure`, `bedrock`

Dual-region providers (qwen, glm, minimax) use separate API key env vars per region; CLI prompts for region as secondary step.

`ollama` has no API key. `OLLAMA_BASE_URL` for remote endpoint (default `http://localhost:11434/v1`).

## Config quirks

- `.env` loaded automatically at `tradingagents/__init__.py` import time
- `TRADINGAGENTS_*` env vars override `DEFAULT_CONFIG` at import (type-coerced: string/int/bool). See `tradingagents/default_config.py:_ENV_OVERRIDES` for the full list
- Provider→env-var mapping single source of truth: `tradingagents/llm_clients/api_key_env.py`
- Model catalog (`model_catalog.py`) is single source for CLI model selections. Versioned IDs only; users wanting auto-latest aliases pick "Custom model ID"
- Per-model API quirks in `capabilities.py` (e.g., DeepSeek thinker rejects `tool_choice`, MiniMax M2.x too)
- News fetch configurable via `news_article_limit`, `global_news_article_limit`, `global_news_lookback_days`, `global_news_queries`
- Alpha benchmark auto-resolved by ticker suffix (non-US: `.NS`→^NSEI, `.T`→^N225, etc.). Override with `benchmark_ticker`
- `backend_url` defaults to `None` (each provider client uses its native default); never set a provider-specific URL here — it leaks to other providers
- All file I/O uses explicit `encoding="utf-8"` (Windows compat)
- Ticker values validated for path-traversal safety on all filesystem operations

## Persistence

- **Decision log** — always on. Appends to `~/.tradingagents/memory/trading_memory.md`; override with `TRADINGAGENTS_MEMORY_LOG_PATH`. Resolved entries include realised return + alpha + LLM reflection
- **Checkpoint resume** — opt-in via `--checkpoint`. Per-ticker SQLite DBs at `~/.tradingagents/cache/checkpoints/`; `--clear-checkpoints` to reset. Auto-cleared on success

## Structured output

Three decision agents use Pydantic schemas (`tradingagents/agents/schemas.py`):
- **Research Manager** → `ResearchPlan` (5-tier rating Buy/Overweight/Hold/Underweight/Sell)
- **Trader** → `TraderProposal` (3-tier Buy/Hold/Sell, with optional entry/stop/sizing)
- **Portfolio Manager** → `PortfolioDecision` (5-tier rating, exec summary, thesis, price target, horizon)

Each provider uses its native structured-output mode (json_schema, response_schema, or tool-use). Render helpers convert back to markdown for downstream consumers.

## Agent node files

| Agent | File |
|---|---|
| Market/News/Fundamentals/Sentiment Analysts | `tradingagents/agents/analysts/` |
| Bull/Bear Researchers | `tradingagents/agents/researchers/` |
| Research Manager | `tradingagents/agents/managers/research_manager.py` |
| Trader | `tradingagents/agents/trader/trader.py` |
| Risk analysts | `tradingagents/agents/risk_mgmt/` |
| Portfolio Manager | `tradingagents/agents/managers/portfolio_manager.py` |
| Agent utils/states | `tradingagents/agents/utils/` |
