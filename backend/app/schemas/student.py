from pydantic import BaseModel

class StudentCreateRequest(BaseModel):
    name: str
    group: str
    avatar: str 

class StudentResponse(BaseModel):
    id: int
    name: str
    group: str
    avatar: str
    balance: int
    hash_access_key: str

    class Config:
        orm_mode = True