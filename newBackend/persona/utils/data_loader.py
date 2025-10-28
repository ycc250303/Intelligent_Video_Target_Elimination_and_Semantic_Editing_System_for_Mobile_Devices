"""
Backwards compatible data loading helpers that work with the integrated
persona storage.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..storage import PersonaStorage

_storage = PersonaStorage()


def load_operations_data(file_path: Optional[str] = None, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    加载操作数据。

    If file_path is provided, behaves like the original utility. Otherwise,
    fetches the operations persisted for the specified user (defaults to the
    storage manager's default user).
    """
    if file_path:
        path = Path(file_path)
        if not path.is_absolute():
            path = _storage.dataset_path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"数据文件不存在: {path}")
        with path.open("r", encoding="utf-8") as fp:
            data = json.load(fp)
        return data.get("operations", [])

    if not user_id:
        # fall back to the default user data file name
        user_id = "default_user"
    return _storage.load_operations(user_id)


def save_operations_data(
    file_path: Optional[str],
    operations_data: List[Dict[str, Any]],
    user_id: Optional[str] = None,
):
    """
    保存操作数据。写入给定 file_path（如提供），并同步保存到 persona
    持久化目录。保持原始工具行为同时支持系统集成。
    """
    if file_path:
        path = Path(file_path)
        if not path.is_absolute():
            path = _storage.dataset_path(file_path)
        os.makedirs(path.parent, exist_ok=True)
        payload = {
            "metadata": {
                "total_operations": len(operations_data),
            },
            "operations": operations_data,
        }
        with path.open("w", encoding="utf-8") as fp:
            json.dump(payload, fp, ensure_ascii=False, indent=2)

    if user_id:
        _storage.save_operations(user_id, operations_data)
