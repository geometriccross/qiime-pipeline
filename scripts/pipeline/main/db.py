from scripts.pipeline import support
from .setup import PipelineContext


def command_list(context: PipelineContext) -> list[str]:
    output = context.setting.container_data.output_path.ctn_pos

    assembly = support.Q2CmdAssembly()

    silva_seq, silva_tax = (
        assembly.new_cmd("qiime rescript get-silva-data")
        .add_parameter("p-version", "138.2")
        .add_parameter("target", "SSURef_NR99")
        .add_output("silva-sequences", output / "silva-seqs.qza")
        .add_output("silva-taxonomy", output / "silva-tax.qza")
        .get_outputs()
    )

    silva_read = (
        assembly.new_cmd("qiime feature-classifier extract-reads")
        .add_input("sequences", silva_seq)
        .add_parameter("min-length", "350")
        .add_parameter("max-length", "500")
        .add_parameter("f-primer", "CCTACGGGNGGCWGCAG")
        .add_parameter("r-primer", "GACTACHVGGGTATCTAATCC")
        .add_output("reads", output / "silva-reads.qza")
        .get_outputs()
    )

    result = (
        assembly.new_cmd("qiime feature-classifier fit-classifier-naive-bayes")
        .add_input("reference-reads", silva_read)
        .add_input("reference-taxonomy", silva_tax)
        .add_output("classifier", output / "classifier-silva138.qza")
        .get_outputs()
    )

    assembly.sort_commands()
    return assembly, result
