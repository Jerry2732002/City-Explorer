from pydantic import BaseModel
from typing import List

class UserLogin(BaseModel):
    useremail: str
    password: str

class UserSignup(BaseModel):
    useremail: str
    password: str
    preferences: List[str]
    