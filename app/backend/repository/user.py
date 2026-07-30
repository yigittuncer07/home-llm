from sqlalchemy.orm import Session
from models.user import User

class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    def add(self, user: User) -> User:
        self.session.add(user)
        self.session.flush()
        return user

    def get_by_id(self, user_id: int) -> User | None:
        return self.session.get(User, user_id)