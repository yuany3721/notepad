from datetime import datetime, timedelta
from typing import Optional
import jwt
from ..models.text_file import AuthToken
from ..utils.config import get_settings

class AuthService:
    def __init__(self):
        self.settings = get_settings()
    
    def verify_password(self, password: str) -> AuthToken:
        """验证口令并生成令牌"""
        if password != self.settings.file_list_password:
            raise ValueError("Invalid password")
        
        # 生成JWT令牌
        expires_delta = timedelta(hours=self.settings.jwt_expire_hours)
        expires_at = datetime.utcnow() + expires_delta
        
        to_encode = {
            "exp": expires_at,
            "sub": "file_list_access"
        }
        
        token = jwt.encode(
            to_encode,
            self.settings.jwt_secret_key,
            algorithm=self.settings.jwt_algorithm
        )
        
        return AuthToken(
            token=token,
            expires_at=expires_at
        )
    
    def validate_token(self, token: str) -> bool:
        """验证JWT令牌"""
        try:
            jwt.decode(
                token,
                self.settings.jwt_secret_key,
                algorithms=[self.settings.jwt_algorithm]
            )
            return True
        except jwt.PyJWTError:
            return False