"""
Persona-aware wrapper around the video operation executor.
"""

import json
import logging
from typing import Any, Dict, Optional

from core.video_operation_executor import VideoOperationExecutor
from persona.manager import PersonaManager

logger = logging.getLogger(__name__)


class PersonaAwareVideoOperationExecutor(VideoOperationExecutor):
    """
    Extends the base executor so every executed operation feeds the persona manager.
    """

    def __init__(
        self,
        output_dir: str = "Results",
        *,
        persona_manager: Optional[PersonaManager] = None,
        user_id: Optional[str] = None,
    ) -> None:
        super().__init__(output_dir=output_dir)
        self.persona_manager = persona_manager or PersonaManager()
        self.persona_user_id = user_id or self.persona_manager.default_user_id

    def execute_from_json(  # type: ignore[override]
        self,
        json_data: Any,
        input_video: Optional[str] = None,
        *,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        video_metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Execute the operation via the base executor and record it for persona learning.
        """
        result = super().execute_from_json(json_data, input_video=input_video)
        if self.persona_manager:
            try:
                payload = self._ensure_dict(json_data)
                self.persona_manager.record_operation(
                    payload,
                    result,
                    input_video=input_video,
                    user_id=user_id or self.persona_user_id,
                    session_id=session_id,
                    video_metadata=video_metadata,
                )
            except Exception:
                logger.exception("Failed to record persona operation.")
        return result

    # Convenience proxies -------------------------------------------------

    def get_persona(self, user_id: Optional[str] = None, refresh: bool = False):
        return self.persona_manager.get_persona(user_id=user_id or self.persona_user_id, refresh=refresh)

    def get_recommendations(self, video_metadata: Dict[str, Any], user_id: Optional[str] = None):
        return self.persona_manager.get_recommendations(video_metadata, user_id=user_id or self.persona_user_id)

    def list_recorded_operations(self, user_id: Optional[str] = None, limit: Optional[int] = None):
        return self.persona_manager.list_operations(user_id=user_id or self.persona_user_id, limit=limit)

    # Internal helpers ----------------------------------------------------

    @staticmethod
    def _ensure_dict(json_data: Any) -> Dict[str, Any]:
        if json_data is None:
            return {}
        if isinstance(json_data, dict):
            return json_data
        if isinstance(json_data, str):
            try:
                return json.loads(json_data)
            except json.JSONDecodeError:
                return {}
        if hasattr(json_data, "dict"):
            try:
                return json_data.dict()
            except Exception:
                return {}
        return {}
