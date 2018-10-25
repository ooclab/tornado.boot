# pylint: disable=R0201

from importlib import import_module

from eva.conf import settings
from eva.management.common import EvaManagementCommand

from codebase.utils.sqlalchemy import dbc


class Command(EvaManagementCommand):
    def __init__(self):
        super(Command, self).__init__()

        self.cmd = "syncdb"
        self.help = "同步数据库(如果表不存在，则创建之)"

    def run(self):
        import_module(settings.MODELS_MODULE)
        dbc.create_all()
