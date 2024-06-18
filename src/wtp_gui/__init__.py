"""welltespy GUI."""

from . import core
from .core import gui

try:
    from ._version import __version__
except ModuleNotFoundError:  # pragma: no cover
    # package is not installed
    __version__ = "0.0.0.dev0"

__all__ = ["core", "gui"]
