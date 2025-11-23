"""
Tests for the refactored PipelineContext implementation.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock
from dataclasses import dataclass

from qiime_pipeline.pipeline.support.context import (
    PipelineContext,
    PipelineContextBuilder,
    ContainerPaths,
    ExecutionConfig,
)
from qiime_pipeline.pipeline.support import PipelineType
from qiime_pipeline.data.store import (
    SettingData,
    ContainerData,
    Datasets,
    Dataset,
    PairPath,
)
from qiime_pipeline.data.store.ribosome_regions import Region


@pytest.fixture
def mock_executor():
    """モックのエグゼキューターを作成"""
    executor = Mock()
    executor.run = Mock(return_value="success")
    executor.stop = Mock()
    return executor


@pytest.fixture
def sample_region():
    """サンプルのリージョン設定"""
    return Region(
        name="V3V4",
        trim_left_f=0,
        trim_left_r=0,
        trunc_len_f=250,
        trunc_len_r=250,
    )


@pytest.fixture
def sample_dataset(tmp_path, sample_region):
    """サンプルのデータセット"""
    # テスト用のファイルを作成
    fastq_dir = tmp_path / "fastq"
    fastq_dir.mkdir()
    (fastq_dir / "sample_R1.fastq").write_text("test")
    (fastq_dir / "sample_R2.fastq").write_text("test")

    metadata_file = tmp_path / "metadata.csv"
    metadata_file.write_text("sample-id,condition\nsample1,control\n")

    return Dataset(
        name="test_dataset",
        fastq_folder=fastq_dir,
        metadata_path=metadata_file,
        region=sample_region,
    )


@pytest.fixture
def sample_setting(tmp_path, sample_dataset):
    """サンプルの設定データ"""
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    db_file = tmp_path / "db" / "classifier.qza"
    db_file.parent.mkdir()
    db_file.write_text("mock db")

    container_data = ContainerData(
        image_or_dockerfile="quay.io/qiime2/core:latest",
        workspace_path=Path("/workspace"),
        output_path=PairPath(
            local_pos=output_dir, ctn_pos=Path("/workspace/out")
        ),
        database_path=PairPath(
            local_pos=db_file, ctn_pos=Path("/workspace/db/classifier.qza")
        ),
    )

    return SettingData(
        container_data=container_data,
        datasets=Datasets(sets={sample_dataset}),
        sampling_depth=10000,
        batch_id="test-batch-123",
    )


class TestContainerPaths:
    """ContainerPathsクラスのテスト"""

    def test_create_container_paths(self):
        """ContainerPathsの作成テスト"""
        paths = ContainerPaths(
            metadata=Path("/workspace/metadata.tsv"),
            manifest=Path("/workspace/manifest.tsv"),
            output=Path("/workspace/out"),
            workspace=Path("/workspace"),
        )

        assert paths.metadata == Path("/workspace/metadata.tsv")
        assert paths.manifest == Path("/workspace/manifest.tsv")
        assert paths.output == Path("/workspace/out")
        assert paths.workspace == Path("/workspace")

    def test_immutability(self):
        """不変性のテスト"""
        paths = ContainerPaths(
            metadata=Path("/workspace/metadata.tsv"),
            manifest=Path("/workspace/manifest.tsv"),
            output=Path("/workspace/out"),
            workspace=Path("/workspace"),
        )

        with pytest.raises(Exception):  # FrozenInstanceError
            paths.metadata = Path("/new/path")


class TestExecutionConfig:
    """ExecutionConfigクラスのテスト"""

    def test_create_execution_config(self, sample_dataset):
        """ExecutionConfigの作成テスト"""
        config = ExecutionConfig(
            pipeline_type=PipelineType.BASIC,
            datasets=Datasets(sets={sample_dataset}),
            sampling_depth=5000,
            batch_id="batch-456",
        )

        assert config.pipeline_type == PipelineType.BASIC
        assert config.sampling_depth == 5000
        assert config.batch_id == "batch-456"

    def test_get_first_dataset_region(self, sample_dataset, sample_region):
        """最初のデータセットのリージョン取得テスト"""
        config = ExecutionConfig(
            pipeline_type=PipelineType.BASIC,
            datasets=Datasets(sets={sample_dataset}),
            sampling_depth=5000,
            batch_id="batch-456",
        )

        region = config.get_first_dataset_region()
        assert region.name == sample_region.name
        assert region.trunc_len_f == sample_region.trunc_len_f


class TestPipelineContext:
    """PipelineContextクラスのテスト"""

    def test_create_context_with_factory(
        self, mock_executor, sample_setting
    ):
        """ファクトリーメソッドでのコンテキスト作成テスト"""
        context = PipelineContext.create(
            ctn_metadata=Path("/workspace/metadata.tsv"),
            ctn_manifest=Path("/workspace/manifest.tsv"),
            executor=mock_executor,
            setting=sample_setting,
            pipeline_type=PipelineType.BASIC,
        )

        assert context.paths.metadata == Path("/workspace/metadata.tsv")
        assert context.paths.manifest == Path("/workspace/manifest.tsv")
        assert context.config.pipeline_type == PipelineType.BASIC
        assert context.executor == mock_executor

    def test_backward_compatible_properties(
        self, mock_executor, sample_setting
    ):
        """後方互換性プロパティのテスト"""
        context = PipelineContext.create(
            ctn_metadata=Path("/workspace/metadata.tsv"),
            ctn_manifest=Path("/workspace/manifest.tsv"),
            executor=mock_executor,
            setting=sample_setting,
            pipeline_type=PipelineType.ANCOM,
        )

        # 旧インターフェースでのアクセス
        assert context.ctn_metadata == Path("/workspace/metadata.tsv")
        assert context.ctn_manifest == Path("/workspace/manifest.tsv")
        assert context.pipeline_type == PipelineType.ANCOM

    def test_context_immutability(self, mock_executor, sample_setting):
        """コンテキストの不変性テスト"""
        context = PipelineContext.create(
            ctn_metadata=Path("/workspace/metadata.tsv"),
            ctn_manifest=Path("/workspace/manifest.tsv"),
            executor=mock_executor,
            setting=sample_setting,
            pipeline_type=PipelineType.BASIC,
        )

        with pytest.raises(Exception):  # FrozenInstanceError
            context.paths = ContainerPaths(
                metadata=Path("/new"),
                manifest=Path("/new"),
                output=Path("/new"),
                workspace=Path("/new"),
            )

    def test_get_output_path(self, mock_executor, sample_setting):
        """出力パス取得テスト"""
        context = PipelineContext.create(
            ctn_metadata=Path("/workspace/metadata.tsv"),
            ctn_manifest=Path("/workspace/manifest.tsv"),
            executor=mock_executor,
            setting=sample_setting,
            pipeline_type=PipelineType.BASIC,
        )

        output_path = context.get_output_path()
        assert output_path == Path("/workspace/out")

    def test_get_batch_id(self, mock_executor, sample_setting):
        """バッチID取得テスト"""
        context = PipelineContext.create(
            ctn_metadata=Path("/workspace/metadata.tsv"),
            ctn_manifest=Path("/workspace/manifest.tsv"),
            executor=mock_executor,
            setting=sample_setting,
            pipeline_type=PipelineType.BASIC,
        )

        batch_id = context.get_batch_id()
        assert batch_id == "test-batch-123"

    def test_get_sampling_depth(self, mock_executor, sample_setting):
        """サンプリング深度取得テスト"""
        context = PipelineContext.create(
            ctn_metadata=Path("/workspace/metadata.tsv"),
            ctn_manifest=Path("/workspace/manifest.tsv"),
            executor=mock_executor,
            setting=sample_setting,
            pipeline_type=PipelineType.BASIC,
        )

        depth = context.get_sampling_depth()
        assert depth == 10000


class TestPipelineContextBuilder:
    """PipelineContextBuilderクラスのテスト"""

    def test_builder_pattern(self, mock_executor, sample_setting):
        """ビルダーパターンでのコンテキスト構築テスト"""
        context = (
            PipelineContextBuilder()
            .with_metadata(Path("/workspace/metadata.tsv"))
            .with_manifest(Path("/workspace/manifest.tsv"))
            .with_executor(mock_executor)
            .with_setting(sample_setting)
            .with_pipeline_type(PipelineType.RAREFACTION_CURVE)
            .build()
        )

        assert context.ctn_metadata == Path("/workspace/metadata.tsv")
        assert context.ctn_manifest == Path("/workspace/manifest.tsv")
        assert context.pipeline_type == PipelineType.RAREFACTION_CURVE

    def test_builder_requires_all_fields(self):
        """ビルダーが全フィールド必須であることのテスト"""
        builder = PipelineContextBuilder()

        with pytest.raises(ValueError, match="All required fields"):
            builder.build()

    def test_builder_method_chaining(self, mock_executor):
        """メソッドチェーンのテスト"""
        builder = PipelineContextBuilder()

        # メソッドチェーンが同じビルダーを返すことを確認
        result = builder.with_metadata(Path("/workspace/metadata.tsv"))
        assert result is builder

        result = builder.with_executor(mock_executor)
        assert result is builder
