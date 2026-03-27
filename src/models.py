"""
Dataclass models for Taskly (MongoDB).
Replaced SQLAlchemy ORM with plain Python dataclasses after migrating to MongoDB.
"""
from dataclasses import dataclass, field
from datetime import datetime
import uuid

@dataclass
class Task:
    title: str
    description: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def to_dict(self):
        return {"id": self.id, "title": self.title, "description": self.description, "created_at": self.created_at.isoformat()}
