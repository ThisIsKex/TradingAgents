---
name: smoke-structured-output
description: Use when running or debugging scripts/smoke_structured_output.py — the three-agent structured-output smoke test. Covers invocation, interpreting PASS/FAIL, and fixing provider-specific failures.
---

# Smoke test: structured output

Run `scripts/smoke_structured_output.py` to verify the three Pydantic decision agents produce clean typed instances + correct markdown with a real LLM provider.

## Usage

```bash
export <API_KEY>=...
python scripts/smoke_structured_output.py <provider>
```

| Provider | API key env var |
|---|---|
| `openai` | `OPENAI_API_KEY` |
| `google` | `GOOGLE_API_KEY` |
| `anthropic` | `ANTHROPIC_API_KEY` |
| `deepseek` | `DEEPSEEK_API_KEY` |
| `qwen` | `DASHSCOPE_API_KEY` |
| `glm` | `ZHIPU_API_KEY` |
| `xai` | `XAI_API_KEY` |

Optional: `--deep-model <id>` and `--quick-model <id>` to override models.

Provider defaults in `PROVIDER_DEFAULTS` (line ~34).

## Pipeline tested

1. **Research Manager** → `ResearchPlan` (5-tier rating)
2. **Trader** → `TraderProposal` (3-tier action + optional entry/stop/sizing)
3. **Portfolio Manager** → `PortfolioDecision` (rating, exec summary, thesis, price target, horizon)
4. **SignalProcessor** → extracts rating from rendered markdown (zero LLM calls)

Script does NOT call `propagate()` — only the three structured-output calls + SignalProcessor.

## Structure checks

Each rendered output must contain specific section headers (checked after generation):

- Research Manager: `**Recommendation**:`
- Trader: `**Action**:` + `FINAL TRANSACTION PROPOSAL:`
- Portfolio Manager: `**Rating**:`, `**Executive Summary**:`, `**Investment Thesis**:`

## Common failures

- **`FAIL  contains '**Recommendation**'`** → provider's structured output isn't rendering headers. Check `capabilities.py` `preferred_structured_method` for this provider. Try `json_schema` for OpenAI/xAI, `response_schema` for Gemini, `function_calling` (no tool_choice) for DeepSeek thinking models.
- **Raw JSON returned** → `render_*` helper in `schemas.py` not called. Trace the agent node to find where `with_structured_output` renders.
- **HTTP 400 / timeout** → try a smaller model via `--quick-model`. DeepSeek thinking models may need `deepseek-chat` instead of `deepseek-reasoner`.
