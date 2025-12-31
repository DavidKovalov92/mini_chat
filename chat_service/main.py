from fastapi import FastAPI
from api.rooms import router as user_router


app = FastAPI(servers=[{"url": "/chat", "description": "Chat Service"}])
app.include_router(user_router)

@app.get("/", tags=['chat_service'])
async def read_root():
    return {"message": "Hello, I'm chat service!"}

