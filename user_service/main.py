from fastapi import FastAPI
from api.user_routers import router as user_router


app = FastAPI()

app.include_router(user_router)

@app.get("/", tags=['Users'])
async def read_root():
    return {"message": "Hello, I'm user service!"}

