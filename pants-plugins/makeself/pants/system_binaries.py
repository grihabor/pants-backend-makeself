from pants.core.util_rules.system_binaries import (SEARCH_PATHS, BinaryPath,
                                                   BinaryPathRequest,
                                                   BinaryPaths)
from pants.engine.rules import Get, collect_rules, rule
from pants.util.logging import LogLevel


class DirnameBinary(BinaryPath):
    pass


class IdBinary(BinaryPath):
    pass


class AwkBinary(BinaryPath):
    pass


class BasenameBinary(BinaryPath):
    pass


class CutBinary(BinaryPath):
    pass


class DfBinary(BinaryPath):
    pass


class ExprBinary(BinaryPath):
    pass


class GzipBinary(BinaryPath):
    pass


class HeadBinary(BinaryPath):
    pass


class SedBinary(BinaryPath):
    pass


class TailBinary(BinaryPath):
    pass


class WcBinary(BinaryPath):
    pass


class FindBinary(BinaryPath):
    pass


class Md5sumBinary(BinaryPath):
    pass


@rule(desc="Finding the `dirname` binary", level=LogLevel.DEBUG)
async def find_dirname() -> DirnameBinary:
    request = BinaryPathRequest(binary_name="dirname", search_path=SEARCH_PATHS)
    paths = await Get(BinaryPaths, BinaryPathRequest, request)
    first_path = paths.first_path_or_raise(request, rationale="dirname file")
    return DirnameBinary(first_path.path, first_path.fingerprint)


@rule(desc="Finding the `id` binary", level=LogLevel.DEBUG)
async def find_id() -> IdBinary:
    request = BinaryPathRequest(binary_name="id", search_path=SEARCH_PATHS)
    paths = await Get(BinaryPaths, BinaryPathRequest, request)
    first_path = paths.first_path_or_raise(request, rationale="id file")
    return IdBinary(first_path.path, first_path.fingerprint)


@rule(desc="Finding the `awk` binary", level=LogLevel.DEBUG)
async def find_awk() -> AwkBinary:
    request = BinaryPathRequest(binary_name="awk", search_path=SEARCH_PATHS)
    paths = await Get(BinaryPaths, BinaryPathRequest, request)
    first_path = paths.first_path_or_raise(request, rationale="awk file")
    return AwkBinary(first_path.path, first_path.fingerprint)


@rule(desc="Finding the `basename` binary", level=LogLevel.DEBUG)
async def find_basename() -> BasenameBinary:
    request = BinaryPathRequest(binary_name="basename", search_path=SEARCH_PATHS)
    paths = await Get(BinaryPaths, BinaryPathRequest, request)
    first_path = paths.first_path_or_raise(request, rationale="basename file")
    return BasenameBinary(first_path.path, first_path.fingerprint)


@rule(desc="Finding the `cut` binary", level=LogLevel.DEBUG)
async def find_cut() -> CutBinary:
    request = BinaryPathRequest(binary_name="cut", search_path=SEARCH_PATHS)
    paths = await Get(BinaryPaths, BinaryPathRequest, request)
    first_path = paths.first_path_or_raise(request, rationale="cut file")
    return CutBinary(first_path.path, first_path.fingerprint)


@rule(desc="Finding the `df` binary", level=LogLevel.DEBUG)
async def find_df() -> DfBinary:
    request = BinaryPathRequest(binary_name="df", search_path=SEARCH_PATHS)
    paths = await Get(BinaryPaths, BinaryPathRequest, request)
    first_path = paths.first_path_or_raise(request, rationale="df file")
    return DfBinary(first_path.path, first_path.fingerprint)


@rule(desc="Finding the `expr` binary", level=LogLevel.DEBUG)
async def find_expr() -> ExprBinary:
    request = BinaryPathRequest(binary_name="expr", search_path=SEARCH_PATHS)
    paths = await Get(BinaryPaths, BinaryPathRequest, request)
    first_path = paths.first_path_or_raise(request, rationale="expr file")
    return ExprBinary(first_path.path, first_path.fingerprint)


@rule(desc="Finding the `gzip` binary", level=LogLevel.DEBUG)
async def find_gzip() -> GzipBinary:
    request = BinaryPathRequest(binary_name="gzip", search_path=SEARCH_PATHS)
    paths = await Get(BinaryPaths, BinaryPathRequest, request)
    first_path = paths.first_path_or_raise(request, rationale="gzip file")
    return GzipBinary(first_path.path, first_path.fingerprint)


@rule(desc="Finding the `head` binary", level=LogLevel.DEBUG)
async def find_head() -> HeadBinary:
    request = BinaryPathRequest(binary_name="head", search_path=SEARCH_PATHS)
    paths = await Get(BinaryPaths, BinaryPathRequest, request)
    first_path = paths.first_path_or_raise(request, rationale="head file")
    return HeadBinary(first_path.path, first_path.fingerprint)


@rule(desc="Finding the `sed` binary", level=LogLevel.DEBUG)
async def find_sed() -> SedBinary:
    request = BinaryPathRequest(binary_name="sed", search_path=SEARCH_PATHS)
    paths = await Get(BinaryPaths, BinaryPathRequest, request)
    first_path = paths.first_path_or_raise(request, rationale="sed file")
    return SedBinary(first_path.path, first_path.fingerprint)


@rule(desc="Finding the `tail` binary", level=LogLevel.DEBUG)
async def find_tail() -> TailBinary:
    request = BinaryPathRequest(binary_name="tail", search_path=SEARCH_PATHS)
    paths = await Get(BinaryPaths, BinaryPathRequest, request)
    first_path = paths.first_path_or_raise(request, rationale="tail file")
    return TailBinary(first_path.path, first_path.fingerprint)


@rule(desc="Finding the `wc` binary", level=LogLevel.DEBUG)
async def find_wc() -> WcBinary:
    request = BinaryPathRequest(binary_name="wc", search_path=SEARCH_PATHS)
    paths = await Get(BinaryPaths, BinaryPathRequest, request)
    first_path = paths.first_path_or_raise(request, rationale="wc file")
    return WcBinary(first_path.path, first_path.fingerprint)


@rule(desc="Finding the `find` binary", level=LogLevel.DEBUG)
async def find_find() -> FindBinary:
    request = BinaryPathRequest(binary_name="find", search_path=SEARCH_PATHS)
    paths = await Get(BinaryPaths, BinaryPathRequest, request)
    first_path = paths.first_path_or_raise(request, rationale="find file")
    return FindBinary(first_path.path, first_path.fingerprint)


@rule(desc="Finding the `md5sum` binary", level=LogLevel.DEBUG)
async def find_md5sum() -> Md5sumBinary:
    request = BinaryPathRequest(binary_name="md5sum", search_path=SEARCH_PATHS)
    paths = await Get(BinaryPaths, BinaryPathRequest, request)
    first_path = paths.first_path_or_raise(request, rationale="md5sum file")
    return Md5sumBinary(first_path.path, first_path.fingerprint)


def rules():
    return collect_rules()
