# pylint: disable=R0903

import os
import json
import uuid
import logging

import tornado.testing

from codebase.utils.sqlalchemy import dbc
from codebase.utils.swaggerui import api
from codebase.app import make_app
from codebase.models import User
from codebase.utils.common import scrub


class Bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# ok '\033[92m\u2713\033[0m'
# \u21E8 输出 ⇨
# \u21B3 输出 ↳
# \u21E2 输出 ⇢
# \u2B91 输出 ⮑
# \u2937 输出 ⤷
# \u27F3 输出 ⟳
# \u2B51 输出 ⭑
# \u2713 输出 ✓


FIRST_ARROW = f"{Bcolors.OKGREEN}\u21E8{Bcolors.ENDC}"
SECOND_ARROW = f"{Bcolors.WARNING}\u21E2{Bcolors.ENDC}"


def validate_default_error(body):
    spec = api.spec_dict["definitions"]["DefaultErrorResponse"]
    api.validate_object(spec, body)


def get_body_json(resp):
    return scrub(json.loads(resp.body))


class BaseTestCase(tornado.testing.AsyncHTTPTestCase):

    main_title = None

    def shortDescription(self):
        class_doc = self.__doc__
        doc = self._testMethodDoc
        first = class_doc.split("\n")[0].strip() if class_doc else None
        second = doc.split("\n")[0].strip() if doc else None
        if not self.main_title:
            self.__class__.main_title = True
            return (f"\n{FIRST_ARROW} {Bcolors.BOLD}{first}{Bcolors.ENDC}\n"
                    f"  {SECOND_ARROW} {second}")
        return f"  {SECOND_ARROW} {second}"

    def get_app(self):
        os.environ["DEBUG"] = "false"
        return make_app()

    @classmethod
    def setUpClass(cls):
        # TODO: 测试开始执行一次
        # 禁止 tornado 日志，如：WARNING:tornado.access:400
        logging.getLogger('tornado.access').disabled = True
        dbc.drop_all()

    @classmethod
    def tearDownClass(cls):
        # 测试结束执行一次
        dbc.drop_all()
        # dbc.close()

    def setUp(self):
        # 每个 testcase 执行前都会执行
        super().setUp()
        dbc.create_all()

        self.current_user = User(uuid=str(uuid.uuid4()))
        self.db.add(self.current_user)
        self.db.commit()

        self.http_request_headers = {"X-User-Id": str(self.current_user.uuid)}

    def tearDown(self):
        # 每个 testcase 执行后都会执行
        super().tearDown()
        # dbc.remove()
        dbc.drop_all()

    @property
    def db(self):
        return dbc.session()

    def _api_request(self, method, url, headers=None, body=None, **kwargs):
        if not headers:
            headers = {}
        headers.update(self.http_request_headers)
        if body:
            body = json.dumps(body)
        return self.fetch(
            url, method=method, body=body, headers=headers,
            allow_nonstandard_methods=True,
            raise_error=False, **kwargs
        )

    def api_get(self, url, headers=None, **kwargs):
        return self._api_request("GET", url, headers=headers, **kwargs)

    def api_post(self, url, headers=None, body=None, **kwargs):
        return self._api_request("POST", url, headers=headers, body=body, **kwargs)

    # def api_put(self, url, headers=None, body=None, **kwargs):
    #     return self._api_request("PUT", url, headers=headers, body=body, **kwargs)

    def api_delete(self, url, headers=None, **kwargs):
        return self._api_request("DELETE", url, headers=headers, **kwargs)

    def validate_default_success(self, body):
        self.assertEqual(body["status"], "success")

    def validate_not_found(self, resp):
        body = get_body_json(resp)
        self.assertEqual(resp.code, 400)
        validate_default_error(body)

        self.assertEqual(body["status"], "not-found")
