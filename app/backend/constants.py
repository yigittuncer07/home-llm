import os
from dotenv import load_dotenv

load_dotenv()

JWT_KEY = os.environ['jwt_key']
DATABASE_URL = os.environ['database_url']