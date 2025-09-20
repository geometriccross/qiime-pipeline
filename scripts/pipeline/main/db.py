from pathlib import Path
from scripts.pipeline import support
from scripts.data.store import PairPath
from .setup import PipelineContext
from .util import copy_from_container


def command_list(context: PipelineContext) -> list[str]:
    workspace = context.setting.container_data.workspace_path

    lib_fresh = ["bash", "-c", "apt update && apt upgrade -y"]
    mkdir = ["mkdir", "-p", str(workspace)]

    download = (
        support.Q2CmdAssembly("qiime rescript get-silva-data")
        .add_parameter("p-version", "138.2")
        .add_parameter("target", "SSURef_NR99")
        .add_output("silva-sequences", (seqs := str(workspace / "silva-seqs.qza")))
        .add_output("silva-taxonomy", (tax := str(workspace / "silva-tax.qza")))
    )

    extract_reads = (
        support.Q2CmdAssembly("qiime feature-classifier extract-reads")
        .add_input("sequences", seqs)
        .add_parameter("min-length", "350")
        .add_parameter("max-length", "500")
        .add_parameter("f-primer", "CCTACGGGNGGCWGCAG")
        .add_parameter("r-primer", "GACTACHVGGGTATCTAATCC")
        .add_output("reads", (reads := str(workspace / "silva-reads.qza")))
    )

    train = (
        support.Q2CmdAssembly("qiime feature-classifier fit-classifier-naive-bayes")
        .add_input("reference-reads", reads)
        .add_input("reference-taxonomy", tax)
        .add_output("classifier", str(workspace / "classifier-silva138.qza"))
    )

    return [lib_fresh, mkdir, download.build(), extract_reads.build(), train.build()]


def run_setup_database(context: PipelineContext) -> str:
    for cmd in command_list(context):
        print(cmd)
        output, error = context.executor.run(cmd)
        if error:
            raise RuntimeError(f"データベースのセットアップに失敗しました: {error}")

    return str(
        (context.setting.container_data.workspace_path / "classifier-silva138.qza")
    )


def execute(context: PipelineContext) -> PairPath:
    ctn_db_file = run_setup_database(context)
    local_file = copy_from_container(context, Path(ctn_db_file))
    return PairPath(local_pos=local_file, container_pos=ctn_db_file)
