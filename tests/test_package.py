"""Tests for the forex_centuries loader (no network)."""

import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))
import forex_centuries as fc  # noqa: E402


def test_registry_paths_exist():
    for name, (rel, desc) in fc.DATASETS.items():
        assert (ROOT / "data" / "derived" / rel).exists(), name
        assert desc


def test_load_uses_cache_for_pinned_version(tmp_path, monkeypatch):
    monkeypatch.setenv("FOREX_CENTURIES_CACHE", str(tmp_path))
    df = pd.DataFrame({"year": [2000], "rate_per_usd": [1.5]})
    (tmp_path / "data-2000-01-01").mkdir()
    df.to_parquet(tmp_path / "data-2000-01-01" / "fx_yearly.parquet")

    def no_network(*a, **k):
        raise AssertionError("should not download a cached file")
    monkeypatch.setattr("forex_centuries.loader._get", no_network)

    out = fc.load("fx_yearly", version="data-2000-01-01")
    pd.testing.assert_frame_equal(out, df)


def test_unknown_dataset():
    with pytest.raises(KeyError, match="fx_yearly"):
        fc.load("nope", version="x")


def test_latest_version_falls_back_to_cache_offline(tmp_path, monkeypatch):
    monkeypatch.setenv("FOREX_CENTURIES_CACHE", str(tmp_path))
    (tmp_path / "latest.json").write_text('{"tag": "data-2000-01-01"}')

    def offline(*a, **k):
        raise OSError("offline")
    monkeypatch.setattr("forex_centuries.loader._get", offline)
    assert fc.latest_version(refresh=True) == "data-2000-01-01"


def test_export_parquet_roundtrip(tmp_path):
    sys.path.insert(0, str(ROOT / "scripts"))
    import export_parquet
    export_parquet.main(tmp_path)
    panel = pd.read_parquet(tmp_path / "fx_yearly.parquet")
    assert {"iso3", "flags", "comparable_with_previous"} <= set(panel.columns)
    assert panel["flags"].map(type).eq(str).all()
    corr = pd.read_parquet(tmp_path / "fx_yearly_correlation.parquet")
    assert corr.columns[0] == "country"
