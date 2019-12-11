from typing import List, Optional

from fastapi.encoders import jsonable_encoder
from sqlalchemy.sql import select, insert
from app.core.security import get_password_hash, verify_password
from app.users.controller import UserCreate, UserUpdate, UserSec, UserORM, User, UserBaseInDB
from databases import Database


async def get(async_db: Database, *, user_id: int) -> Optional[UserORM]:

    result = await async_db.fetch_one(select([UserORM]).where(UserORM.id == user_id))
    return UserORM(**result.__dict__.get("_row"))


async def get_by_email(async_db: Database, *, email: str) -> Optional[UserSec]:
    result = await async_db.fetch_one(select([UserORM]).where(UserORM.email == email))
    if result:
        return UserSec(**result.__dict__.get("_row"))
    return None


async def authenticate(async_db: Database, *, email: str, password: str) -> Optional[User]:
    user = await get_by_email(async_db, email=email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    # Convert to User instance from UserInDb that does not includes hash.
    return User(**user.dict())


def is_active(user) -> bool:
    return user.is_active


def is_superuser(user) -> bool:
    return user.is_superuser


async def get_multi(async_db: Database, *, skip=0, limit=100) -> List[Optional[UserBaseInDB]]:
    users = []
    async for user in async_db.iterate(select([UserORM]).offset(skip).limit(limit)):
        user_rec = user.__dict__.get("_row")
        users.append(UserBaseInDB(**user_rec))
    return users


async def create(async_db: Database, *, user_in: UserCreate) -> User:
    user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        is_superuser=user_in.is_superuser,
    )
    print(insert(UserORM))
    res = await async_db.execute(insert(UserORM), **user.dict())
    # db_session.commit()
    # db_session.refresh(user)
    return res


async def update(async_db: Database, *, user: User, user_in: UserUpdate) -> User:
    user_data = jsonable_encoder(user)
    update_data = user_in.dict(skip_defaults=True)
    for field in user_data:
        if field in update_data:
            setattr(user, field, update_data[field])
    if user_in.password:
        passwordhash = get_password_hash(user_in.password)
        user.hashed_password = passwordhash

    await async_db.execute(insert(UserORM), values=user.dict())
    refreshed_user = await get(async_db=async_db, user_id=user.id)
    return User(**refreshed_user.__dict__)
