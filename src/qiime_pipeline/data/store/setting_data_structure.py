"""
設定データ構造（改善版）

実際の使用パターンを分析し、アクセス性と安全性を両立した設計です。
"""

from __future__ import annotations
import dataclasses
from pathlib import Path
from typing import Callable
from .dataset import Datasets
from .generate_id import generate_id


# --- 定数 ---
DEFAULT_SAMPLING_DEPTH = 10000


# --- Value Objects ---
@dataclasses.dataclass(frozen=True)
class PairPath:
    """
    ローカルのパスとDockerコンテナでのマウント先の組

    Dockerマウント用に特化した値オブジェクトです。

    Attributes:
        local_pos: ホストマシン上のパス（マウント元）
        ctn_pos: コンテナ内でのマウント先パス

    Example:
        >>> pair = PairPath(
        ...     local_pos=Path("/home/user/output"),
        ...     ctn_pos=Path("/workspace/out")
        ... )
        >>> mount_str = f"type=bind,src={pair.local_resolved},dst={pair.ctn_pos}"
    """

    local_pos: Path
    ctn_pos: Path

    @property
    def local_resolved(self) -> Path:
        """
        絶対パスに解決されたローカルパスを取得

        マウント時には絶対パスが必要なため、このプロパティを使用します。
        """
        return self.local_pos.resolve()

    def to_mount_option(self, readonly: bool = True) -> list[str]:
        """
        Dockerマウントオプションとして使える文字列リストを生成

        Args:
            readonly: 読み取り専用でマウントするか

        Returns:
            マウントオプションのリスト

        Example:
            >>> pair.to_mount_option(readonly=True)
            ['type=bind', 'src=/home/user/output', 'dst=/workspace/out,readonly']
        """
        readonly_suffix = ",readonly" if readonly else ""
        return [
            "type=bind",
            f"src={self.local_resolved}",
            f"dst={self.ctn_pos}{readonly_suffix}",
        ]


@dataclasses.dataclass(frozen=True)
class ContainerData:
    """
    コンテナ実行に必要な設定

    Dockerコンテナ実行時の基本設定を保持します。

    Attributes:
        image_or_dockerfile: Dockerイメージ名またはDockerfileのパス
        workspace_path: コンテナ内のワークスペースディレクトリ
        output_path: 出力ディレクトリのパス（ローカル/コンテナ）
        database_path: データベースファイルのパス（ローカル/コンテナ）
    """

    image_or_dockerfile: str | Path
    workspace_path: Path
    output_path: PairPath
    database_path: PairPath


@dataclasses.dataclass(frozen=True)
class SettingData:
    """
    パイプライン全体の設定データ

    不変オブジェクトとして設計されており、作成後の変更は不可能です。
    アクセス性を向上させるため、便利なプロパティを提供しています。

    Attributes:
        container_data: コンテナ関連の設定
        datasets: 解析対象のデータセット
        sampling_depth: サンプリング深度（デフォルト: 10000）
        batch_id: バッチ実行の識別子（自動生成）

    Example:
        >>> setting = SettingData(
        ...     container_data=container_data,
        ...     datasets=datasets,
        ...     sampling_depth=5000
        ... )
        >>> # 簡潔なアクセス
        >>> output = setting.local_output_path  # 以前: setting.container_data.output_path.local_pos
    """

    container_data: ContainerData
    datasets: Datasets
    sampling_depth: int = DEFAULT_SAMPLING_DEPTH
    batch_id: str = dataclasses.field(default_factory=generate_id)

    # ========================================
    # 便利なアクセサプロパティ
    # ========================================

    @property
    def local_output_path(self) -> Path:
        """ローカルの出力ディレクトリパス"""
        return self.container_data.output_path.local_pos

    @property
    def ctn_output_path(self) -> Path:
        """コンテナ内の出力ディレクトリパス"""
        return self.container_data.output_path.ctn_pos

    @property
    def local_database_path(self) -> Path:
        """ローカルのデータベースファイルパス"""
        return self.container_data.database_path.local_pos

    @property
    def ctn_database_path(self) -> Path:
        """コンテナ内のデータベースファイルパス"""
        return self.container_data.database_path.ctn_pos

    @property
    def ctn_workspace_path(self) -> Path:
        """コンテナ内のワークスペースパス"""
        return self.container_data.workspace_path

    @property
    def image(self) -> str | Path:
        """Dockerイメージまたは Dockerfile"""
        return self.container_data.image_or_dockerfile

    @property
    def output_pair(self) -> PairPath:
        """出力パスのペア（ローカル/コンテナ）"""
        return self.container_data.output_path

    @property
    def database_pair(self) -> PairPath:
        """データベースパスのペア（ローカル/コンテナ）"""
        return self.container_data.database_path

    # ========================================
    # 検証メソッド（オプショナル）
    # ========================================

    def validate_local_paths(
        self, validator: Callable[[Path], bool] | None = None, strict: bool = True
    ) -> list[str]:
        """
        ローカル側のパスを検証

        Args:
            validator: パス検証関数（デフォルトは Path.exists）
            strict: Trueの場合、Dockerfileも検証対象にする

        Returns:
            検証エラーのメッセージリスト（空の場合は全て有効）

        Note:
            この検証はオプショナルです。
            本番環境では setup() 時に呼び出すことを推奨しますが、
            テスト環境では省略可能です。

        Example:
            >>> errors = setting.validate_local_paths()
            >>> if errors:
            ...     raise ValueError(f"Invalid paths: {', '.join(errors)}")
        """
        if validator is None:
            validator = lambda p: p.exists()

        errors = []

        # Dockerfileの検証（strictモードのみ）
        if strict and isinstance(self.image, Path):
            if not validator(self.image):
                errors.append(f"Dockerfile not found: {self.image}")

        # 出力ディレクトリの検証
        if not validator(self.local_output_path):
            errors.append(f"Output directory not found: {self.local_output_path}")

        # データベースファイルの検証
        if not validator(self.local_database_path):
            errors.append(f"Database file not found: {self.local_database_path}")

        # Datasetsのパス検証
        for dataset in self.datasets.sets:
            if not validator(dataset.fastq_folder):
                errors.append(f"FASTQ folder not found: {dataset.fastq_folder}")
            if not validator(dataset.metadata_path):
                errors.append(f"Metadata file not found: {dataset.metadata_path}")

        return errors

    def ensure_local_paths(self) -> None:
        """
        ローカルパスの検証を行い、問題があれば例外を発生

        Raises:
            ValueError: パスが存在しない場合

        Note:
            本番環境での使用を想定しています。
            テスト環境では validate_local_paths() を直接使用してください。
        """
        errors = self.validate_local_paths()
        if errors:
            raise ValueError(f"Invalid local paths found:\n  " + "\n  ".join(errors))
