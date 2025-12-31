from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import Response, JSONResponse
from fastapi.openapi.utils import get_openapi
import httpx
import os
import time
from contextlib import asynccontextmanager

auth_service_url = os.getenv("AUTH_SERVICE_URL", "http://localhost:8001")
user_service_url = os.getenv("USER_SERVICE_URL", "http://localhost:8002")
chat_service_url = os.getenv("CHAT_SERVICE_URL", "http://localhost:8003")

SERVICES = {
    "auth_service": auth_service_url,
    "user_service": user_service_url,
    "chat_service": chat_service_url
}

@asynccontextmanager
async def lifespan(app: FastAPI):
    time.sleep(10)
    combined_paths = {}
    combined_components = {
        "schemas": {},
        "responses": {},
        "parameters": {},
        "requestBodies": {},
    }
    combined_tags = []

    async with httpx.AsyncClient(verify=False) as client:
        for name, url in SERVICES.items():
            try:
                response = await client.get(url + "/openapi.json")
                response.raise_for_status()
                openapi_schema = response.json()

                for path, methods in openapi_schema.get("paths", {}).items():
                    new_path = f"/{name}{path}"
                    combined_paths[new_path] = methods

                components = openapi_schema.get("components", {})
                for comp_type, comp_value in components.items():
                    if comp_type in combined_components:
                        combined_components[comp_type].update(comp_value)

                if "tags" in openapi_schema:
                    for tag in openapi_schema["tags"]:
                        if tag not in combined_tags:
                            combined_tags.append(tag)

            except Exception as e:
                print(f"Error fetching OpenAPI schema from {name}: {e}")

    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema
        
        openapi_schema = get_openapi(
            title="API Gateway",
            version="1.0.0",
            description="API Gateway for Microservices",
            routes=app.routes,
        )
        
        # Об'єднуємо компоненти
        openapi_schema["paths"] = combined_paths
        openapi_schema["components"] = combined_components
        openapi_schema["tags"] = combined_tags

        # 1. Переконуємося, що securitySchemes існують
        if "securitySchemes" not in openapi_schema["components"]:
            openapi_schema["components"]["securitySchemes"] = {}
        
        openapi_schema["components"]["securitySchemes"]["BearerAuth"] = {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
        
        # 2. Глобальна безпека
        openapi_schema["security"] = [{"BearerAuth": []}]

        # 3. КРИТИЧНО: Прив'язуємо безпеку до кожного доданого методу
        for path in openapi_schema["paths"]:
            for method in openapi_schema["paths"][path]:
                # Додаємо авторизацію до кожного методу, якщо її там ще немає
                if "security" not in openapi_schema["paths"][path][method]:
                    openapi_schema["paths"][path][method]["security"] = [{"BearerAuth": []}]

        app.openapi_schema = openapi_schema
        return app.openapi_schema

    app.openapi = custom_openapi
    yield

async def forward_request(service_url: str, method: str, path: str, body=None, headers=None, params=None):
    async with httpx.AsyncClient() as client:
        url = f"{service_url}/{path}"
        response = await client.request(method, url, json=body, headers=headers, params=params)
        return response

app = FastAPI(
    lifespan=lifespan,
    swagger_ui_parameters={"persistAuthorization": True}
)

@app.api_route(
    "/{service}/{path:path}", 
    methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    operation_id="proxy_request" 
)
async def gateway(service: str, path: str, request: Request):
    print(f"GATEWAY DEBUG: Browser Auth Header: {request.headers.get('authorization')}")
    if service not in SERVICES:
        raise HTTPException(status_code=404, detail="Service not found")

    service_url = SERVICES[service]
    body = await request.json() if request.method in ["POST", "PUT", "PATCH"] else None
    
    headers = {
        key: value for key, value in request.headers.items() 
        if key.lower() not in ['content-length', 'host']
    }

    params = dict(request.query_params)
    
    response = await forward_request(service_url, request.method, path, body, headers, params)
    return Response(content=response.content,
                    status_code=response.status_code,
                    media_type=response.headers.get('Content-Type'))