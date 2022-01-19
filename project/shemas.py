from typing import List, Optional

from pydantic import BaseModel

class UserA(BaseModel):
    id: int
    is_active: bool
    email: str
    password: str

    class Config:
        orm_mode = True