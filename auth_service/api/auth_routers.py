import httpx
import uuid
from fastapi import APIRouter, Depends, HTTPException, status, Response

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from fastapi import Cookie
from core.security import decode_token 

from sqlalchemy import select
from core.security import verify_password

from db.db_helper import db_helper
from core.security import get_password_hash, create_access_token, create_refresh_token
from models.auth import AuthUser
from schemas.auth import UserRegister, Token, UserLogin, RefreshRequest

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


@router.post("/login", response_model=Token)
async def login_for_access_token(
    response: Response,
    user_in: UserLogin,
    session: AsyncSession = Depends(db_helper.session_dependency)
):
    # 1. Шукаємо користувача в БД за email
    stmt = select(AuthUser).where(AuthUser.email == user_in.email)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()

    # 2. Перевіряємо існування та пароль
    if not user or not verify_password(user_in.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3. Генеруємо токени
    access_token = create_access_token(user_id=user.id)
    refresh_token = create_refresh_token(user_id=user.id)

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True, 
        samesite="lax"
    )
    # 4. Повертаємо токени (можна також встановити refresh_token у куки)
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )


import traceback # Додай цей імпорт на початку файлу

@router.post("/refresh", response_model=Token)
async def refresh_access_token(
    response: Response,
    refresh_token: str | None = Cookie(None),
    session: AsyncSession = Depends(db_helper.session_dependency)
):
    try:
        if not refresh_token:
            print("DEBUG: Cookie is missing")
            raise HTTPException(status_code=401, detail="Refresh token missing")

        clean_token = refresh_token.strip('"')
        print(f"DEBUG: Processing token: {clean_token[:10]}...")

        token_data = decode_token(clean_token)
        if not token_data:
            print("DEBUG: Decode failed")
            raise HTTPException(status_code=401, detail="Invalid token")

        stmt = select(AuthUser).where(AuthUser.id == token_data.user_id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            print(f"DEBUG: User {token_data.user_id} not found")
            raise HTTPException(status_code=404, detail="User not found")

        new_access = create_access_token(user_id=user.id)
        new_refresh = create_refresh_token(user_id=user.id)

        response.set_cookie(key="refresh_token", value=new_refresh, httponly=True)

        print("DEBUG: Preparing to return Token object")
        
        # Створюємо словник вручну для перевірки
        result_data = {
            "access_token": new_access,
            "refresh_token": new_refresh,
            "token_type": "bearer"
        }
        return result_data

    except Exception as e:
        print("!!! REAL ERROR DETECTED !!!")
        print(traceback.format_exc()) # Оце нарешті покаже все в логах Docker
        raise HTTPException(status_code=500, detail=str(e))