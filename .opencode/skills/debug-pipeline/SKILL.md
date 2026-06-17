---
name: debug-pipeline
description: Use when debugging a TradingAgents pipeline run — LangGraph streaming quirks, state shape, checkpoint resume, memory log inspection, and signal extraction.
---

# Debugging the pipeline

## Streaming chunks are deltas, not full state

`graph.stream()` yields per-node deltas. Merge them at the end:

```python
trace = []
for chunk in graph.stream(init_state, **args):
    trace.append(chunk)
final_state = {}
for chunk in trace:
    final_state.update(chunk)
```

This is already done by `_run_graph()` in debug mode (`trading_graph.py:348-358`).

## Debug mode

```python
TradingAgentsGraph(debug=True, config=config)
```

Prints `chunk["messages"][-1].pretty_print()` for each chunk. Shows what each agent outputs in sequence.

## Final state shape

Key fields on `final_state`:

| Field | Type | Set by |
|---|---|---|
| `market_report` | str | Market Analyst |
| `sentiment_report` | str | Sentiment Analyst |
| `news_report` | str | News Analyst |
| `fundamentals_report` | str | Fundamentals Analyst |
| `investment_debate_state` | InvestDebateState | Bull/Bear Researchers + Research Manager |
| `investment_plan` | str | Research Manager (rendered) |
| `trader_investment_plan` | str | Trader (rendered) |
| `risk_debate_state` | RiskDebateState | Aggressive/Neutral/Conservative + PM |
| `final_trade_decision` | str | Portfolio Manager (rendered) |

Full shape: `propagation.py:create_initial_state()` and `agent_states.py:AgentState`.

## Signal extraction

`SignalProcessor` (`signal_processing.py`) reads `final_trade_decision` markdown with a heuristic (zero LLM calls). It looks for the `**Rating**:` line to extract Buy/Overweight/Hold/Underweight/Sell.

```python
rating = ta.process_signal(final_state["final_trade_decision"])
```

## Checkpoint resume

Only when `config["checkpoint_enabled"] = True` or `--checkpoint` CLI flag.

- Per-ticker SQLite: `~/.tradingagents/cache/checkpoints/<TICKER>.db`
- Thread ID = `sha256("{TICKER}:{DATE}")[:16]` — same tkr+date resumes, different date starts fresh
- Logs: `Resuming from step N for <TICKER> on <date>` or `Starting fresh`
- Auto-cleared on successful completion
- Reset before run: `--clear-checkpoints`
- Implementation: `checkpointer.py` → `SqliteSaver` context manager

## Memory log

Always-on decision log at `~/.tradingagents/memory/trading_memory.md`.

- Structure: YAML frontmatter + markdown body per entry
- States: `pending` (unresolved) → `resolved` (after next same-ticker run)
- Resolution: fetches realised return + alpha vs benchmark + LLM reflection
- Only Portfolio Manager reads memory context (via `past_context` in state)
- Override path: `TRADINGAGENTS_MEMORY_LOG_PATH`
- Cap resolved entries: `config["memory_log_max_entries"]`

## Common issues

- **Config state leaks between runs**: `DEFAULT_CONFIG` must be `.copy()`'d before mutation. Sub-dicts need deep copy. Fixed in v0.2.5.
- **`backend_url` leaks to wrong provider**: set to `None` (default). Each client uses its own default endpoint. Fixed in v0.2.4.
- **Messages repeat in CLI display**: `_processed_message_ids` set de-dup. Check if message IDs are present.
- **Report section missing**: streaming chunks are deltas; make sure `final_state.update(chunk)` runs for every chunk in `trace`.
