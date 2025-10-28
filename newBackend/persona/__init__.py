"""
Persona integration package.

Exposes the persona manager and executor adapter that bridge the
video editing persona modeling components into the backend system.
"""

from .manager import PersonaManager
from .executor import PersonaAwareVideoOperationExecutor

__all__ = ["PersonaManager", "PersonaAwareVideoOperationExecutor"]
