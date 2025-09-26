from pydantic import BaseModel

class Message(BaseModel):
    message: str

class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str

class UserPublic(UserBase):
    id: int
    
    class Config:
        from_attributes = True

class UserDB(UserPublic):
    password: str