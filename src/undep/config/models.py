from typing import List, Optional
from pydantic import BaseModel, HttpUrl

class SourceLocation(BaseModel):
    repo: str
    branch: str = "main"
    path: str
    
class TargetLocation(BaseModel):
    path: str
    line_start: Optional[int] = None
    line_end: Optional[int] = None

class UpdateConfig(BaseModel):
    frequency: str = "weekly"
    auto_merge: bool = False
    notifications: List[str] = ["email"]

class SourceConfig(BaseModel):
    source: SourceLocation
    target: TargetLocation
    update: UpdateConfig

class UndepConfig(BaseModel):
    version: str
    sources: List[SourceConfig]