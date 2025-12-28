import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select 
from fastapi import Query
from db.db_helper import db_helper
from models.user import User
from fastapi import Response
from schemas.user import UserCreate, UserRead, UserUpdate

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

@router.get("/{user_id}", response_model=UserRead)
async def get_user_by_id(
    user_id: uuid.UUID,
    session: AsyncSession = Depends(db_helper.session_dependency)
):
    user = await session.get(User, user_id)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found."
        )

    return user

@router.patch("/{user_id}", response_model=UserRead)
async def update_user_profile(
    user_id: uuid.UUID,
    user_update: UserUpdate,
    session: AsyncSession = Depends(db_helper.session_dependency)
):
    user = await session.get(User, user_id)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found."
        )
    
    update_data = user_update.model_dump(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(user, key, value)
    
    session.add(user)
    await session.commit()
    await session.refresh(user)
    
    return user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: uuid.UUID,
    session: AsyncSession = Depends(db_helper.session_dependency)
):
    user = await session.get(User, user_id)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found."
        )
        
    await session.delete(user)
    await session.commit()
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/", response_model=list[UserRead])
async def get_all_users(
    session: AsyncSession = Depends(db_helper.session_dependency),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100)
):
    statement = select(User).offset(skip).limit(limit)
    
    result = await session.execute(statement)
    users = result.scalars().all()
    
    return users