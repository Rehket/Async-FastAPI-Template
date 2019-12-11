from typing import Optional
from pydantic import BaseModel
from sqlalchemy import Boolean, Column, Integer, String, DateTime, FetchedValue
from app.db.base_class import Base
from datetime import datetime

class UserORM(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean(), default=True)
    is_superuser = Column(Boolean(), default=False)
    sys_revision = Column(Integer, server_default=FetchedValue())
    sys_created_date = Column(DateTime(timezone=True),  server_default=FetchedValue())
    sys_modified_date = Column(DateTime(timezone=True), server_default=FetchedValue())


# Shared properties
class UserBase(BaseModel):
    email: Optional[str] = None
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    full_name: Optional[str] = None

    class Config:
        orm_mode = True


class UserBaseInDB(UserBase):
    id: int = None
    sys_revision: int = None
    sys_created_date: datetime = None
    sys_modified_date: datetime = None

# Properties to receive via API on creation
class UserCreate(UserBaseInDB):
    email: str
    password: str


# Properties to receive via API on update
class UserUpdate(UserBaseInDB):
    password: Optional[str] = None


# Additional properties to return via API
class User(UserBaseInDB):
    pass


# Additional properties stored in DB
class UserSec(UserBaseInDB):
    hashed_password: str
