from fastapi import FastAPI


app = FastAPI(servers=[{"url": "/users", "description": "User Service"}])


@app.get("/", tags=['user_service'])
async def read_root():
    return {"message": "Hello, I'm user service!"}

