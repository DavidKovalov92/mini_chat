# Mini Chat 💬

A scalable, microservices-based chat application built with Python and Docker. This project demonstrates a modern architecture pattern separating authentication, user management, and chat functionality into distinct services, orchestrated via Docker Compose and routed through an Nginx gateway.

## 🚀 Features

* **Microservices Architecture**: Separate services for Auth, Chat, and User management.
* **Dockerized**: Fully containerized environment using `docker-compose` for easy deployment.
* **API Gateway**: Nginx configured as a reverse proxy to route requests to appropriate services.
* **Scalable Design**: Modular structure allowing independent development and scaling of components.
* **Database Migrations**: Managed via Alembic (Mako templates detected).

## 🛠️ Tech Stack

* **Language**: Python 3.x
* **Containerization**: Docker, Docker Compose
* **Gateway/Proxy**: Nginx
* **Database Tools**: Alembic (Migrations)
* **Services**:
    * `auth_service` - Handles registration and authentication (JWT).
    * `chat_service` - Manages messaging logic.
    * `user_service` - Handles user profiles and data.
    * `gateway` - Entry point for the frontend/clients.

## 📂 Project Structure

```text
mini_chat/
├── auth_service/      # Service for Authentication
├── chat_service/      # Service for Chat logic
├── user_service/      # Service for User management
├── gateway/           # API Gateway configuration
├── nginx/             # Nginx configuration files
├── docker-compose.yaml # Orchestration file
└── requirements.txt   # Project dependencies
