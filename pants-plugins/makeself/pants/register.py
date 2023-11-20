from . import makeself
from .goals import package
from .target_types import MakeselfBinaryTarget


def target_types():
    return [MakeselfBinaryTarget]


def rules():
    return [
        *package.rules(),
        *makeself.rules(),
    ]
