import httpx
import uuid
from fastapi import APIRouter, Depends, HTTPException, status, Response

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from db.db_helper import db_helper
from core.security import get_password_hash, create_access_token, create_refresh_token
from models.auth import AuthUser
from schemas.auth import UserRegister, Token, UserLogin

from core.config import settings

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=Token
)
async def register_user(
    user_in: UserRegister,
    session: AsyncSession = Depends(db_helper.session_dependency)
):
    
    user_service_url = settings.USER_SERVICE_URL # 👈 Это должно быть в .env
    
    # Данные для профиля в user_service
    user_profile_data = {
        "username": user_in.username,
    }
    
    new_user_id: uuid.UUID
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{user_service_url}/users/", # 👈 URL эндпоинта user_service
                json=user_profile_data
            )
            
            # Если user_service вернул ошибку (например, "username занят")
            if response.status_code != status.HTTP_201_CREATED:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Error creating user profile: {response.json().get('detail')}"
                )
            
            # Получаем ID созданного пользователя из ответа user_service
            new_user_id = uuid.UUID(response.json().get("id"))
            
    except httpx.RequestError:
        # Если user_service вообще недоступен
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="User service is unavailable."
        )

    # --- Шаг 3: Хэшируем пароль ---
    hashed_password = get_password_hash(user_in.password)
    
    # --- Шаг 4: Создаем AuthUser в auth_db ---
    auth_user = AuthUser(
        id=new_user_id,
        email=user_in.email,
        hashed_password=hashed_password
    )
    
    session.add(auth_user)
    
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered."
        )
    
    access_token = create_access_token(user_id=new_user_id)
    refresh_token = create_refresh_token(user_id=new_user_id)
    
    response = Response(status_code=status.HTTP_201_CREATED)
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        samesite="lax", 
        secure=True   
    )
    
    return Token(
        access_token=create_access_token(user_id=new_user_id),
        refresh_token=create_refresh_token(user_id=new_user_id)
    )