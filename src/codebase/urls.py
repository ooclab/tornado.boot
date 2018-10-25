from tornado.web import url

from codebase.controllers import (
    default,
    role
)


HANDLERS = [
    url(r"/",
        default.SpecHandler),

    url(r"/_health",
        default.HealthHandler),

    # Role

    url(r"/role",
        role.RoleHandler),

    url(r"/role/"
        r"([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})",
        role.SingleRoleHandler),
]
