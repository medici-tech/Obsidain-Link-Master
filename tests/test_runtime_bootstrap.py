import logging

import pytest

from obsidian_auto_linker_enhanced import bootstrap_runtime, runtime_config


def test_bootstrap_runtime_idempotent():
    first = bootstrap_runtime(log_level="DEBUG")
    second = bootstrap_runtime(log_level="INFO")

    assert first is runtime_config
    assert second is runtime_config


def test_bootstrap_runtime_configures_logging():
    bootstrap_runtime(log_level="DEBUG")
    logger = logging.getLogger("obsidian_linker")

    assert logger.handlers, "bootstrap should configure logging handlers"
    assert logger.isEnabledFor(logging.DEBUG)


def test_main_initializes_processing_context(monkeypatch):
    """Main should always have a context available for provider tests."""

    import obsidian_auto_linker_enhanced as linker

    # Avoid side effects during bootstrap
    monkeypatch.setattr(linker, "load_progress", lambda: None)
    monkeypatch.setattr(linker, "load_cache", lambda: None)

    captured = {}

    def fake_call_ollama(prompt, system_prompt="", max_retries=None, track_metrics=True, *, context):
        captured["ollama_context"] = context
        return "ok"

    class StopProcessing(RuntimeError):
        pass

    def fake_call_ai_provider(prompt, system_prompt="", context=None, **_kwargs):
        captured["ai_context"] = context
        raise StopProcessing()

    monkeypatch.setattr(linker, "call_ollama", fake_call_ollama)
    monkeypatch.setattr(linker, "call_ai_provider", fake_call_ai_provider)

    with pytest.raises(StopProcessing):
        linker.main(enable_dashboard=False, dashboard_update_interval=1)

    # Both providers should receive the same initialized context
    assert "ollama_context" in captured
    assert "ai_context" in captured
    assert captured["ollama_context"] is captured["ai_context"]
