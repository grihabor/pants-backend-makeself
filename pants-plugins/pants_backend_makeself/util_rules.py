import logging
from dataclasses import dataclass
from typing import Optional

from pants.core.util_rules.system_binaries import (
    BashBinary,
    BinaryShims,
    BinaryShimsRequest,
    CatBinary,
    MkdirBinary,
    TarBinary,
)
from pants.engine.fs import Digest
from pants.engine.process import Process
from pants.engine.rules import Get, collect_rules, rule
from pants.util.logging import LogLevel
from pants_backend_makeself.system_binaries import (
    AwkBinary,
    Base64Binary,
    BasenameBinary,
    Bzip2Binary,
    CutBinary,
    DateBinary,
    DdBinary,
    DfBinary,
    DirnameBinary,
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
    TailBinary,
    TestBinary,
    WcBinary,
    XzBinary,
    ZstdBinary,
)

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class RunMakeselfArchive:
    exe: str
    input_digest: Digest
    description: str
    level: LogLevel = LogLevel.INFO
    output_directory: Optional[str] = None


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
    rm: RmBinary,
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
                rm,
                sed,
                shasum,
                tail,
                tar,
                test,
                wc,
                xz,
                zstd,
            ),
            rationale="run makeself archive",
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
        argv=argv,
        input_digest=request.input_digest,
        immutable_input_digests=shims.immutable_input_digests,
        output_directories=output_directories,
        description=request.description,
        level=request.level,
        env={"PATH": shims.path_component},
    )


def rules():
    return collect_rules()
