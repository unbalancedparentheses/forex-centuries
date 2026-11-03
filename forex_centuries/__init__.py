"""Load forex-centuries datasets as pandas DataFrames.

    >>> import forex_centuries as fc
    >>> fc.list_datasets()
    >>> df = fc.load("fx_yearly")
    >>> df = fc.load("fx_daily", version="data-2026-11-03.38")   # pin a release

Data is downloaded once from the GitHub release assets and cached under
~/.cache/forex-centuries (override with FOREX_CENTURIES_CACHE). Each source
keeps its own license; see DATA_CARD.md in the repository.
"""

from .datasets import DATASETS
from .loader import cache_dir, latest_version, list_datasets, load

__all__ = ["DATASETS", "cache_dir", "latest_version", "list_datasets", "load"]
__version__ = "0.1.0"
