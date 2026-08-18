from fastapi import FastAPI
from routers import auth, chats, user, messages
from core.exceptions import AppException
from core.handlers import app_exception_handler

app = FastAPI()
app.add_exception_handler(AppException, app_exception_handler)
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(user.router, prefix="/user", tags=["user"])
app.include_router(chats.router, prefix="/chats", tags=["chats"])
app.include_router(messages.router, prefix="/chats/{chat_id}/messages", tags=["messages"])

@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}

@app.get('/')
def read_root():
    return {"message": "Welcome to the API"}