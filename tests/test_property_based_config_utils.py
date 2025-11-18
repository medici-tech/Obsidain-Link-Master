from pathlib import Path

import hypothesis.strategies as st
from hypothesis import HealthCheck, given, settings

from config_utils import ensure_directory_exists, load_json_file, save_json_file


json_scalars = st.booleans() | st.integers() | st.floats(allow_nan=False) | st.text()
json_data_strategy = st.recursive(
    json_scalars,
    lambda children: st.lists(children, max_size=5) | st.dictionaries(st.text(min_size=1, max_size=8), children, max_size=5),
    max_leaves=20,
)


@settings(max_examples=25, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(json_data_strategy)
def test_save_and_load_json_round_trip(tmp_path: Path, payload):
    target_file = tmp_path / "data" / "sample.json"

    assert save_json_file(str(target_file), payload, create_backup=False)

    loaded = load_json_file(str(target_file), default=None)
    assert loaded == payload

    assert save_json_file(str(target_file), payload, create_backup=True)

    backup_file = target_file.with_suffix(".json.backup")
    assert backup_file.exists()
    assert load_json_file(str(backup_file), default=None) == payload


safe_path_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-"


@settings(max_examples=20, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(st.lists(st.text(alphabet=safe_path_chars, min_size=1, max_size=12), min_size=1, max_size=3))
def test_ensure_directory_exists_creates_nested_dirs(tmp_path: Path, path_parts):
    nested_dir = tmp_path.joinpath(*path_parts)

    assert ensure_directory_exists(str(nested_dir), create=True)
    assert nested_dir.exists()
    assert nested_dir.is_dir()

    assert ensure_directory_exists(str(nested_dir), create=False)
