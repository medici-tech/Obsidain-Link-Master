import logging

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
