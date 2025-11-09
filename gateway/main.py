from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import Response, JSONResponse
from fastapi.openapi.utils import get_openapi
import httpx
import os
import time
from contextlib import asynccontextmanager

auth_service = os.getenv("AUTH_SERVICE_URL", "localhost")
user_service = os.getenv("USER_SERVICE_URL", "localhost")
chat_service = os.getenv("CHAT_SERVICE_URL", "localhost")



SERVICES = {
    "auth_service": f"http://{auth_service}:8001",
    "user_service": f"http://{user_service}:8002",
    "chat_service": f"http://{chat_service}:8003"
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
        openapi_schema["paths"] = combined_paths
        openapi_schema["components"] = combined_components
        openapi_schema["tags"] = combined_tags
        app.openapi_schema = openapi_schema
        return app.openapi_schema

    app.openapi = custom_openapi
    yield

async def forward_request(service_url: str, method: str, path: str, body=None, headers=None, params=None):
    async with httpx.AsyncClient() as client:
        url = f"{service_url}/{path}"
        response = await client.request(method, url, json=body, headers=headers, params=params)
        return response

app = FastAPI(lifespan=lifespan)

@app.api_route("/{service}/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def gateway(service: str, path: str, request: Request):
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