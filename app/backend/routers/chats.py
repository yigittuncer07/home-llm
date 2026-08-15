from fastapi import APIRouter

router = APIRouter()

@router.get("/chats")
async def get_chats():
    pass
