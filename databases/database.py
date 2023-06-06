from urllib.parse import quote

from decouple import config as decouple_config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

Session = sessionmaker()


class Database(object):
    def __init__(self, name):
        adapter = decouple_config(f'{name}_ADAPTER')
        host = decouple_config(f'{name}_HOST')
        port = decouple_config(f'{name}_PORT')
        database = decouple_config(f'{name}_DATABASE')
        user = decouple_config(f'{name}_USER')
        password = decouple_config(f'{name}_PASSWORD')
        db_uri = f'{adapter}://{user}:%s@{host}:{port}/{database}' % quote(password)
        engine = create_engine(db_uri, echo=False)
        Session.configure(bind=engine)
        self.session = Session()
