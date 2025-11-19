from copy import deepcopy
from pathlib import Path
from typing import Dict

from freezegun import freeze_time

import obsidian_auto_linker_enhanced as linker


def _build_analytics(sample: Dict[str, object]) -> Dict[str, object]:
    analytics = deepcopy(sample)
    analytics["start_time"] = linker.datetime(2024, 1, 1, 10, 0, 0)
    analytics["end_time"] = linker.datetime(2024, 1, 1, 11, 0, 0)
    return analytics


def test_generate_analytics_report_snapshot(tmp_path: Path, sample_analytics: Dict[str, object], monkeypatch):
    fixed_time = "2024-01-01 12:00:00"
    analytics = _build_analytics(sample_analytics)

    monkeypatch.setattr(linker, "analytics", analytics)
    monkeypatch.setattr(linker, "ANALYTICS_ENABLED", True)

    frozen_datetime = freeze_time(fixed_time)
    frozen_datetime.start()

    monkeypatch.setattr(linker, "config", {"analytics_file": str(tmp_path / "analytics.json"), "generate_report": True})
    monkeypatch.chdir(tmp_path)

    try:
        linker.generate_analytics_report()
    finally:
        frozen_datetime.stop()

    report_path = tmp_path / "analytics_report.html"
    assert report_path.exists()

    snapshot_path = Path(__file__).parent / "snapshots" / "analytics_report.html"
    assert snapshot_path.exists(), "Snapshot missing; regenerate with known-good analytics output"

    assert report_path.read_text().strip() == snapshot_path.read_text().strip()

    analytics_file = tmp_path / "analytics.json"
    assert analytics_file.exists()
    assert analytics_file.read_text().strip(), "Analytics JSON should not be empty"
