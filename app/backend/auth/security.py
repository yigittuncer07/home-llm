import logging

import bcrypt 
import datetime
import jwt
from constants import JWT_KEY

def hash_password(password: str) -> str:
    
    salt = bcrypt.gensalt()
    hash = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hash.decode('utf-8')

def verify_password(password: str, hash: bytes) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hash)

def generate_jwt_token(user_id: str, role: str, expire: int = 30) -> str:
    payload = {
        'sub': user_id,
        'role': role, 
        'iat': datetime.datetime.now(datetime.timezone.utc),
        'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=expire)
    }
    
    token = jwt.encode(payload, JWT_KEY, algorithm='HS256')
    return token

def validate_jwt_token(token: str) -> dict | None:
    try:
        decoded_payload = jwt.decode(token, JWT_KEY, algorithms=['HS256'])
        return decoded_payload
    except jwt.ExpiredSignatureError:
        logging.warning("Token expired, failed to validate")
        return None
    except jwt.InvalidTokenError:
        logging.warning("Token invalid, failed to validate")
        return None

