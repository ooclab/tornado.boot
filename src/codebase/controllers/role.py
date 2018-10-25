# pylint: disable=W0223,W0221,broad-except

from tornado.web import HTTPError

from codebase.web import APIRequestHandler
from codebase.models import Role
from codebase.utils.sqlalchemy.page import get_list


class RoleHandler(APIRequestHandler):

    def get(self):
        """获取角色列表
        """
        err, result, _filter = get_list(
            self,
            self.db.query(Role),
            allow_sort_by=["id", "created", "name"],
            model=Role,
        )
        if err:
            self.fail(err)
            return

        self.success(**{"data": [x.isimple for x in result], "filter": _filter})

    def post(self):
        """创建角色
        """
        body = self.get_body_json()

        role = self.db.query(Role).filter_by(name=body["name"]).first()
        if role:
            self.fail("name-exist")
            return

        role = Role(
            name=body["name"],
            summary=body.get("summary"),
            description=body.get("description"),
        )
        self.db.add(role)
        self.db.commit()
        self.success(id=str(role.uuid))


class _BaseSingleRoleHandler(APIRequestHandler):

    def get_role(self, _id):
        role = self.db.query(Role).filter_by(uuid=_id).first()
        if role:
            return role
        raise HTTPError(400, reason="not-found")


class SingleRoleHandler(_BaseSingleRoleHandler):

    def get(self, _id):
        """获取角色详情
        """
        role = self.get_role(_id)
        self.success(data=role.ifull)

    def post(self, _id):
        """更新角色属性
        """
        role = self.get_role(_id)
        body = self.get_body_json()
        role.update(**body)
        self.db.commit()
        self.success()

    def delete(self, _id):
        """删除角色
        """
        role = self.get_role(_id)
        # TODO: how to rollback ?
        self._remove_role(role)
        self.success()

    def _remove_role(self, role):
        # 删除 User 依赖
        # role.users = []

        # 删除 Permission 依赖
        # TODO: 是否需要删除没有任何 Role 关联的 Permission ?
        role.permissions = []

        # 删除自身
        self.db.delete(role)

        self.db.commit()
