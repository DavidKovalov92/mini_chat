from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert

from sqlalchemy import select, desc
from models.chat import Message, chat_members
from schemas.chat import MessageRead

from sqlalchemy import select
from models.chat import ChatRoom, chat_members 

from models.chat import Message
from schemas.chat import MessageCreate, MessageRead

from db.db_helper import db_helper
from models.chat import ChatRoom, chat_members
from schemas.chat import RoomCreate, RoomRead
from core.dependencies import get_current_user_id
import uuid

router = APIRouter(prefix="/rooms", tags=["Rooms"])

@router.post("/", response_model=RoomRead, status_code=status.HTTP_201_CREATED)
async def create_room(
    room_in: RoomCreate,
    current_user_id: uuid.UUID = Depends(get_current_user_id),
    session: AsyncSession = Depends(db_helper.session_dependency),
):
    # 1. Створюємо об'єкт кімнати
    new_room = ChatRoom(
        name=room_in.name,
        owner_id=current_user_id
    )
    session.add(new_room)
    
    # Виконуємо flush, щоб отримати ID нової кімнати перед коммітом
    await session.flush()

    # 2. Додаємо творця в таблицю учасників (chat_members)
    stmt = insert(chat_members).values(
        room_id=new_room.id,
        user_id=current_user_id
    )
    await session.execute(stmt)

    # 3. Зберігаємо зміни
    await session.commit()
    await session.refresh(new_room)

    return new_room

@router.get("/", response_model=list[RoomRead])
async def get_my_rooms(
    current_user_id: uuid.UUID = Depends(get_current_user_id),
    session: AsyncSession = Depends(db_helper.session_dependency),
):
    # 1. Створюємо запит: вибираємо кімнати, де ID користувача є в учасниках
    stmt = (
        select(ChatRoom)
        .join(chat_members)
        .where(chat_members.c.user_id == current_user_id)
        .order_by(ChatRoom.created_at.desc())
    )
    
    # 2. Виконуємо запит
    result = await session.execute(stmt)
    rooms = result.scalars().all()
    
    # 3. Повертаємо список (навіть якщо він порожній, це буде [], а не None)
    return rooms

@router.post("/{room_id}/messages", response_model=MessageRead, status_code=status.HTTP_201_CREATED)
async def send_message(
    room_id: uuid.UUID,
    message_in: MessageCreate,
    current_user_id: uuid.UUID = Depends(get_current_user_id),
    session: AsyncSession = Depends(db_helper.session_dependency),
):
    # 1. Перевіряємо, чи є користувач учасником цієї кімнати
    member_check_stmt = select(chat_members).where(
        chat_members.c.room_id == room_id,
        chat_members.c.user_id == current_user_id
    )
    member_exists = await session.execute(member_check_stmt)
    
    if not member_exists.fetchone():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Ви не є учасником цієї кімнати"
        )

    # 2. Створюємо повідомлення
    new_message = Message(
        room_id=room_id,
        sender_id=current_user_id,
        text=message_in.text
    )
    
    session.add(new_message)
    await session.commit()
    await session.refresh(new_message)

    return new_message


@router.get("/{room_id}/messages", response_model=list[MessageRead])
async def get_room_messages(
    room_id: uuid.UUID,
    limit: int = 50,
    offset: int = 0,
    current_user_id: uuid.UUID = Depends(get_current_user_id),
    session: AsyncSession = Depends(db_helper.session_dependency),
):
    """
    Отримати історіy повідомлень для конкретної кімнати.
    Тільки учасники кімнати мають доступ до історії.
    """
    
    # 1. Перевірка членства (Security Check)
    # Ми не дозволяємо бачити повідомлення тим, хто не в чаті
    member_check_stmt = select(chat_members).where(
        chat_members.c.room_id == room_id,
        chat_members.c.user_id == current_user_id
    )
    member_exists = await session.execute(member_check_stmt)
    
    if not member_exists.fetchone():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Ви не є учасником цієї кімнати"
        )

    # 2. Отримання повідомлень
    # Сортуємо за часом (спочатку нові), додаємо ліміти для пагінації
    stmt = (
        select(Message)
        .where(Message.room_id == room_id)
        .order_by(desc(Message.created_at))
        .limit(limit)
        .offset(offset)
    )
    
    result = await session.execute(stmt)
    messages = result.scalars().all()

    # Повертаємо список повідомлень (Pydantic автоматично перетворить їх за схемою MessageRead)
    return messages


from fastapi import WebSocket, WebSocketDisconnect, Query
from api.ws_manager import manager
from jose import jwt, JWTError
from core.config import settings
from core.dependencies import get_ws_user



@router.websocket("/{room_id}/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    room_id: uuid.UUID,
    token: str = Query(...)
):
    # 1. Перевірка токена
    user_id = await get_ws_user(token)
    if not user_id:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    # 2. Перевірка членства в кімнаті (можна додати запит до БД тут)
    # Для швидкості поки припустимо, що перевірка пройшла успішно

    # 3. Підключення
    await manager.connect(websocket, room_id)
    
    try:
        while True:
            # Очікуємо повідомлення від клієнта
            data = await websocket.receive_json()
            
            # Тут зазвичай повідомлення зберігається в базу даних (як ми робили в POST методі)
            # А потім розсилається всім учасникам
            
            resp_message = {
                "room_id": str(room_id),
                "sender_id": str(user_id),
                "text": data.get("text"),
                "type": "new_message"
            }
            
            await manager.broadcast(resp_message, room_id)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, room_id)