"""envctl package."""

__all__ = ["__version__"]

try:
    from importlib.metadata import version

    __version__ = version("envctl")
except Exception:
    __version__ = "0.0.0-dev"
