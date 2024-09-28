from tradingtoolbox.utils.logger import logger, print
from .dev import _dev

__all__ = ["logger", "print"]


def dev():
    _dev()
