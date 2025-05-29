#!/usr/bin/env python
import os
import uuid
import docker
import pytest
import shutil
from pathlib import Path
from typing import Generator


def create_temp_dir() -> Path:
    """一時ディレクトリを作成する

    Returns:
        Path: 作成された一時ディレクトリのパス
    """
    tmp_dir = Path("/tmp") / str(uuid.uuid4())
    tmp_dir.mkdir(parents=True, exist_ok=False)
    return tmp_dir
