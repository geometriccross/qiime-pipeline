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


class TestPairPath:
    """改善されたPairPathクラスのテスト"""

    def test_create_pair_path(self, tmp_path):
        """PairPathの作成テスト"""
        local = tmp_path / "output"
        local.mkdir()

        pair = PairPath(local_pos=local, ctn_pos=Path("/workspace/out"))

        assert pair.local_pos == local
        assert pair.ctn_pos == Path("/workspace/out")

    def test_local_resolved_property(self, tmp_path):
        """絶対パス解決のテスト"""
        local = tmp_path / "output"
        local.mkdir()

        pair = PairPath(local_pos=local, ctn_pos=Path("/workspace/out"))

        resolved = pair.local_resolved
        assert resolved.is_absolute()
        assert resolved == local.resolve()

    def test_to_mount_option_readonly(self, tmp_path):
        """マウントオプション生成テスト（readonly）"""
        local = tmp_path / "output"
        local.mkdir()

        pair = PairPath(local_pos=local, ctn_pos=Path("/workspace/out"))

        options = pair.to_mount_option(readonly=True)
        assert len(options) == 3
        assert options[0] == "type=bind"
        assert options[1] == f"src={local.resolve()}"
        assert options[2] == "dst=/workspace/out,readonly"

    def test_to_mount_option_readwrite(self, tmp_path):
        """マウントオプション生成テスト（readwrite）"""
        local = tmp_path / "output"
        local.mkdir()

        pair = PairPath(local_pos=local, ctn_pos=Path("/workspace/out"))

        options = pair.to_mount_option(readonly=False)
        assert len(options) == 3
        assert options[0] == "type=bind"
        assert options[1] == f"src={local.resolve()}"
        assert options[2] == "dst=/workspace/out"

    def test_immutability(self, tmp_path):
        """不変性のテスト"""
        local = tmp_path / "output"
        local.mkdir()

        pair = PairPath(local_pos=local, ctn_pos=Path("/workspace/out"))

        with pytest.raises(Exception):  # FrozenInstanceError
            pair.local_pos = Path("/new/path")


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
        output_path=PairPath(local_pos=output_dir, ctn_pos=Path("/workspace/out")),
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

    def test_create_context_with_factory(self, mock_executor, sample_setting):
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

    def test_backward_compatible_properties(self, mock_executor, sample_setting):
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


class TestSettingData:
    """SettingDataの新しい機能のテスト"""

    def test_accessor_properties(self, sample_setting):
        """アクセサプロパティのテスト"""
        # local_output_path
        assert (
            sample_setting.local_output_path
            == sample_setting.container_data.output_path.local_pos
        )

        # ctn_output_path
        assert (
            sample_setting.ctn_output_path
            == sample_setting.container_data.output_path.ctn_pos
        )

        # local_database_path
        assert (
            sample_setting.local_database_path
            == sample_setting.container_data.database_path.local_pos
        )

        # ctn_database_path
        assert (
            sample_setting.ctn_database_path
            == sample_setting.container_data.database_path.ctn_pos
        )

        # ctn_workspace_path
        assert (
            sample_setting.ctn_workspace_path
            == sample_setting.container_data.workspace_path
        )

        # image
        assert sample_setting.image == sample_setting.container_data.image_or_dockerfile

        # output_pair
        assert sample_setting.output_pair == sample_setting.container_data.output_path

        # database_pair
        assert (
            sample_setting.database_pair == sample_setting.container_data.database_path
        )

    def test_validate_local_paths_success(self, sample_setting):
        """パス検証成功テスト"""

        # 全てのパスが存在すると仮定
        def always_valid(p: Path) -> bool:
            return True

        errors = sample_setting.validate_local_paths(validator=always_valid)
        assert errors == []

    def test_validate_local_paths_failure(self, sample_setting):
        """パス検証失敗テスト"""

        # 全てのパスが存在しないと仮定
        def always_invalid(p: Path) -> bool:
            return False

        errors = sample_setting.validate_local_paths(
            validator=always_invalid, strict=False
        )

        # エラーリストが返されることを確認
        assert len(errors) > 0
        assert any("Output directory" in e for e in errors)
        assert any("Database file" in e for e in errors)

    def test_validate_local_paths_with_existing_files(self, tmp_path, sample_dataset):
        """実際のファイルで検証テスト"""
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        db_file = tmp_path / "db" / "classifier.qza"
        db_file.parent.mkdir()
        db_file.write_text("mock db")

        container_data = ContainerData(
            image_or_dockerfile="quay.io/qiime2/core:latest",
            workspace_path=Path("/workspace"),
            output_path=PairPath(local_pos=output_dir, ctn_pos=Path("/workspace/out")),
            database_path=PairPath(
                local_pos=db_file, ctn_pos=Path("/workspace/db/classifier.qza")
            ),
        )

        setting = SettingData(
            container_data=container_data,
            datasets=Datasets(sets={sample_dataset}),
            sampling_depth=10000,
            batch_id="test-batch",
        )

        # デフォルトの検証（Path.exists）
        errors = setting.validate_local_paths(strict=False)
        assert errors == []

    def test_ensure_local_paths_raises_on_error(self, sample_setting):
        """パス検証エラー時に例外発生テスト"""

        # validate_local_pathsをモックしてエラーを返す
        def always_invalid(p: Path) -> bool:
            return False

        # 検証でエラーがあるのでValueErrorが発生するはず
        # ただし、ensure_local_pathsは内部でvalidate_local_pathsを呼ぶので、
        # 直接モックすることはできない。代わりに存在しないパスを持つsettingを作る

        non_existent = Path("/non/existent/path")
        container_data = ContainerData(
            image_or_dockerfile="quay.io/qiime2/core:latest",
            workspace_path=Path("/workspace"),
            output_path=PairPath(
                local_pos=non_existent, ctn_pos=Path("/workspace/out")
            ),
            database_path=PairPath(
                local_pos=non_existent, ctn_pos=Path("/workspace/db/classifier.qza")
            ),
        )

        bad_setting = SettingData(
            container_data=container_data,
            datasets=sample_setting.datasets,
            sampling_depth=10000,
            batch_id="test-batch",
        )

        with pytest.raises(ValueError, match="Invalid local paths"):
            bad_setting.ensure_local_paths()

    def test_immutability(self, sample_setting):
        """不変性のテスト"""
        with pytest.raises(Exception):  # FrozenInstanceError
            sample_setting.sampling_depth = 5000
