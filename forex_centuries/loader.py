"""Download-and-cache loader for forex-centuries release assets."""

import json
import os
import shutil
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

from .datasets import DATASETS

REPO = "unbalancedparentheses/forex-centuries"
_USER_AGENT = "forex-centuries-python"
_LATEST_TTL = 24 * 3600  # re-check the latest release at most once a day


def cache_dir():
    """Directory where downloaded files are cached."""
    base = os.environ.get("FOREX_CENTURIES_CACHE")
    if base:
        return Path(base)
    xdg = os.environ.get("XDG_CACHE_HOME")
    return Path(xdg) / "forex-centuries" if xdg else Path.home() / ".cache" / "forex-centuries"


def list_datasets():
    """Return {name: description} for every available dataset."""
    return {name: desc for name, (_, desc) in DATASETS.items()}


def _get(url, timeout=60):
    req = urllib.request.Request(url, headers={"User-Agent": _USER_AGENT})
    return urllib.request.urlopen(req, timeout=timeout)


def latest_version(refresh=False):
    """Tag of the latest data release (cached for a day; falls back to cache offline)."""
    marker = cache_dir() / "latest.json"
    if not refresh and marker.exists() and time.time() - marker.stat().st_mtime < _LATEST_TTL:
        return json.loads(marker.read_text())["tag"]
    try:
        with _get(f"https://api.github.com/repos/{REPO}/releases/latest", timeout=30) as resp:
            tag = json.load(resp)["tag_name"]
    except Exception:
        if marker.exists():  # offline or rate-limited: use the last known release
            return json.loads(marker.read_text())["tag"]
        raise
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.write_text(json.dumps({"tag": tag}))
    return tag


def _download(url, dest):
    dest.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=dest.parent, suffix=".part")
    try:
        with os.fdopen(fd, "wb") as out, _get(url, timeout=300) as resp:
            shutil.copyfileobj(resp, out)
        os.replace(tmp, dest)
    except BaseException:
        os.unlink(tmp)
        raise


def load(name, version="latest", refresh=False):
    """Load dataset `name` as a pandas DataFrame.

    version: a release tag such as "data-2026-11-03", or "latest".
    refresh: re-download even if the file is cached.
    """
    import pandas as pd

    if name not in DATASETS:
        raise KeyError(f"Unknown dataset {name!r}. Available: {', '.join(sorted(DATASETS))}")
    tag = latest_version(refresh=refresh) if version == "latest" else version
    path = cache_dir() / tag / f"{name}.parquet"
    if refresh or not path.exists():
        url = f"https://github.com/{REPO}/releases/download/{tag}/{name}.parquet"
        try:
            _download(url, path)
        except urllib.error.HTTPError as e:
            if e.code == 404:
                raise LookupError(f"{name}.parquet is not attached to release {tag}") from e
            raise
    return pd.read_parquet(path)
