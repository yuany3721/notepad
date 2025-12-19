from pydantic_settings import BaseSettings
from pathlib import Path
import os

class Settings(BaseSettings):
    """应用配置"""
    
    # 基础配置
    app_name: str = os.getenv("APP_NAME", "Vue3 + Python Notepad")
    
    # 文件存储配置
    notes_dir: str = "/app/data"
    
    # 安全配置
    file_list_password: str = os.getenv("FILE_LIST_PASSWORD", "admin123")
    
    # JWT配置（使用固定值，简化配置）
    jwt_secret_key: str = "default-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440  # 24小时
    
    # 文件限制（使用固定值，简化配置）
    max_file_size: int = 100000  # 100KB
    max_filename_length: int = 200
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# 创建全局设置实例
settings = Settings()

def get_settings() -> Settings:
    return settings

# 确保数据目录存在
def ensure_data_directory():
    os.makedirs(settings.notes_dir, exist_ok=True)

# 在导入时创建目录
ensure_data_directory()