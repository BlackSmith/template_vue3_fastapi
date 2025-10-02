from fastapi import APIRouter, Depends, Security, status
from libs.db import DBPool, db_pool
from typing import List
from libs.keycloak import get_me
from models.base import query_params
from models.user import User, UserDB, UserUpdate

router = APIRouter(tags=["users"])
sql_logger = 'sql.users'



@router.get("/", response_model=List[User])
async def user_list(q_params: dict = Depends(query_params),
                    pool: DBPool = Depends(db_pool),
                    _user: User = Security(get_me)):
    _user.test_permission('admin:all')
    async with pool.acquire_with_log(sql_logger) as db:
        users = await UserDB.gets(db, 'disabled IS NOT true', **q_params)
        # for user in users:
        #     await UserDB.load_assigns(db, user)
        return users


@router.get("/{user_id}", response_model=User)
async def user_get(user_id: int,
                   pool: DBPool = Depends(db_pool),
                   _user: User = Security(get_me)):
    _user.test_permission('admin:all')
    async with pool.acquire_with_log(sql_logger) as db:
        user = await UserDB.get(db, user_id)
        # await UserDB.load_assigns(db, user)
        return user

@router.put("/{user_id}", response_model=User)
async def user_update(user_id: int, update: UserUpdate,
                      pool: DBPool = Depends(db_pool),
                      _user: User = Security(get_me)):
    _user.test_permission('admin:all')
    async with pool.acquire_with_log(sql_logger) as db, db.transaction():
        return await UserDB.update(db, user_id, update)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def user_delete(user_id: int,
                      pool: DBPool = Depends(db_pool),
                      _user: User = Security(get_me)):
    _user.test_permission('admin:all')
    async with pool.acquire_with_log(sql_logger) as db, db.transaction():
        await UserDB.delete(db, user_id)


# @router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
# async def user_create(create: UserCreate,
#                       pool: DBPool = Depends(db_pool),
#                       _user: User = Security(get_client)):
#     _user.test_permission('admin:all')
#     async with pool.acquire_with_log(sql_logger) as db:
#         return await UserDB.create(db, create)

