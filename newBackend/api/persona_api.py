#!/usr/bin/env python3
"""
Persona service API.
Provides endpoints to inspect personas, list operations, and request recommendations.
"""

import logging
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

from persona.manager import PersonaManager

logger = logging.getLogger(__name__)

persona_app = FastAPI(title="Persona Modeling API", version="1.0.0")
persona_manager = PersonaManager()


class RecommendationRequest(BaseModel):
    video_metadata: Dict[str, Any] = Field(default_factory=dict, description="视频元信息")


class TrainPersonaRequest(BaseModel):
    operations: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="可选的操作记录列表，用于手动训练/覆盖",
    )


@persona_app.get("/persona/{user_id}")
def get_persona(user_id: str, refresh: bool = Query(False, description="是否强制重新训练")):
    try:
        persona = persona_manager.get_persona(user_id=user_id, refresh=refresh)
        if not persona:
            raise HTTPException(status_code=404, detail="未找到用户人格数据")
        return {"status": "success", "persona": persona}
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("获取人格信息失败")
        raise HTTPException(status_code=500, detail=str(exc))


@persona_app.get("/persona/{user_id}/operations")
def list_operations(
    user_id: str,
    limit: int = Query(50, ge=1, le=500, description="返回的最大操作数"),
):
    try:
        operations = persona_manager.list_operations(user_id=user_id, limit=limit)
        return {"status": "success", "count": len(operations), "operations": operations}
    except Exception as exc:
        logger.exception("获取操作历史失败")
        raise HTTPException(status_code=500, detail=str(exc))


@persona_app.post("/persona/{user_id}/train")
def train_persona(user_id: str, request: TrainPersonaRequest):
    try:
        persona = persona_manager.train_persona(user_id=user_id, operations=request.operations)
        if not persona:
            raise HTTPException(status_code=404, detail="无操作数据可用于训练")
        return {"status": "success", "persona": persona}
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("训练人格失败")
        raise HTTPException(status_code=500, detail=str(exc))


@persona_app.post("/persona/{user_id}/recommendations")
def recommend_operations(user_id: str, request: RecommendationRequest):
    try:
        recommendations = persona_manager.get_recommendations(
            video_metadata=request.video_metadata or {}, user_id=user_id
        )
        return {"status": "success", "count": len(recommendations), "recommendations": recommendations}
    except Exception as exc:
        logger.exception("获取推荐操作失败")
        raise HTTPException(status_code=500, detail=str(exc))
