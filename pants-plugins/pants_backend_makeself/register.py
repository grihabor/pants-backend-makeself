from pants_backend_makeself import system_binaries

from . import makeself
from .goals import package, run
from .target_types import MakeselfArchiveTarget


def target_types():
    return [MakeselfArchiveTarget]


def rules():
    return [
        *system_binaries.rules(),
        *package.rules(),
        *run.rules(),
        *makeself.rules(),
    ]
