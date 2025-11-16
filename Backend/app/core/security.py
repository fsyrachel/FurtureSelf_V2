# 位于: Backend/app/core/security.py
"""
(P1) 加密/解密服务
(基于 Tech Specs v1.5 - 数据安全要求)
"""
import base64
from cryptography.fernet import Fernet
from app.core.config import settings

# 从十六进制字符串密钥创建 Fernet 实例
# 密钥必须是 32 字节且 URL-safe base64 编码
# 我们将十六进制密钥转换为字节，然后进行 base64 编码
key_bytes = bytes.fromhex(settings.ENCRYPTION_KEY)
fernet_key = base64.urlsafe_b64encode(key_bytes)
cipher_suite = Fernet(fernet_key)

def encrypt_data(data: str) -> str:
    """加密数据"""
    if not data:
        return data
    encrypted_data = cipher_suite.encrypt(data.encode('utf-8'))
    return encrypted_data.decode('utf-8')

def decrypt_data(encrypted_data: str) -> str:
    """解密数据"""
    if not encrypted_data:
        return encrypted_data
    decrypted_data = cipher_suite.decrypt(encrypted_data.encode('utf-8'))
    return decrypted_data.decode('utf-8')
