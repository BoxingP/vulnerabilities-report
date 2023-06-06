import datetime

from sqlalchemy import Column, Integer, String, Time, ForeignKey
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


class VulnerabilitiesStatistic(Base):
    __tablename__ = 'vulnerabilities_statistic'
    id = Column(Integer, primary_key=True, nullable=False)
    server_id = Column(Integer, ForeignKey('on_premise_server.id'))
    severity_1 = Column(Integer, nullable=True)
    severity_2 = Column(Integer, nullable=True)
    severity_3 = Column(Integer, nullable=True)
    severity_4 = Column(Integer, nullable=True)
    severity_5 = Column(Integer, nullable=True)
    updated_time = Column(Time, default=datetime.datetime.utcnow() + datetime.timedelta(hours=8), nullable=True)
