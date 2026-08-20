from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, chats, user, messages, models
from core.exceptions import AppException
from core.handlers import app_exception_handler

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(AppException, app_exception_handler)
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(user.router, prefix="/user", tags=["user"])
app.include_router(chats.router, prefix="/chats", tags=["chats"])
app.include_router(models.router, prefix="/models", tags=["models"])
app.include_router(messages.router, prefix="/chats/{chat_id}/messages", tags=["messages"])

@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}

@app.get('/')
def read_root():
    return {"message": "Welcome to the API"}