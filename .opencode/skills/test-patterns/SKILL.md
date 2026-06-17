---
name: test-patterns
description: Use when writing, running, or debugging tests in TradingAgents. Covers conftest fixtures, test markers, mocking patterns, and conventions.
---

# Test patterns

## Running tests

```bash
pytest                           # all (no API keys needed)
pytest -m unit                   # fast isolated tests only
pytest -m integration            # tests requiring external services
pytest -m smoke                  # quick sanity checks
pytest tests/test_env_overrides.py  # single file
```

Markers defined in `pyproject.toml`:

```ini
markers = [
    "unit: fast isolated unit tests",
    "integration: tests requiring external services",
    "smoke: quick sanity-check tests",
]
```

## conftest.py fixtures (`tests/conftest.py`)

Two key fixtures:

1. **`_dummy_api_keys` (autouse)** — sets every known API key env var to `"placeholder"` if absent. All unit tests pass without real credentials. Covers all keys in `_API_KEY_ENV_VARS`.

2. **`mock_lll_client`** — mocks `tradingagents.llm_clients.factory.create_llm_client` with a MagicMock. Use when testing graph/agent setup without LLM calls:

```python
def test_something(mock_llm_client):
    # create_llm_client() now returns a MagicMock
    ...
```

## Two test styles coexist

### pytest function style (preferred for new tests)

Uses `monkeypatch`, `tmp_path`, `@pytest.mark.parametrize`.

```python
def test_something(monkeypatch, tmp_path):
    monkeypatch.setenv("TRADINGAGENTS_LLM_PROVIDER", "google")
    ...
```

### unittest.TestCase style

Used in `test_checkpoint_resume.py`. Works under pytest runner:

```python
class TestFeature(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
    def test_feature(self):
        ...
```

## Key patterns

- **Reload module for env-var tests**: `importlib.reload(module)` after monkeypatching env (see `test_env_overrides.py:_reload_with_env`)
- **Parametrize edge cases**: `@pytest.mark.parametrize` for boolean coercion, string variants, etc.
- **Mock questionary for CLI tests**: `unittest.mock.patch` on `questionary.password`/`questionary.text` (see `test_api_key_env.py`)
- **Test checkpoint state**: build a minimal `StateGraph`, crash a node, verify resume (see `test_checkpoint_resume.py`)
- **Lazy imports in tests**: only import provider SDKs inside the test function, not at module level
