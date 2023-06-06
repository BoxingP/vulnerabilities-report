import datetime

from sqlalchemy import Column, Integer, String, Time
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class OnPremiseServer(Base):
    __tablename__ = 'on_premise_server'
    id = Column(Integer, primary_key=True, nullable=False)
    server_name = Column(String, nullable=True)
    application_name = Column(String, nullable=True)
    os_info = Column(String, nullable=True)
    it_contact = Column(String, nullable=True)
    updated_time = Column(Time, default=datetime.datetime.utcnow() + datetime.timedelta(hours=8), nullable=True)
