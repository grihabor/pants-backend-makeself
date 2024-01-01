import dataclasses
import logging
import os
from dataclasses import dataclass
from typing import Optional

from makeself.pants.system_binaries import (
    AwkBinary,
    Base64Binary,
    BasenameBinary,
    Bzip2Binary,
    CksumBinary,
    CutBinary,
    DateBinary,
    DdBinary,
    DfBinary,
    DirnameBinary,
    DuBinary,
    ExprBinary,
    FindBinary,
    GpgBinary,
    GzipBinary,
    HeadBinary,
    IdBinary,
    Md5sumBinary,
    PwdBinary,
    RmBinary,
    SedBinary,
    ShBinary,
    SortBinary,
    TailBinary,
    TestBinary,
    TrBinary,
    WcBinary,
    XargsBinary,
    XzBinary,
    ZstdBinary,
)
from pants.core.util_rules import external_tool
from pants.core.util_rules.external_tool import (
    DownloadedExternalTool,
    ExternalToolRequest,
    TemplatedExternalTool,
)
from pants.core.util_rules.system_binaries import (
    BashBinary,
    BinaryShims,
    BinaryShimsRequest,
    CatBinary,
    ChmodBinary,
    MkdirBinary,
    TarBinary,
)
from pants.engine.fs import EMPTY_DIGEST, Digest, RemovePrefix
from pants.engine.platform import Platform
from pants.engine.process import Process, ProcessCacheScope, ProcessResult
from pants.engine.rules import Get, collect_rules, rule
from pants.util.logging import LogLevel

logger = logging.getLogger(__name__)


class MakeselfSubsystem(TemplatedExternalTool):
    options_scope = "makeself"
    help = "A tool to generate a self-extractable compressed tar archives."

    default_version = "2.5.0"
    default_known_versions = [
        "2.5.0|macos_arm64 |4d2fa9d898be22c63bb3c6bb7cc3dc97237700dea6d6ad898dcbec0289df0bc4|45867",
        "2.5.0|macos_x86_64|4d2fa9d898be22c63bb3c6bb7cc3dc97237700dea6d6ad898dcbec0289df0bc4|45867",
        "2.5.0|linux_arm64 |4d2fa9d898be22c63bb3c6bb7cc3dc97237700dea6d6ad898dcbec0289df0bc4|45867",
        "2.5.0|linux_x86_64|4d2fa9d898be22c63bb3c6bb7cc3dc97237700dea6d6ad898dcbec0289df0bc4|45867",
    ]

    default_url_template = "https://github.com/megastep/makeself/releases/download/release-{version}/makeself-{version}.run"


class MakeselfDistribution(DownloadedExternalTool):
    """The makeself distribution.

    You can find releases here: https://github.com/megastep/makeself/releases
    """


@rule(desc="Download makeself distribution", level=LogLevel.DEBUG)
async def download_makeself_distribution(
    options: MakeselfSubsystem,
    platform: Platform,
) -> MakeselfDistribution:
    tool = await Get(
        DownloadedExternalTool,
        ExternalToolRequest,
        options.get_request(platform),
    )
    logger.debug("makeself external tool: %s", tool)
    return MakeselfDistribution(digest=tool.digest, exe=tool.exe)


class MakeselfTool(DownloadedExternalTool):
    """The Makeself tool."""


@dataclass(frozen=True)
class RunMakeselfArchive:
    exe: str
    input_digest: Digest
    description: str
    level: LogLevel = LogLevel.INFO
    output_directory: Optional[str] = None


@dataclass(frozen=True)
class RunMakeselfArthiveProcess(Process):
    pass


@rule(desc="Run makeself archive", level=LogLevel.DEBUG)
async def run_makeself_archive(
    request: RunMakeselfArchive,
    awk: AwkBinary,
    base64: Base64Binary,
    basename: BasenameBinary,
    bash: BashBinary,
    bzip2: Bzip2Binary,
    cat: CatBinary,
    cut: CutBinary,
    dd: DdBinary,
    df: DfBinary,
    dirname: DirnameBinary,
    expr: ExprBinary,
    find: FindBinary,
    gpg: GpgBinary,
    gzip: GzipBinary,
    head: HeadBinary,
    id: IdBinary,
    md5sum: Md5sumBinary,
    mkdir: MkdirBinary,
    pwd: PwdBinary,
    sed: SedBinary,
    shasum: DateBinary,
    tail: TailBinary,
    tar: TarBinary,
    test: TestBinary,
    wc: WcBinary,
    xz: XzBinary,
    zstd: ZstdBinary,
) -> Process:
    shims = await Get(
        BinaryShims,
        BinaryShimsRequest(
            paths=(
                awk,
                base64,
                basename,
                bash,
                bzip2,
                cat,
                cut,
                dd,
                df,
                dirname,
                expr,
                find,
                gpg,
                gzip,
                head,
                id,
                md5sum,
                mkdir,
                pwd,
                sed,
                shasum,
                tail,
                tar,
                test,
                wc,
                xz,
                zstd,
            ),
            rationale="extract makeself archive",
        ),
    )
    output_directories = []
    argv = [
        request.exe,
        "--accept",
        "--noprogress",
        "--nox11",
        "--nochown",
        "--nodiskspace",
        "--quiet",
    ]

    if output_directory := request.output_directory:
        output_directories = [output_directory]
        argv.extend(["--keep", "--target", request.output_directory])

    return Process(
        argv=[bash.path] + argv,
        input_digest=request.input_digest,
        immutable_input_digests=shims.immutable_input_digests,
        output_directories=output_directories,
        description=request.description,
        level=request.level,
        env={"PATH": shims.path_component},
    )


