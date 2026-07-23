"""GWResults: simple, beautiful access to gravitational-wave results."""

from . import posterior, search

try:
    from ._version import version as __version__
except ImportError:  # pragma: no cover
    __version__ = "0.0.0+unknown"

__all__ = ["posterior", "search", "__version__"]
