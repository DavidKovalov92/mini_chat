from fastapi import FastAPI


app = FastAPI(servers=[{"url": "/auth", "description": "Auth Service"}])


@app.get("/")
async def read_root():
    return {"message": "Hello, I'm auth service!"}

@app.get("/items/{item_id}")
async def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}