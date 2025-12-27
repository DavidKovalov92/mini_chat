# 🚀 Mini Messenger (Microservices Architecture)

Це MVP сучасного месенджера, побудованого на базі мікросервісів. Проєкт демонструє роботу з розподіленими базами даних, JWT-авторизацією через Gateway та міжсервісну взаємодію.



---

## 🛠 Технологічний стек

- **Backend:** FastAPI (Python 3.11+)
- **Database:** PostgreSQL (окрема БД для кожного сервісу)
- **ORM:** SQLAlchemy 2.0 (Async) + Alembic (Migrations)
- **Infrastructure:** Docker & Docker Compose
- **Security:** JWT (Access & Refresh tokens), Argon2 (Hashing)
- **API Gateway:** Reverse Proxy з інтегрованою безпекою та Healthchecks
- **Tools:** DBeaver (DB management), Postman, Swagger/OpenAPI

---

## 📊 Поточний статус розробки

### ✅ COMPLETED (Що вже працює)

#### 🚀 Infrastructure & User Service
- [x] Повна структура проекту та Docker-контейнеризація.
- [x] Налаштування `DatabaseHelper` для асинхронної роботи.
- [x] Live-reload для розробки через Named Volumes.
- [x] **Gateway:** Healthchecks, прокидання портів та виправлення `operation_id` для Swagger.
- [x] **User Service:** CRUD операції для профілів (Create, Read, Update, Delete).
- [x] Ендпоінт `GET /users/me` для отримання профілю через токен.

#### 🔑 Auth Service (JWT/OAuth2)
- [x] Модель `AuthUser` (Email, Hashed Password, User_id).
- [x] **Register:** Синхронне створення профілю в `user_service` зі спільним UUID.
- [x] **Login:** Генерація пари Access & Refresh токенів.
- [x] **Refresh:** Оновлення сесії через куки або JSON body.
- [x] Налаштування `OAuth2PasswordBearer` для захисту ресурсів.

---

## ⏳ TODO (План на майбутнє)

### 💬 Фаза 3 - Chat Service (REST API)
- [ ] Налаштування сервісу та асинхронних міграцій.
- [ ] Моделі: `ChatRoom`, `ChatMember` (Many-to-Many), `Message`.
- [ ] Ендпоінти створення кімнат та керування учасниками.
- [ ] Історія повідомлень з пагінацією та редагування повідомлень.

### ⚡ Фаза 4 - Real-time (WebSockets)
- [ ] Connection Manager для WebSocket з'єднань.
- [ ] Логіка збереження та миттєвої розсилки повідомлень учасникам кімнати.
- [ ] WebSocket-події для редагування та видалення.

### 🦓 Фаза 5 - Kafka (Синхронізація)
- [ ] Статуси користувачів (Online/Offline) через Kafka.
- [ ] Синхронізація змін імені користувача між сервісами.

### 🤖 Фаза 6 - CI/CD & DevOps
- [ ] Покриття коду тестами (pytest + httpx).
- [ ] GitHub Actions для автоматичного Build & Push образів.
- [ ] Налаштування CD (авто-деплой на сервер через SSH).

---

## 🚀 Як запустити проект

1. **Клонувати репозиторій:**
   ```bash
   git clone [https://github.com/DavidKovalov92/mini_chat.git](https://github.com/DavidKovalov92/mini_chat.git)
   cd mini_chat

2. ```bash
    docker compose up --build