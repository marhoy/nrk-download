"""Package initialization."""

import importlib.metadata

__all__ = ["__version__"]
__version__ = importlib.metadata.version(__package__) if __package__ else "unknown"
