# pylint: disable=W0511,C0111,C0103
"""SQLAlchemy Help Method
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from eva.conf import settings


ORMBase = declarative_base()


class DBC:
    """DB Connection

    http://docs.sqlalchemy.org/en/latest/orm/contextual.html
    http://docs.sqlalchemy.org/en/latest/orm/session_basics.html#session-faq-whentocreate
    """

    def __init__(self):
        self.db_uri = settings.DB_URI
        self.dbengine = create_engine(self.db_uri, echo=False)
        session_factory = sessionmaker(bind=self.dbengine)
        self.session = scoped_session(session_factory)

    def remove(self):
        self.session.remove()

    def create_all(self):
        # TODO: session.remove() 保证不会死锁
        self.session.remove()
        ORMBase.metadata.create_all(self.dbengine)

    def drop_all(self):
        # TODO: session.remove() 保证不会死锁
        self.session.remove()
        ORMBase.metadata.drop_all(self.dbengine)


dbc = DBC()
