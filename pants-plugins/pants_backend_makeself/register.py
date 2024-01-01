from . import makeself, system_binaries, util_rules
from .goals import package, run
from .target_types import MakeselfArchiveTarget


def target_types():
    return [MakeselfArchiveTarget]


def rules():
    return [
        *makeself.rules(),
        *package.rules(),
        *run.rules(),
        *system_binaries.rules(),
        *util_rules.rules(),
    ]
