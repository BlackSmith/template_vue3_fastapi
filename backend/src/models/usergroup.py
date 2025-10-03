from datetime import datetime
from typing import Annotated, Optional, Set

from pydantic import BeforeValidator
from libs.db import DBConnection, Connection
from libs.helpers import str2set
from config import get_config
from models.base import BaseDBModel, BaseModel, Field, Connection

KEYCLOAK_REALM_ADMIN_ROLE = get_config('KEYCLOAK_REALM_ADMIN_ROLE')


class UserGroup(BaseModel):
    id: int
    name: str = Field(max_length=75)
    permissions: Annotated[Set[str], BeforeValidator(str2set)] = Field(default_factory=set)
    description: Optional[str] = Field(None, max_length=75)
    realm_role: Optional[str] = Field(None, max_length=75)
    is_default: Optional[bool] = Field(default=False)
    is_assignable: bool = Field(default=True)
    is_readonly: Optional[bool] = Field(default=False)
    created_at: Optional[datetime] = Field(default=None)


class UserGroupUpdate(BaseModel):
    name: str = Field( max_length=75)
    description: Optional[str] = Field(None, max_length=75)
    realm_role: Optional[str] = Field(None, max_length=75)
    permissions: set[str] = Field(default_factory=set,
                                  json_schema_extra={"no_save": True})


class UserGroupCreate(UserGroupUpdate):
    pass


# Database model class with asyncpg integration
class UserGroupDB(BaseDBModel):

    class Meta:
        db_table = 'usergroup'
        PYDANTIC_CLASS = UserGroup
        DEFAULT_SORT_BY: str = 'name'
        sub_columns = '''
            COALESCE(JSON_AGG(DISTINCT p.name) FILTER (WHERE p.name IS NOT NULL),'[]') as permissions
        '''
        sub_sql = 'LEFT JOIN "usergroup_permissions" p ON p.usergroup_id = f.id'
        group_by = ['f.id']

    @DBConnection.register_startup
    @staticmethod
    async def init(db: Connection):
        await db.execute('UPDATE "usergroup" SET realm_role = $1 WHERE name = $2',
                         KEYCLOAK_REALM_ADMIN_ROLE, 'Admins')

    @classmethod
    async def assign_usergroups_to_user(cls, db: Connection, user, usergroups: Set[int]):
        usergroups_obj = await db.fetch(
            'SELECT id FROM "usergroup" WHERE id = ANY($1::int[]) AND is_assignable = true',
            list(usergroups)
        )
        ugs = [ug['id'] for ug in usergroups_obj]
        vals = [(ug, user) for ug in ugs]
        await db.executemany('''
            INSERT INTO "usergroup_user" ("usergroup_id", "user_id")
            VALUES ($1, $2)
            ON CONFLICT ("usergroup_id", "user_id") DO NOTHING;
        ''', vals)

        await db.execute('''
            DELETE FROM "usergroup_user" WHERE "user_id" = $1 AND
                "usergroup_id" != ALL($2::int[]);
        ''', user, ugs)
        usergroups.clear()
        usergroups.update(ugs)
