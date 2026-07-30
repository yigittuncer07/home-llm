from sqlalchemy.orm import Session
from models.user_config import UserConfig

class UserConfigRepository:
    def __init__(self, session: Session):
        self.session = session

    def add(self, config: UserConfig) -> UserConfig:
        self.session.add(config)
        self.session.flush()
        return config

    def get_by_user_id(self, user_id: int) -> UserConfig | None:
        return self.session.get(UserConfig, user_id)