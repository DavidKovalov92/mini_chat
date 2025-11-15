from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from db.db_helper import db_helper
from models.user import User
from schemas.user import UserCreate, UserRead

router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "/", 
    response_model=UserRead,  
    status_code=201,
)
async def create_user(
    user_in: UserCreate, 
    session: AsyncSession = Depends(db_helper.session_dependency)
):
    new_user = User(**user_in.model_dump())

    session.add(new_user)

    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=400, 
            detail=f"User with username '{new_user.username}' already exists."
        )
    await session.refresh(new_user)

    return new_user