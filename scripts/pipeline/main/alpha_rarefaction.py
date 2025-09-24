#!/usr/bin/env python

from scripts.pipeline import support
from .setup import PipelineContext


def command_list(context: PipelineContext) -> tuple[support.Q2CmdAssembly, str]:
    output = context.setting.container_data.output_path.ctn_pos
    assembly = support.Q2CmdAssembly()
    # fmt: off

    # Import sequences
    imported = assembly.new_cmd("qiime tools import") \
        .add_option("type", "SampleData[PairedEndSequencesWithQuality]") \
        .add_option("input-format", "PairedEndFastqManifestPhred33V2") \
        .add_option("input-path", context.ctn_manifest) \
        .add_option("output-path", output / "paired_end_demux.qza") \
        .get_outputs()

    # Get region settings from the first dataset
    dataset = next(iter(context.setting.datasets.sets))
    region = dataset.region

    denoised_table, denoised_seq, denoised_stats =  \
        assembly.new_cmd("qiime dada2 denoise-paired") \
        .add_option("quiet") \
        .add_input("demultiplexed-seqs", imported) \
        .add_parameter("n-threads", "0") \
        .add_parameter("trim-left-f", str(region.trim_left_f)) \
        .add_parameter("trim-left-r", str(region.trim_left_r)) \
        .add_parameter("trunc-len-f", str(region.trunc_len_f)) \
        .add_parameter("trunc-len-r", str(region.trunc_len_r)) \
        .add_output("table", output / "denoised_table.qza") \
        .add_output("representative-sequences", output / "denoised_seq.qza") \
        .add_output("denoising-stats", output / "denoised_stats.qza") \
        .get_outputs()

    align_seq, masked_align_seq, unrooted_tree, rooted_tree = \
        assembly.new_cmd("qiime phylogeny align-to-tree-mafft-fasttree") \
        .add_option("quiet") \
        .add_input("sequences", denoised_seq) \
        .add_output("alignment", output / "aligned-rep-seqs.qza") \
        .add_output("masked-alignment", output / "masked-aligned-rep-seqs.qza") \
        .add_output("tree", output / "unrooted-tree.qza") \
        .add_output("rooted-tree", output / "rooted-tree.qza") \
        .get_outputs()

    sampling_depth = context.setting.sampling_depth

    # 実行時のエラーを避けるため
    # steps, iterationsはサンプルのmax featureよりも十分に小さくする
    qzv = (
        assembly.new_cmd("qiime diversity alpha-rarefaction")
        .add_option("quiet")
        .add_input("table", denoised_table)
        .add_input("phylogeny", rooted_tree)
        .add_parameter("min-depth", "1")
        .add_parameter("max-depth", sampling_depth)
        .add_parameter("steps", str(2) if sampling_depth < 10 else str(10))
        .add_parameter("iterations", str(1) if sampling_depth < 10 else str(10))
        .add_metadata("metadata-file", str(context.ctn_metadata))
        .add_output("visualization", output / "alpha_rarefaction.qzv")
        .get_outputs()
    )

    # fmt: on

    assembly.sort_commands()
    return assembly, qzv
