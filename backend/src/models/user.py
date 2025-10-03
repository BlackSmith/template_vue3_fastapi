
from loggate import get_logger
from pydantic import BeforeValidator, Field
from datetime import datetime
from typing import Annotated, Optional, Set

from models.usergroup import UserGroupDB
from models import Forbidden, ObjectNotFound
from config import get_config
from libs.helpers import str2set
from models.base import BaseDBModel, BasePModel, BaseModel, Connection, C, G

KEYCLOAK_REALM_ADMIN_ROLE = get_config('KEYCLOAK_REALM_ADMIN_ROLE')

logger = get_logger('user')

class User(BasePModel):
    id: int
    name: str
    email: str
    created_at: Optional[datetime]
    last_logged_at: Optional[datetime]
    last_realm_roles: Optional[str]
    permissions: Annotated[Set[str], BeforeValidator(str2set)] = Field(default_factory=set)
    member_of_static_ids: Annotated[Set[int], BeforeValidator(str2set)] = Field(default_factory=set)
    member_of_dynamic_ids: Annotated[Set[int], BeforeValidator(str2set)] = Field(default_factory=set)
    disabled: Optional[bool] = Field(None)

    def can(self, permission: str|None = None) -> bool:
        return permission in self.permissions

    def test_permission(self, permission: str|None = None):
        # if not permission:
        #     permission = str(inspect.stack()[1].function).replace('_', ':')
        if not self.can(permission):
            logger.error(f'User {self.name} does not have permission {permission}')
            raise Forbidden(
                f'You do not have permission "{permission}" '
                f'to perform this operation.'
            )


class UserInternalUpdate(BaseModel):
    last_logged_at: datetime
    last_realm_roles: Optional[str]
    disabled: Optional[bool] = Field(None)


class UserUpdate(BaseModel):
    name: str = Field(max_length=75)
    email: str = Field(max_length=50)
    member_of_static_ids: Optional[Set[int]] = Field(default_factory=set,
                                                     json_schema_extra={"no_save": True})


class UserCreate(UserUpdate):
    pass

# Database model class with asyncpg integration
class UserDB(BaseDBModel):
    class Meta:
        db_table = 'user'
        PYDANTIC_CLASS = User
        DEFAULT_SORT_BY: str = 'name'
        sub_columns = '''
            COALESCE(JSON_AGG(DISTINCT ug."id") FILTER (WHERE ug."id" IS NOT NULL),'[]') AS member_of_static_ids,
            COALESCE(JSON_AGG(DISTINCT ugd."id") FILTER (WHERE ugd."id" IS NOT NULL),'[]') AS member_of_dynamic_ids,
            COALESCE(JSON_AGG(DISTINCT p.name) FILTER (WHERE p.name IS NOT NULL),'[]') AS permissions
        '''
        sub_sql = '''
            LEFT JOIN "usergroup_user" u ON u.user_id = f.id
            LEFT JOIN "usergroup" ug ON ug."id" = u."usergroup_id"
            LEFT JOIN "usergroup" ugd ON ugd."realm_role" = ANY(string_to_array(f.last_realm_roles, ','))
            LEFT JOIN "usergroup_permissions" p ON p."usergroup_id" = ug."id" OR p."usergroup_id" = ugd."id"
        '''
        group_by = ['f.id']

    @classmethod
    async def get_identity(cls, db: Connection, query: str | int | User, *args, **kwargs) -> Optional[User]:
        if isinstance(query, cls.Meta.PYDANTIC_CLASS):
            return query
        if isinstance(query, int) and len(args) == 0:
            args = [query]
            query = 'f."id"=$2'
        if row := await db.fetchrow(f'''
                SELECT
                    f.*,
                    COALESCE(JSON_AGG(DISTINCT ug."id") FILTER (WHERE ug."id" IS NOT NULL),'[]') AS member_of_static_ids,
                    COALESCE(JSON_AGG(DISTINCT ugd."id") FILTER (WHERE ugd."id" IS NOT NULL),'[]') AS member_of_dynamic_ids,
                    COALESCE(JSON_AGG(DISTINCT ug_p.name) FILTER (WHERE ug_p.name IS NOT NULL),'[]') AS permissions
                FROM "user" f
                LEFT JOIN "usergroup_user" ug_u ON ug_u."user_id" = f."id"
                LEFT JOIN "usergroup" ug ON ug."id" = ug_u."usergroup_id"
                LEFT JOIN "usergroup" ugd ON ugd."realm_role" = ANY($1::text[])
                LEFT JOIN "usergroup_permissions" ug_p ON ug_p."usergroup_id" = ug."id" OR ug_p."usergroup_id" = ugd."id"
                WHERE {query}
                GROUP BY f.id;
            ''',
            kwargs.get('realm_roles', []),
            *args
        ):
            res = cls.get_object(cls.Meta.PYDANTIC_CLASS, row)
            return res
        else:
            raise ObjectNotFound(
                f'Object {cls.__name__} not found: {query} {args}.'
            )

    @classmethod
    async def pre_update(cls, db: Connection, user: User, update: UserUpdate, **kwargs):
        if hasattr(update, "member_of_static_ids"):
            await UserGroupDB.assign_usergroups_to_user(db, user, update.member_of_static_ids)
