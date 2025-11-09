from fastapi import FastAPI


app = FastAPI(servers=[{"url": "/chat", "description": "Chat Service"}])


@app.get("/", tags=['chat_service'])
async def read_root():
    return {"message": "Hello, I'm chat service!"}

@app.get("/items/{item_id}", tags=['chat_service'])
async def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}