@rule(desc="Extract makeself distribution", level=LogLevel.DEBUG)
async def extract_makeself_distribution(
    dist: MakeselfDistribution,
) -> MakeselfTool:
    out = "__makeself"
    result = await Get(
        ProcessResult,
        RunMakeselfArchive(
            exe=dist.exe,
            input_digest=dist.digest,
            output_directory=out,
            description=f"Extracting Makeself archive: {out}",
            level=LogLevel.DEBUG,
        ),
    )
    digest = await Get(Digest, RemovePrefix(result.output_digest, out))
    return MakeselfTool(digest=digest, exe="makeself.sh")


@dataclass(frozen=True)
class MakeselfProcess:
    archive_dir: str
    file_name: str
    label: str
    startup_script: str
    input_digest: Digest
    description: str = dataclasses.field(compare=False)
    level: LogLevel
    cache_scope: Optional[ProcessCacheScope]
    timeout_seconds: Optional[int]
    output_filename: str

    @classmethod
    def new(
        cls,
        *,
        archive_dir: str,
        file_name: str,
        label: str,
        startup_script: str,
        description: str,
        output_filename: str,
        input_digest: Digest = EMPTY_DIGEST,
        level: LogLevel = LogLevel.INFO,
        cache_scope: Optional[ProcessCacheScope] = None,
        timeout_seconds: Optional[int] = None,
    ):
        return MakeselfProcess(
            archive_dir=archive_dir,
            file_name=file_name,
            label=label,
            startup_script=startup_script,
            input_digest=input_digest,
            description=description,
            level=level,
            output_filename=output_filename,
            cache_scope=cache_scope,
            timeout_seconds=timeout_seconds,
        )


@rule
async def create_makeself_archive(
    request: MakeselfProcess,
    makeself: MakeselfTool,
    awk: AwkBinary,
    basename: BasenameBinary,
    bash: BashBinary,
    cat: CatBinary,
    date: DateBinary,
    dirname: DirnameBinary,
    du: DuBinary,
    expr: ExprBinary,
    find: FindBinary,
    gzip: GzipBinary,
    rm: RmBinary,
    sed: SedBinary,
    sh: ShBinary,
    sort: SortBinary,
    tar: TarBinary,
    wc: WcBinary,
    xargs: XargsBinary,
    tr: TrBinary,
    cksum: CksumBinary,
    cut: CutBinary,
    chmod: ChmodBinary,
) -> Process:
    shims = await Get(
        BinaryShims,
        BinaryShimsRequest(
            paths=(
                awk,
                basename,
                cat,
                date,
                dirname,
                du,
                expr,
                find,
                gzip,
                rm,
                sed,
                sh,
                sort,
                tar,
                wc,
                tr,
                cksum,
                cut,
                chmod,
                xargs,
            ),
            rationale="create makeself archive",
        ),
    )
    tooldir = "__makeself"
    argv = (
        os.path.join(tooldir, makeself.exe),
        request.archive_dir,
        request.file_name,
        request.label,
        os.path.join(os.curdir, request.startup_script),
    )
    process = Process(
        argv,
        input_digest=request.input_digest,
        immutable_input_digests={
            tooldir: makeself.digest,
            **shims.immutable_input_digests,
        },
        env={"PATH": shims.path_component},
        description=request.description,
        level=request.level,
        append_only_caches={},
        output_files=(request.output_filename,),
        cache_scope=request.cache_scope or ProcessCacheScope.SUCCESSFUL,
        timeout_seconds=request.timeout_seconds,
    )
    return process


def rules():
    return [
        *collect_rules(),
        *external_tool.rules(),
    ]
