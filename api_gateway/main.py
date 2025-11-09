from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response
import httpx

app = FastAPI(title="Unified API Gateway", version="1.0")

# Адреса сервисов
services = {
    "auth": "http://auth_service:8000",
    "users": "http://user_service:8000",
    "chat": "http://chat_service:8000",
}

# 1️⃣ Объединяем OpenAPI схемы всех сервисов
@app.get("/openapi.json")
async def merged_openapi():
    merged_paths = {}
    merged_components = {"schemas": {}}

    async with httpx.AsyncClient() as client:
        for name, url in services.items():
            resp = await client.get(f"{url}/openapi.json")
            data = resp.json()

            # Добавляем префикс сервиса к каждому пути
            for path, value in data.get("paths", {}).items():
                new_path = f"/{name}{path}"
                merged_paths[new_path] = value

            # Объединяем схемы компонентов
            if "components" in data and "schemas" in data["components"]:
                merged_components["schemas"].update(data["components"]["schemas"])

    merged_openapi = {
        "openapi": "3.0.0",
        "info": {"title": "Unified API Gateway", "version": "1.0"},
        "paths": merged_paths,
        "components": merged_components,
    }
    return JSONResponse(merged_openapi)

# 2️⃣ Проксируем все запросы к соответствующим сервисам
@app.api_route("/{service}/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy(service: str, path: str, request: Request):
    if service not in services:
        return JSONResponse({"error": "Service not found"}, status_code=404)

    url = f"{services[service]}/{path}"
    body = await request.body()

    async with httpx.AsyncClient() as client:
        resp = await client.request(
            method=request.method,
            url=url,
            headers=request.headers.raw,
            content=body,
            params=request.query_params
        )

    return Response(content=resp.content, status_code=resp.status_code, headers=resp.headers)
