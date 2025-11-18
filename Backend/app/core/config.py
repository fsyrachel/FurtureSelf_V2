# 位于: Backend/app/core/config.py
"""
(P1) 集中配置管理
(基于 Tech Specs v1.5)
"""
from pydantic_settings import BaseSettings
from typing import List
from pydantic import SecretStr

class Settings(BaseSettings):
    # 应用信息 (来自您的 main.py)
    APP_NAME: str = "未来自我 - 职业探索原型 API"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"
    DEBUG: bool = (APP_ENV == "development")
    LOG_LEVEL: str = "DEBUG" if DEBUG else "INFO"

    # CORS (来自您的 main.py)
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",  # (P1) VITE 默认端口
        "http://127.0.0.1:5173",
        "http://localhost:3000",  # (P1) CRA 默认端口
    ]

    # 数据库 (DB v1.3)
<<<<<<< HEAD
    DATABASE_URL: str = "postgresql+psycopg2://futureself:futureself@localhost:5432/futureself_db"

=======
    DATABASE_URL : str= "postgresql+psycopg2://futureself:futureself@localhost:5432/futureself_db"
  
>>>>>>> b218fc476dc540b3f1ff99140de32a837678d817
    # 异步任务 (P1)
    REDIS_URL: str = "redis://localhost:6379/0"
    # # (P1 v1.11 变更)
    # GOOGLE_API_KEY: str = "AIzaSyAzGUb2a9Smg5-vNcT-CA27_TfeeOBEXJs"# (P1 v1.11)
    
    # # (P1 v1.11) Gemini (Chat)
    # GEMINI_MODEL_STANDARD: str = "gemini-2.5-flash"
    # GEMINI_MODEL_VALIDATOR: str = "gemini-2.5-flash"
    # BASE_URL : str = "https://www.chataiapi.com"
    # OPEN_API_KEY: str = "sk-i9V9UPL3RLOS43zeSgVFxR4V2vwRpoceRLkbIXgkf6sU7rvi"  # (P1 v1.10)
    # LLM (P1)
    SILICONFLOW_API_KEY: str = "sk-yfepdlpbtzvofydhieehhnteodpylaatesoxbhbgtaxhgovi" # (P1 v1.10)
    SF_MODEL_STANDARD: str = "zai-org/GLM-4.6" # (示例: 一个强大的模型)
    SF_MODEL_FAST: str = "zai-org/GLM-4.6"                      # (示例: 一个快速的模型)
    SF_MODEL_VALIDATOR: str = "deepseek-ai/DeepSeek-V3.2-Exp"

    # (P1 DB v1.3) 加密密钥 (必须 32 字节)
    ENCRYPTION_KEY: str = "0123456789abcdef0123456789abcdef" 

    MAX_CHAT_MESSAGES: int = 5  # 聊天消息最大条数限制
    
    # (P1 v1.10) 硅基流动
    SILICONFLOW_API_BASE: str = "https://api.siliconflow.cn/v1"
    EMBEDDING_MODEL_NAME: str = "BAAI/bge-m3" # 1024 维

    class Config:
        env_file = ".env" # (P1) 确保您在 Backend/ 根目录有这个 .env 文件
        env_file_encoding = 'utf-8'

settings = Settings()