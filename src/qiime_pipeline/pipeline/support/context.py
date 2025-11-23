"""
Pipeline context classes with improved architecture.

このモジュールはパイプライン実行に必要なコンテキスト情報を提供します。
責務を分離し、不変性と型安全性を確保した設計です。
"""

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Protocol

from qiime_pipeline.data.store import SettingData, Datasets


# --- Enums ---
class PipelineType(Enum):
    """パイプラインの実行タイプ"""

    BASIC = "basic"
    RAREFACTION_CURVE = "rarefaction_curve"
    ANCOM = "ancom"

    def from_str(label: str) -> PipelineType:
        """文字列からPipelineTypeを生成"""
        label = label.lower()
        if label in ("basic", "rarefaction_curve", "ancom"):
            return PipelineType(label)
        else:
            raise ValueError(f"Unknown pipeline type: {label}")


# --- interfaces ---
class CommandExecutor(Protocol):
    """コマンド実行インターフェース"""

    def run(self, command: list[str]) -> str:
        """コマンドを実行し、結果を返す"""
        ...

    def stop(self) -> None:
        """実行環境を停止する"""
        ...


class PathResolver(Protocol):
    """パス解決インターフェース"""

    def get_output_path(self) -> Path:
        """出力ディレクトリのパスを取得"""
        ...

    def get_database_path(self) -> Path:
        """データベースファイルのパスを取得"""
        ...


# --- value objects ---
@dataclass(frozen=True)
class ContainerPaths:
    """
    コンテナ内で使用されるパスの集合

    全てのパスは不変で、作成後に変更できません。
    """

    metadata: Path
    manifest: Path
    output: Path
    workspace: Path

    def __post_init__(self):
        """パスの検証"""
        # コンテナ内パスは絶対パスまたはワークスペース相対パス
        if not self.output.is_absolute() and not str(self.output).startswith("/"):
            object.__setattr__(self, "output", self.workspace / self.output)


@dataclass(frozen=True)
class ExecutionConfig:
    """
    パイプライン実行の設定情報

    サンプリング深度、バッチID、データセット情報など、
    実行時に変更されない設定を保持します。
    """

    pipeline_type: PipelineType
    datasets: Datasets
    sampling_depth: int
    batch_id: str

    def get_first_dataset_region(self):
        """最初のデータセットのリージョン設定を取得"""
        dataset = next(iter(self.datasets.sets))
        return dataset.region


@dataclass(frozen=True)
class PipelineContext:
    """
    パイプライン実行コンテキスト (改善版)

    パイプラインの実行に必要な全ての情報を保持しますが、
    責務を明確に分離し、不変性を確保しています。

    Attributes:
        paths: コンテナ内のパス情報
        config: 実行設定
        executor: コマンド実行インターフェース
        setting: 完全な設定データ (後方互換性のため保持)
    """

    paths: ContainerPaths
    config: ExecutionConfig
    executor: CommandExecutor
    setting: SettingData  # 後方互換性のため保持

    @classmethod
    def create(
        cls,
        ctn_metadata: Path,
        ctn_manifest: Path,
        executor: CommandExecutor,
        setting: SettingData,
        pipeline_type: PipelineType,
    ) -> PipelineContext:
        """
        Args:
            ctn_metadata: コンテナ内のメタデータファイルパス
            ctn_manifest: コンテナ内のマニフェストファイルパス
            executor: コマンド実行インターフェース
            setting: 設定データ
            pipeline_type: パイプラインタイプ

        Returns:
            PipelineContext: 構築されたコンテキスト
        """
        paths = ContainerPaths(
            metadata=ctn_metadata,
            manifest=ctn_manifest,
            output=setting.ctn_output_path,
            workspace=setting.ctn_workspace_path,
        )

        config = ExecutionConfig(
            pipeline_type=pipeline_type,
            datasets=setting.datasets,
            sampling_depth=setting.sampling_depth,
            batch_id=setting.batch_id,
        )

        return cls(
            paths=paths,
            config=config,
            executor=executor,
            setting=setting,
        )

    # 後方互換性のためのプロパティ
    @property
    def ctn_metadata(self) -> Path:
        """後方互換性: メタデータパスへのアクセス"""
        return self.paths.metadata

    @property
    def ctn_manifest(self) -> Path:
        """後方互換性: マニフェストパスへのアクセス"""
        return self.paths.manifest

    @property
    def pipeline_type(self) -> PipelineType:
        """後方互換性: パイプラインタイプへのアクセス"""
        return self.config.pipeline_type

    def get_output_path(self) -> Path:
        """出力パスを取得"""
        return self.paths.output

    def get_batch_id(self) -> str:
        """バッチIDを取得"""
        return self.config.batch_id

    def get_sampling_depth(self) -> int:
        """サンプリング深度を取得"""
        return self.config.sampling_depth

    def get_database_path(self) -> Path:
        """データベースファイルのパスを取得"""
        return self.setting.ctn_database_path

    def get_first_dataset_region(self):
        """最初のデータセットのリージョン設定を取得"""
        return self.config.get_first_dataset_region()


# ========================================
# Context Builder (Optional)
# ========================================


class PipelineContextBuilder:
    """
    PipelineContextを段階的に構築するビルダー

    複雑な構築ロジックをカプセル化し、テスト容易性を向上させます。
    """

    def __init__(self):
        self._metadata: Path | None = None
        self._manifest: Path | None = None
        self._executor: CommandExecutor | None = None
        self._setting: SettingData | None = None
        self._pipeline_type: PipelineType | None = None

    def with_metadata(self, path: Path) -> PipelineContextBuilder:
        """メタデータパスを設定"""
        self._metadata = path
        return self

    def with_manifest(self, path: Path) -> PipelineContextBuilder:
        """マニフェストパスを設定"""
        self._manifest = path
        return self

    def with_executor(self, executor: CommandExecutor) -> PipelineContextBuilder:
        """エグゼキューターを設定"""
        self._executor = executor
        return self

    def with_setting(self, setting: SettingData) -> PipelineContextBuilder:
        """設定データを設定"""
        self._setting = setting
        return self

    def with_pipeline_type(self, pipeline_type: PipelineType) -> PipelineContextBuilder:
        """パイプラインタイプを設定"""
        self._pipeline_type = pipeline_type
        return self

    def build(self) -> PipelineContext:
        """PipelineContextを構築"""
        if not all(
            [
                self._metadata,
                self._manifest,
                self._executor,
                self._setting,
                self._pipeline_type,
            ]
        ):
            raise ValueError("All required fields must be set before building")

        return PipelineContext.create(
            ctn_metadata=self._metadata,
            ctn_manifest=self._manifest,
            executor=self._executor,
            setting=self._setting,
            pipeline_type=self._pipeline_type,
        )
