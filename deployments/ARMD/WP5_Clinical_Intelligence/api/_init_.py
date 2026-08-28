"""
WP5 API Layer

Contains FastAPI routers.

Responsibilities
----------------

• Request validation

• Dependency injection

• Response serialization

No business logic belongs here.
"""

from .routes import router

__all__ = [
    "router",
]