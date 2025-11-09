from fastapi import FastAPI


app = FastAPI(servers=[{"url": "/users", "description": "User Service"}])


@app.get("/", tags=['user_service'])
async def read_root():
    return {"message": "Hello, I'm user service!"}

@app.get("/items/{item_id}", tags=['user_service'])
async def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}