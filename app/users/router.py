from typing import List

from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from app.api.utils.db import get_async_db
from app.api.utils.security import get_current_active_superuser, get_current_active_user
import config
from app.users.controller import User, UserCreate, UserSec, UserUpdate, UserORM, UserBaseInDB
from app.users import crud as user_crud
from databases import Database

router = APIRouter()


@router.get("/", response_model=List[User])
async def read_users(
    db: Database = Depends(get_async_db),
    skip: int = 0,
    limit: int = 100,
    current_user: UserORM = Depends(get_current_active_superuser),
):
    """
    Retrieve users.
    """
    user_list = await user_crud.get_multi(db, skip=skip, limit=limit)
    return user_list


@router.post("/", response_model=UserBaseInDB)
async def create_user(
    *,
    db: Database = Depends(get_async_db),
    user_in: UserCreate,
    current_user: UserORM = Depends(get_current_active_superuser),
):
    """
    Create new user.
    """
    user = user_crud.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )
    user = user_crud.create(db, user_in=user_in)

    return user


@router.put("/me", response_model=UserBaseInDB)
async def update_user_me(
    *,
    db: Database = Depends(get_async_db),
    password: str = Body(None),
    full_name: str = Body(None),
    email: str = Body(None),
    current_user: UserORM = Depends(get_current_active_user),
):
    """
    Update own user.
    """
    current_user_data = jsonable_encoder(current_user)
    user_in = UserUpdate(**current_user_data)
    if password is not None:
        user_in.password = password
    if full_name is not None:
        user_in.full_name = full_name
    if email is not None:
        user_in.email = email
    user = user_crud.update(db, user=User(**current_user.__dict__), user_in=user_in)
    return user


@router.get("/me", response_model=UserBaseInDB)
async def read_user_me(
    db: Database = Depends(get_async_db),
    current_user: UserORM = Depends(get_current_active_user),
):
    """
    Get current user.
    """
    return current_user


@router.post("/open", response_model=User)
async def create_user_open(
    *,
    db: Database = Depends(get_async_db),
    password: str = Body(...),
    email: str = Body(...),
    full_name: str = Body(None),
):
    """
    Create new user without the need to be logged in.
    """
    if not config.USERS_OPEN_REGISTRATION:
        raise HTTPException(
            status_code=403,
            detail="Open user registration is forbidden on this server",
        )
    user = await user_crud.get_by_email(db, email=email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system",
        )
    user_in = UserCreate(password=password, email=email, full_name=full_name)
    user = user_crud.create(db, user_in=user_in)
    return user


@router.get("/{user_id}", response_model=UserBaseInDB)
async def read_user_by_id(
    user_id: int,
    current_user: UserORM = Depends(get_current_active_user),
    db: Database = Depends(get_async_db),
):
    """
    Get a specific user by id.
    """
    user = await user_crud.get(db, user_id=user_id)
    print("Here", user.email)
    if user == current_user:
        print("Here", user.email)
        return user
    if not user_crud.is_superuser(current_user):
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return user


@router.put("/{user_id}", response_model=UserBaseInDB)
async def update_user(
    *,
    db: Database = Depends(get_async_db),
    user_id: int,
    user_in: UserUpdate,
    current_user: UserSec = Depends(get_current_active_superuser),
):
    """
    Update a user.
    """
    user = await user_crud.get(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system",
        )
    user = user_crud.update(db, user=User(**user.__dict__), user_in=user_in)
    return user
