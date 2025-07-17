"""
Green PM - Security Utilities
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
import secrets
import hashlib
import base64
from cryptography.fernet import Fernet

from src.core.config import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Encryption
cipher_suite = Fernet(settings.ENCRYPTION_KEY.encode() if settings.ENCRYPTION_KEY else Fernet.generate_key())

class SecurityManager:
    """Security utilities manager"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(hours=24)
        
        to_encode.update({"exp": expire})
        
        encoded_jwt = jwt.encode(
            to_encode, 
            settings.JWT_SECRET, 
            algorithm="HS256"
        )
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> Dict[str, Any]:
        """Verify and decode a JWT token"""
        try:
            payload = jwt.decode(
                token, 
                settings.JWT_SECRET, 
                algorithms=["HS256"]
            )
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    @staticmethod
    def generate_reset_token() -> str:
        """Generate a secure reset token"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def generate_api_key() -> str:
        """Generate an API key"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def hash_api_key(api_key: str) -> str:
        """Hash an API key for storage"""
        return hashlib.sha256(api_key.encode()).hexdigest()
    
    @staticmethod
    def encrypt_sensitive_data(data: str) -> str:
        """Encrypt sensitive data"""
        return cipher_suite.encrypt(data.encode()).decode()
    
    @staticmethod
    def decrypt_sensitive_data(encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        return cipher_suite.decrypt(encrypted_data.encode()).decode()
    
    @staticmethod
    def generate_file_token(file_path: str, user_id: int, expires_in: int = 3600) -> str:
        """Generate a temporary file access token"""
        data = {
            "file_path": file_path,
            "user_id": user_id,
            "exp": datetime.utcnow() + timedelta(seconds=expires_in)
        }
        return jwt.encode(data, settings.JWT_SECRET, algorithm="HS256")
    
    @staticmethod
    def verify_file_token(token: str) -> Dict[str, Any]:
        """Verify a file access token"""
        try:
            payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid file access token"
            )

security = SecurityManager()