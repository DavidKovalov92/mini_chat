import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config
from sqlalchemy import pool
# ----------------------------------------------------
# 1. НАШИ ИМПОРТЫ
# ----------------------------------------------------
# Добавляем импорт настроек из нашего приложения
from core.config import settings

# Добавляем импорт Base из нашего приложения
# Alembic будет использовать Base.metadata для поиска моделей
from models.base import Base

# !!! ВАЖНО !!!
# Когда у вас появятся модели (например, User),
# импортируйте их ЗДЕСЬ. Это нужно, чтобы
# Base.metadata "узнал" о них.
#
from models.user import User
# from app.models.item import Item
# ----------------------------------------------------


# Это стандартный код Alembic
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ----------------------------------------------------
# 2. УКАЗЫВАЕМ НАШИ МОДЕЛИ
# ----------------------------------------------------
# Указываем Alembic, что наши модели (metadata)
# находятся в app.models.base.Base.metadata
target_metadata = Base.metadata
# ----------------------------------------------------


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.
    (Этот режим нам не так важен, как online)
    """
    
    # ----------------------------------------------------
    # 3. НАСТРОЙКА URL (OFFLINE)
    # ----------------------------------------------------
    # Получаем наш асинхронный URL из settings
    async_db_url = settings.DATABASE_URL
    # Превращаем его в синхронный (Alembic не умеет в asyncpg)
    sync_db_url = async_db_url.replace("postgresql+asyncpg://", "postgresql://")
    
    context.configure(
        url=sync_db_url,  # Используем наш синхронный URL
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    # ----------------------------------------------------

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.
    (Это основной режим)
    """

    # ----------------------------------------------------
    # 4. НАСТРОЙКА URL (ONLINE)
    # ----------------------------------------------------
    # Эта магия нужна, чтобы взять URL из env.py,
    # а не из alembic.ini
    
    # Копируем секцию [alembic] из конфига
    connectable_config = config.get_section(config.config_ini_section, {})
    
    # Получаем наш асинхронный URL из settings
    async_db_url = settings.DATABASE_URL
    # Превращаем его в синхронный
    sync_db_url = async_db_url.replace("postgresql+asyncpg://", "postgresql://")
    
    # Подменяем URL в конфиге на наш, синхронный
    connectable_config["sqlalchemy.url"] = sync_db_url
    # ----------------------------------------------------

    # Создаем engine с этим URL
    connectable = engine_from_config(
        connectable_config,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()