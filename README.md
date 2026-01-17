# 💬 MINI-CHAT
**A scalable, microservices-based chat application built with Python and Docker.**

![GitHub Repo Size](https://img.shields.io/github/repo-size/DavidKovalov92/mini_chat?style=for-the-badge)
![GitHub Language Count](https://img.shields.io/github/languages/count/DavidKovalov92/mini_chat?style=for-the-badge)
![License](https://img.shields.io/github/license/DavidKovalov92/mini_chat?style=for-the-badge)

---

## 📝 Overview
**MINI-CHAT** is a robust messaging platform designed with a **Microservices Architecture**. The project demonstrates a modern approach to software design by separating authentication, user management, and chat functionality into distinct, containerized services.

The primary goal of the project is to provide a highly decoupled environment, orchestrated via **Docker Compose** and routed through a high-performance **Nginx** gateway to ensure scalability and ease of deployment.

---

## ✨ Key Features

* 🧩 **Microservices Architecture:** distinct separation of concerns with dedicated services for **Auth**, **Chat**, and **User** management.
* 🐳 **Containerization:** Fully containerized environment using **Docker** and **Docker Compose**, ensuring consistency across development and production.
* 🌐 **API Gateway:** Centralized request routing using **Nginx** as a reverse proxy to manage traffic between clients and backend services.
* 🔄 **Database Management:** Automated database migrations and schema management handled via **Alembic**.
* 🔐 **Security:** Secure authentication flow handled by a dedicated `auth_service` utilizing **JWT**.

---

## 🛠️ Technical Stack

| Category | Technologies |
| :--- | :--- |
| **Languages** | ![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54) |
| **Infrastructure** | ![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white) ![Nginx](https://img.shields.io/badge/nginx-%23009639.svg?style=for-the-badge&logo=nginx&logoColor=white) |
| **Data & Tools** | ![Alembic](https://img.shields.io/badge/Alembic-F05033?style=for-the-badge&logo=python&logoColor=white) ![Mako](https://img.shields.io/badge/Mako-yellow?style=for-the-badge) |
| **Architecture** | ![Microservices](https://img.shields.io/badge/Microservices-black?style=for-the-badge) ![REST](https://img.shields.io/badge/REST_API-005571?style=for-the-badge&logo=postman) |

---

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
