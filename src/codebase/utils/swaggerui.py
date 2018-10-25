# pylint: disable=C0103,R0201,R0903

import os

import yaml

from bravado_core.spec import Spec
from bravado_core.validate import validate_object


class Api:

    def __init__(self):

        # TODO: eva.conf.settings.ROOT_PATH 有 bug, 显示的是 python3 的路径
        curdir = os.path.dirname(__file__)
        spec_path = os.path.join(curdir, "../../codebase/schema.yml")
        self.spec_dict = yaml.load(open(spec_path))
        self.spec = Spec.from_dict(self.spec_dict)

    def validate_object(self, object_spec, value):
        validate_object(self.spec, object_spec, value)


api = Api()
