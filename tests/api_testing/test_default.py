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
    """GET / - SwaggerUI 文档
    """

    def test_spec(self):
        """返回正确
        """

        resp = self.fetch("/")
        self.assertEqual(resp.code, 200)
