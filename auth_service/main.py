from fastapi import FastAPI
from api.auth_routers import router as auth_router


app = FastAPI()
app.include_router(auth_router)


@app.get("/", tags=['auth_service'])
def health_check():
    return {"status": "ok"}