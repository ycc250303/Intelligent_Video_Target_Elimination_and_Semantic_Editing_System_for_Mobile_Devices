"""
Utility helpers for persisting persona-related data.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from .constants import OPERATIONS_DIR, PERSONAS_DIR, DATASETS_DIR


class PersonaStorage:
    """
    Handles persistence of operations history and persona snapshots per user.
    """

    def __init__(
        self,
        operations_dir: Path = OPERATIONS_DIR,
        personas_dir: Path = PERSONAS_DIR,
        datasets_dir: Path = DATASETS_DIR,
    ) -> None:
        self.operations_dir = operations_dir
        self.personas_dir = personas_dir
        self.datasets_dir = datasets_dir

    def _user_operations_path(self, user_id: str) -> Path:
        user_dir = self.operations_dir / user_id
        user_dir.mkdir(parents=True, exist_ok=True)
        return user_dir / "operations.json"

    def load_operations(self, user_id: str) -> List[Dict[str, Any]]:
        path = self._user_operations_path(user_id)
        if not path.exists():
            return []
        try:
            with path.open("r", encoding="utf-8") as fp:
                data = json.load(fp)
        except json.JSONDecodeError:
            return []
        return data.get("operations", [])

    def save_operations(self, user_id: str, operations: List[Dict[str, Any]]) -> None:
        path = self._user_operations_path(user_id)
        payload = {
            "metadata": {
                "user_id": user_id,
                "total_operations": len(operations),
                "updated_at": datetime.utcnow().isoformat() + "Z",
            },
            "operations": operations,
        }
        with path.open("w", encoding="utf-8") as fp:
            json.dump(payload, fp, ensure_ascii=False, indent=2)

    def append_operation(self, user_id: str, operation: Dict[str, Any]) -> None:
        operations = self.load_operations(user_id)
        operations.append(operation)
        self.save_operations(user_id, operations)

    def persona_path(self, user_id: str) -> Path:
        self.personas_dir.mkdir(parents=True, exist_ok=True)
        return self.personas_dir / f"{user_id}.json"

    def load_persona(self, user_id: str) -> Optional[Dict[str, Any]]:
        path = self.persona_path(user_id)
        if not path.exists():
            return None
        try:
            with path.open("r", encoding="utf-8") as fp:
                return json.load(fp)
        except json.JSONDecodeError:
            return None

    def save_persona(self, user_id: str, persona: Dict[str, Any]) -> Path:
        path = self.persona_path(user_id)
        persona = dict(persona)  # avoid accidental mutation
        persona["user_id"] = user_id
        persona["persisted_at"] = datetime.utcnow().isoformat() + "Z"
        with path.open("w", encoding="utf-8") as fp:
            json.dump(persona, fp, ensure_ascii=False, indent=2)
        return path

    def dataset_path(self, relative: str) -> Path:
        """
        Build a path inside the datasets directory for backwards compatibility
        with the original data_loader helper.
        """
        path = (self.datasets_dir / relative).resolve()
        if not str(path).startswith(str(self.datasets_dir.resolve())):
            raise ValueError("Dataset path escape detected.")
        return path
