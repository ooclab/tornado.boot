from yaml import safe_load
from swagger_spec_validator.util import get_validator

from .base import BaseTestCase


class HealthTestCase(BaseTestCase):
    """GET /_health - 健康检查
    """

    def test_health(self):
        """返回正确
        """

        resp = self.fetch("/_health")
        self.assertEqual(resp.code, 200)
        self.assertEqual(resp.body, b"ok")


class SpecTestCase(BaseTestCase):
    """GET /_spec - SwaggerUI 文档
    """

    def test_spec(self):
        """返回正确
        """

        resp = self.fetch("/_spec")
        self.assertEqual(resp.code, 200)

    def test_validate_swaggerui(self):
        """验证 SwaggerUI 文档是否有效
        """
        resp = self.fetch("/_spec")
        spec_json = safe_load(resp.body)
        validator = get_validator(spec_json)
        validator.validate_spec(spec_json)
