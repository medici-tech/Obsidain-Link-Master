"""Basic import tests for the enhanced auto-linker module."""

import importlib


def test_obsidian_auto_linker_module_imports():
    """Ensure the module imports cleanly and exposes call_ollama."""
    module = importlib.import_module("obsidian_auto_linker_enhanced")
    assert hasattr(module, "call_ollama")
