import sys
from importlib import import_module

from eva.conf import settings
from eva.management.common import EvaManagementCommand

from codebase.utils.sqlalchemy import dbc


class Command(EvaManagementCommand):
    def __init__(self):
        super(Command, self).__init__()

        self.cmd = "dropdb"
        self.help = "清空数据库"

    def run(self):

        if not self.args.ignore_env_check:
            print("dropdb 只能在开发/测试环境中使用!")
            sys.exit(1)

        import_module(settings.MODELS_MODULE)
        dbc.drop_all()
