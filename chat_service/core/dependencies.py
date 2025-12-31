import uuid
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from fastapi import Request
from core.config import settings

# Вказуємо шлях до логіну, щоб Swagger знав, куди звертатися
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth_service/auth/login")

from fastapi import Request, Header

async def get_current_user_id(
    request: Request, 
    authorization: str | None = Header(None) # Беремо заголовок напряму
) -> uuid.UUID:
    # Цей принт спрацює ЗАВЖДИ
    print(f"DEBUG: ALL HEADERS: {dict(request.headers)}")
    print(f"DEBUG: RAW AUTH HEADER: {authorization}")

    if not authorization or not authorization.startswith("Bearer "):
        print("DEBUG: Authorization header is missing or invalid format")
        raise HTTPException(status_code=401, detail="Not authenticated")

    token = authorization.replace("Bearer ", "")
    
    try:
        payload = jwt.decode(
            token, 
            settings.JWT_SECRET_KEY, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        user_id_str: str = payload.get("sub")
        if not user_id_str:
            raise HTTPException(status_code=401, detail="Token sub missing")
            
        return uuid.UUID(user_id_str)
        
    except JWTError as e:
        print(f"DEBUG: JWT Decode Error: {e}")
        raise HTTPException(status_code=401, detail=str(e))
    


async def get_ws_user(token: str):
    """Функція для перевірки токена у WebSocket"""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        return uuid.UUID(user_id)
    except (JWTError, ValueError):
        return None