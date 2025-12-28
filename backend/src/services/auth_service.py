from datetime import datetime, timedelta
from typing import Optional
import jwt
from ..models.text_file import AuthToken
from ..utils.config import get_settings


class AuthService:
    def __init__(self):
        self.settings = get_settings()
    
    def verify_password(self, password: str) -> AuthToken:
        if password != self.settings.file_list_password:
            raise ValueError("Invalid password")
        
        expires_delta = timedelta(minutes=self.settings.jwt_expire_minutes)
        expires_at = datetime.utcnow() + expires_delta
        
        payload = {
            "exp": expires_at,
            "sub": "file_list_access"
        }
        
        token = jwt.encode(payload, self.settings.jwt_secret_key, algorithm="HS256")
        
        return AuthToken(
            token=token,
            expires_at=expires_at
        )
    
    def validate_token(self, token: str) -> bool:
        try:
            jwt.decode(token, self.settings.jwt_secret_key, algorithms=["HS256"])
            return True
        except Exception:
            return False
