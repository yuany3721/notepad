from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class TextFile(BaseModel):
    filename: str
    content: str
    created_at: datetime
    updated_at: datetime
    size: int

class FileListItem(BaseModel):
    filename: str
    created_at: datetime
    updated_at: datetime
    size: int
    preview: Optional[str] = None

class SaveRequest(BaseModel):
    content: str

class AuthToken(BaseModel):
    token: str
    expires_at: datetime

class PasswordRequest(BaseModel):
    password: str

class FileListResponse(BaseModel):
    files: List[FileListItem]
    total: int
    page: int
    limit: int