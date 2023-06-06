from urllib.parse import quote

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

Session = sessionmaker()


class Database(object):
    def __init__(self):
        adapter = 'postgresql+psycopg2'
        host = ''
        port = ''
        database = ''
        user = ''
        password = ''
        db_uri = f'{adapter}://{user}:%s@{host}:{port}/{database}' % quote(password)
        engine = create_engine(db_uri, echo=False)
        Session.configure(bind=engine)
        self.session = Session()
