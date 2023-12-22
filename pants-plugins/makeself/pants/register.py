from makeself.pants import system_binaries

from . import makeself
from .goals import package
from .target_types import MakeselfArchiveTarget


def target_types():
    return [MakeselfArchiveTarget]


def rules():
    return [
        *system_binaries.rules(),
        *package.rules(),
        *makeself.rules(),
    ]
