from fastapi import APIRouter, Depends, Security, status

from libs.db import DBPool, db_pool
from typing import List

from libs.keycloak import get_me
from models.base import query_params
from models.user import User
from models.usergroup import (UserGroup, UserGroupUpdate, UserGroupCreate,
                              UserGroupDB)

router = APIRouter(tags=["usergroups"])
sql_logger = 'sql.usergroups'


@router.get("/", response_model=List[UserGroup])
async def usergroup_list(q_params: dict = Depends(query_params),
                    pool: DBPool = Depends(db_pool),
                    _user: User = Security(get_me)):
    _user.test_permission('admin:all')
    async with pool.acquire_with_log(sql_logger) as db:
        return await UserGroupDB.gets(db, **q_params)


@router.get("/{usergroup_id}", response_model=UserGroup)
async def usergroup_get(usergroup_id: int,
                        pool: DBPool = Depends(db_pool),
                        _user: User = Security(get_me)):
    _user.test_permission('admin:all')
    async with pool.acquire_with_log(sql_logger) as db:
        return await UserGroupDB.get(db, usergroup_id)


@router.put("/{usergroup_id}", response_model=UserGroup)
async def usergroup_update(usergroup_id: int, update: UserGroupUpdate,
                            pool: DBPool = Depends(db_pool),
                            _user: User = Security(get_me)):
    _user.test_permission('admin:all')
    async with pool.acquire_with_log(sql_logger) as db, db.transaction():
        return await UserGroupDB.update(db, usergroup_id, update)


@router.delete("/{usergroup_id}", status_code=status.HTTP_204_NO_CONTENT)
async def usergroup_delete(usergroup_id: int,
                           pool: DBPool = Depends(db_pool),
                           _user: User = Security(get_me)):
    _user.test_permission('admin:all')
    async with pool.acquire_with_log(sql_logger) as db, db.transaction():
        await UserGroupDB.delete(db, usergroup_id)


@router.post("/", response_model=UserGroup,
             status_code=status.HTTP_201_CREATED)
async def usergroup_create(create: UserGroupCreate,
                           pool: DBPool = Depends(db_pool),
                           _user: User = Security(get_me)):
    _user.test_permission('admin:all')
    async with pool.acquire_with_log(sql_logger) as db, db.transaction():
        return await UserGroupDB.create(db, create)

