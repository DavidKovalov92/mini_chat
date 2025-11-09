from fastapi import FastAPI


app = FastAPI()


@app.get("/", tags=['auth_service'])
async def read_root():
    return {"message": "Hello, I'm auth service!"}

@app.get("/items/{item_id}", tags=['auth_service'])
async def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}