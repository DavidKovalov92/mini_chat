from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from jose import jwt, JWTError
from pydantic import BaseModel
import uuid
from core.config import settings


pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)



class TokenData(BaseModel):
    user_id: uuid.UUID

def create_access_token(user_id: uuid.UUID) -> str:
    expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    expires_at = datetime.now(timezone.utc) + expires_delta
    
    to_encode = {
        "sub": str(user_id),  
        "exp": expires_at,    
        "type": "access"    
    }
    
    return jwt.encode(
        to_encode, 
        settings.JWT_SECRET_KEY, 
        algorithm=settings.JWT_ALGORITHM
    )

def create_refresh_token(user_id: uuid.UUID) -> str:
    expires_delta = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    expires_at = datetime.now(timezone.utc) + expires_delta
    
    to_encode = {
        "sub": str(user_id),
        "exp": expires_at,
        "type": "refresh"
    }
    
    return jwt.encode(
        to_encode, 
        settings.JWT_SECRET_KEY, 
        algorithm=settings.JWT_ALGORITHM
    )

def decode_token(token: str) -> TokenData | None:
    try:
        payload = jwt.decode(
            token, 
            settings.JWT_SECRET_KEY, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        user_id = uuid.UUID(payload.get("sub"))
        
        return TokenData(user_id=user_id)
        
    except (JWTError, ValueError, TypeError):
        return None