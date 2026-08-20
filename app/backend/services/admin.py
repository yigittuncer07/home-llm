#backend/services/admin.py

import logging

from sqlalchemy.ext.asyncio import AsyncSession
from repository.user import UserRepository

async def get_all_users_service(session: AsyncSession):
    user_repository = UserRepository(session)
    users = await user_repository.get_all()
    logging.info(f"Retrieved {len(users)} users from the database.")
    
    return users