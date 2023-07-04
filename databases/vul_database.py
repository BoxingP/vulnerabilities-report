import datetime

from sqlalchemy import func, exc, update, or_

from databases.database import Database
from databases.database_schema import OnPremiseServer, VulnerabilitiesStatistic


class VulDatabase(Database):
    def __init__(self, name):
        super(VulDatabase, self).__init__(name)

    def update_column(self, server_id, column_name, new_value, updated_by):
        current_value = self.session.query(getattr(OnPremiseServer, column_name)).filter(
            OnPremiseServer.id == server_id).scalar()
        if current_value is None or current_value == 'NaN' or (
                column_name == 'it_contact' and '@' not in current_value):
            query = update(OnPremiseServer).where(OnPremiseServer.id == server_id).values(
                **{column_name: new_value}, updated_by=updated_by,
                updated_time=datetime.datetime.utcnow() + datetime.timedelta(hours=8))
            self.session.execute(query)
            self.session.commit()

    def insert_on_premise_server_info(self, name, ip_address=None, application_name=None, environment=None,
                                      it_contact=None, os_info=None, updated_by=None):
        new_server_info = OnPremiseServer(
            server_name=name,
            ip_address=ip_address,
            application_name=application_name,
            environment=environment,
            it_contact=it_contact,
            os_info=os_info,
            updated_by=updated_by,
            updated_time=datetime.datetime.utcnow() + datetime.timedelta(hours=8)
        )
        self.session.add(new_server_info)
        self.session.commit()

    def insert_or_update_on_premise_server_info(self, name, ip_address=None, application_name=None, environment=None,
                                                it_contact=None, os_info=None, updated_by=None):
        server_name = name.lower()
        query = self.session.query(OnPremiseServer.id).filter(
            func.lower(OnPremiseServer.server_name).ilike(server_name))
        server_id = query.scalar()
        if server_id is None:
            self.insert_on_premise_server_info(name=name, ip_address=ip_address, application_name=application_name,
                                               environment=environment, it_contact=it_contact, os_info=os_info,
                                               updated_by=updated_by)
        else:
            self.update_column(server_id, 'ip_address', ip_address, updated_by)
            self.update_column(server_id, 'application_name', application_name, updated_by)
            self.update_column(server_id, 'environment', environment, updated_by)
            self.update_column(server_id, 'it_contact', it_contact, updated_by)
            self.update_column(server_id, 'os_info', os_info, updated_by)

    def get_on_premise_server_contact(self):
        results = self.session.query(OnPremiseServer.server_name, OnPremiseServer.it_contact).all()
        data = [{'server_name': server_name, 'it_contact': it_contact} for server_name, it_contact in results]
        return data

    def insert_or_update_vulnerabilities_statistic(self, data):
        server_name = data['server_name'].lower()
        query = self.session.query(OnPremiseServer.id).filter(
            func.lower(OnPremiseServer.server_name).ilike(server_name))
        server_id = query.scalar()
        if server_id is None:
            print(f"{server_name} related information does not exist.")
            return
        year = data['year']
        month = data['month']
        day = data['day']
        severity_1 = severity_2 = severity_3 = severity_4 = severity_5 = 0
        for severity_data in data['vulnerabilities_severity']:
            level = severity_data['level']
            total = severity_data['total']
            if level == 1:
                severity_1 = total
            elif level == 2:
                severity_2 = total
            elif level == 3:
                severity_3 = total
            elif level == 4:
                severity_4 = total
            elif level == 5:
                severity_5 = total
        vulnerabilities_statistic = VulnerabilitiesStatistic(
            server_id=server_id,
            severity_1=severity_1,
            severity_2=severity_2,
            severity_3=severity_3,
            severity_4=severity_4,
            severity_5=severity_5,
            year=year,
            month=month,
            day=day
        )
        try:
            self.session.add(vulnerabilities_statistic)
            self.session.commit()
        except exc.IntegrityError as e:
            self.session.rollback()
            existing_statistic = self.session.query(VulnerabilitiesStatistic).filter_by(
                server_id=server_id, year=year, month=month, day=day).one_or_none()
            if existing_statistic is not None:
                existing_statistic.severity_1 = severity_1
                existing_statistic.severity_2 = severity_2
                existing_statistic.severity_3 = severity_3
                existing_statistic.severity_4 = severity_4
                existing_statistic.severity_5 = severity_5
                existing_statistic.updated_time = datetime.datetime.utcnow() + datetime.timedelta(hours=8)
                self.session.commit()
                self.session.refresh(existing_statistic)
            else:
                print("An error occurred during the insert or update vulnerabilities statistic:", str(e))

    def update_server_name_to_uppercase(self):
        stmt = update(OnPremiseServer).values(server_name=func.upper(OnPremiseServer.server_name))
        self.session.execute(stmt)
        self.session.commit()

    def remove_meaningless_server(self, servers):
        query = self.session.query(OnPremiseServer).filter(
            or_(*(OnPremiseServer.server_name.ilike(server) for server in servers))
        )
        query.delete(synchronize_session=False)
        self.session.commit()
        self.session.close()

    def replace_empty_to_null(self):
        column_names = ['application_name', 'it_contact', 'os_info']
        for column_name in column_names:
            query = update(OnPremiseServer).where(getattr(OnPremiseServer, column_name) == 'NaN').values(
                **{column_name: None})
            self.session.execute(query)
        self.session.commit()
