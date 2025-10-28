"""
Persona manager that glues backend operations with the persona modeling core.
"""

import json
import logging
import uuid
from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional

from .constants import DEFAULT_USER_ID
from .core.persona_model import VideoEditingPersona
from .storage import PersonaStorage

logger = logging.getLogger(__name__)


class PersonaManager:
    """
    High-level facade for managing persona training data and inference.
    """

    def __init__(
        self,
        storage: Optional[PersonaStorage] = None,
        default_user_id: str = DEFAULT_USER_ID,
        max_operations: Optional[int] = 1000,
    ) -> None:
        self.storage = storage or PersonaStorage()
        self.default_user_id = default_user_id
        self.max_operations = max_operations
        self._persona_cache: Dict[str, Dict[str, Any]] = {}

    # ------------------------------------------------------------------
    # Data ingestion
    # ------------------------------------------------------------------

    def record_operation(
        self,
        operation_request: Any,
        result: Any = None,
        *,
        input_video: Optional[str] = None,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        video_metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Persist an operation executed by the backend for persona learning.
        """
        user_id = user_id or self.default_user_id
        try:
            record = self._build_operation_record(
                operation_request,
                result,
                input_video=input_video,
                session_id=session_id,
                video_metadata=video_metadata,
            )
        except Exception:
            logger.exception("Failed to build operation record for persona tracking.")
            return None

        if not record or not record.get("action"):
            return None

        try:
            operations = self.storage.load_operations(user_id)
            operations.append(record)
            if self.max_operations and len(operations) > self.max_operations:
                operations = operations[-self.max_operations :]
            self.storage.save_operations(user_id, operations)
            self._persona_cache.pop(user_id, None)
        except Exception:
            logger.exception("Failed to append persona operation record.")
            return None
        return record

    def _build_operation_record(
        self,
        operation_request: Any,
        result: Any,
        *,
        input_video: Optional[str],
        session_id: Optional[str],
        video_metadata: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        data = self._normalize_request(operation_request)
        operation_data = data.get("operations", {})

        record: Dict[str, Any] = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "action": operation_data.get("operation"),
            "parameters": operation_data.get("params", {}),
            "editor": operation_data.get("editor", "ffmpeg"),
            "input_video": input_video,
            "session_id": session_id or data.get("session_id"),
            "video_context": video_metadata
            or data.get("video_metadata")
            or data.get("video_context")
            or {},
            "metadata": data.get("metadata", {}),
        }

        if result is not None:
            record.update(
                {
                    "output_video": getattr(result, "output_path", None),
                    "success": bool(getattr(result, "success", False)),
                    "success_metric": 1.0 if getattr(result, "success", False) else 0.0,
                    "execution_time": getattr(result, "execution_time", 0.0) or 0.0,
                    "error_message": getattr(result, "error_message", None),
                }
            )
            metadata = getattr(result, "metadata", None)
            if metadata:
                record["result_metadata"] = metadata
        else:
            record.update(
                {
                    "output_video": None,
                    "success": False,
                    "success_metric": 0.0,
                    "execution_time": 0.0,
                    "error_message": None,
                }
            )

        return record

    def _normalize_request(self, operation_request: Any) -> Dict[str, Any]:
        if operation_request is None:
            return {}
        if isinstance(operation_request, dict):
            return operation_request
        if isinstance(operation_request, str):
            try:
                return json.loads(operation_request)
            except json.JSONDecodeError:
                logger.warning("Operation request JSON decode failed.")
                return {}
        if hasattr(operation_request, "dict"):
            try:
                return operation_request.dict()
            except Exception:
                return {}
        return {}

    # ------------------------------------------------------------------
    # Persona lifecycle
    # ------------------------------------------------------------------

    def train_persona(self, user_id: Optional[str] = None, operations: Optional[Iterable[Dict[str, Any]]] = None):
        user_id = user_id or self.default_user_id
        operations_list = list(operations) if operations is not None else self.storage.load_operations(user_id)
        if not operations_list:
            return None

        persona_model = VideoEditingPersona(user_id=user_id)
        persona_model.train(operations_list)
        persona_data = persona_model.get_persona()
        self.storage.save_persona(user_id, persona_data)
        self._persona_cache[user_id] = persona_data
        return persona_data

    def get_persona(self, user_id: Optional[str] = None, refresh: bool = False):
        user_id = user_id or self.default_user_id

        if not refresh and user_id in self._persona_cache:
            return self._persona_cache[user_id]

        if not refresh:
            persona_data = self.storage.load_persona(user_id)
            if persona_data:
                self._persona_cache[user_id] = persona_data
                return persona_data

        persona_data = self.train_persona(user_id=user_id)
        return persona_data

    def get_recommendations(self, video_metadata: Dict[str, Any], user_id: Optional[str] = None):
        user_id = user_id or self.default_user_id
        persona_data = self.get_persona(user_id)
        if not persona_data:
            return []

        persona_model = VideoEditingPersona(user_id=user_id)
        persona_model.user_persona = persona_data
        return persona_model.predict_operations(video_metadata or {})

    def list_operations(self, user_id: Optional[str] = None, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        user_id = user_id or self.default_user_id
        operations = self.storage.load_operations(user_id)
        if limit:
            return operations[-limit:]
        return operations

    def clear_cache(self):
        self._persona_cache.clear()
