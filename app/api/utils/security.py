import jwt
from fastapi import Depends, HTTPException, Security
from fastapi.security import OAuth2PasswordBearer
from jwt import PyJWTError
from starlette.status import HTTP_403_FORBIDDEN

from app.users import crud as crud_user
from app.api.utils.db import get_async_db
import config
from app.core.jwt import ALGORITHM
from app.users.controller import UserORM
from app.models.token import TokenPayload
from databases import Database

reusable_oauth2 = OAuth2PasswordBearer(tokenUrl=f"{config.OPEN_API_PREFIX}/api/v1/login/access-token")


async def get_current_user(
    token: str = Security(reusable_oauth2),
    async_db: Database = Depends(get_async_db),
):
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[ALGORITHM])
        token_data = TokenPayload(**payload)
    except PyJWTError:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Could not validate credentials"
        )
    user = await crud_user.get(async_db, user_id=token_data.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


async def get_current_active_user(current_user: UserORM = Security(get_current_user)):
    if not crud_user.is_active(current_user):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_current_active_superuser(current_user: UserORM = Security(get_current_user)):
    if not crud_user.is_superuser(current_user):
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return current_user
