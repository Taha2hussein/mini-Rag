from pydantic import BaseModel, EmailStr
from typing import Optional


class UserInCreate(BaseModel):
    email: EmailStr
    password: str
    last_name: str
    first_name: str 
    
class UserInUpdate(BaseModel):
    id: int
    email: EmailStr
    password: str
    last_name: str
    first_name: str 

class UserOutput(BaseModel):
    id: int | None = None
    email: EmailStr | None = None
    last_name: str | None = None
    first_name: str | None = None
     
     
class LoginwithToken(BaseModel):
    user_token: str
    
    
class UserInLogin(BaseModel):
    email: EmailStr
    password: str