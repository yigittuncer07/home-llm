from pydantic import BaseModel

class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    

class RegisterRequest(BaseModel):
    email: str
    password: str
    
class RegisterResponse(BaseModel):
    message: str