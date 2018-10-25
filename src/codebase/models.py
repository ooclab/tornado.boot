# pylint: disable=R0902,E1101,W0201,too-few-public-methods,W0613

import datetime
import uuid

from sqlalchemy_utils import UUIDType
from eva.conf import settings
from eva.utils.time_ import utc_rfc3339_string
from sqlalchemy import (
    event,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Sequence,
    String,
    Table,
    Text,
)
from sqlalchemy.orm import relationship

from codebase.utils.sqlalchemy import ORMBase, dbc


_USER_ROLES = Table(
    "authz_user__role",
    ORMBase.metadata,
    Column("user_id", Integer, ForeignKey("authz_user.id")),
    Column("role_id", Integer, ForeignKey("authz_role.id")),
)


_ROLE_PERMISSIONS = Table(
    "authz_role__permission",
    ORMBase.metadata,
    Column("role_id", Integer, ForeignKey("authz_role.id")),
    Column("permission_id", Integer, ForeignKey("authz_permission.id")),
)


class SimilarBase:

    def update(self, **kwargs):
        length = len(kwargs)
        if "summary" in kwargs:
            self.summary = kwargs.pop("summary")
        if "description" in kwargs:
            self.description = kwargs.pop("description")
        if len(kwargs) != length:
            self.updated = datetime.datetime.utcnow()

    @property
    def isimple(self):
        return {"id": str(self.uuid), "name": self.name, "summary": self.summary}

    @property
    def ifull(self):
        return {
            "id": str(self.uuid),
            "name": self.name,
            "summary": self.summary,
            "description": self.description,
            "updated": utc_rfc3339_string(self.updated),
            "created": utc_rfc3339_string(self.created),
        }


class Role(ORMBase, SimilarBase):
    """
    角色与一组权限绑定，用户可以属于多个角色。
    """

    __tablename__ = "authz_role"

    id = Column(Integer, Sequence("authz_role_id_seq"), primary_key=True)
    uuid = Column(UUIDType(), default=uuid.uuid4, unique=True)
    name = Column(String(128), unique=True)
    summary = Column(String(1024))
    description = Column(Text)
    updated = Column(DateTime(), default=datetime.datetime.utcnow)
    created = Column(DateTime(), default=datetime.datetime.utcnow)

    permissions = relationship(
        "Permission", secondary=_ROLE_PERMISSIONS, backref="roles"
    )


class Permission(ORMBase, SimilarBase):
    """
    提供“标识“，判断用户是否拥有某个“权限”
    """

    __tablename__ = "authz_permission"

    id = Column(Integer, Sequence("authz_permission_id_seq"), primary_key=True)
    uuid = Column(UUIDType(), default=uuid.uuid4, unique=True)
    name = Column(String(512), unique=True)
    summary = Column(String(1024))
    description = Column(Text)
    updated = Column(DateTime(), default=datetime.datetime.utcnow)
    created = Column(DateTime(), default=datetime.datetime.utcnow)


class User(ORMBase):
    """
    用户由 AuthN 服务创建并鉴别，本处存储仅是为了关系映射方便

    1. uuid 作为用户 ID 不宜放在其他关联表中，而应该使用 Integer 主键
    2. SQLAlchemy 可以提供方便的查询
    """

    __tablename__ = "authz_user"

    id = Column(Integer, Sequence("authz_user_id_seq"), primary_key=True)
    # TODO: 虽然我们这里认为 user id 是 uuid，当实际情况不一定是
    # 这里可以考虑根据用户配置，动态创建 uid 项，而不是强制使用 uuid
    uuid = Column(UUIDType(), unique=True)
    created = Column(DateTime(), default=datetime.datetime.utcnow)

    roles = relationship("Role", secondary=_USER_ROLES, backref="users")


# 第一次创建 Role 表时创建一些默认角色
@event.listens_for(Role.__table__, 'after_create')
def insert_initial_roles(*args, **kwargs):
    db = dbc.session()
    db.add(Role(name=settings.ADMIN_ROLE_NAME))
    db.add(Role(name='anonymous'))
    db.add(Role(name='authenticated'))
    db.commit()
