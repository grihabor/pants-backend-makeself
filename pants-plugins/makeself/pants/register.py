from makeself.pants import system_binaries

from . import makeself
from .goals import package
from .target_types import MakeselfBinaryTarget


def target_types():
    return [MakeselfBinaryTarget]


def rules():
    return [
        *system_binaries.rules(),
        *package.rules(),
        *makeself.rules(),
    ]
