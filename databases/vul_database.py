import datetime

from sqlalchemy import func, exc

from databases.database import Database
from databases.database_schema import OnPremiseServer, VulnerabilitiesStatistic


class VulDatabase(Database):
    def __init__(self, name):
        super(VulDatabase, self).__init__(name)

    def insert_on_premise_server_info(self, name, contact):
        new_server_info = OnPremiseServer(
            server_name=name,
            it_contact=contact
        )
        self.session.add(new_server_info)
        self.session.commit()

    def get_on_premise_server_contact(self):
        results = self.session.query(OnPremiseServer.server_name, OnPremiseServer.it_contact).all()
        data = [{'server_name': server_name, 'it_contact': it_contact} for server_name, it_contact in results]
        return data

    def insert_or_update_vulnerabilities_statistic(self, data):
        server_name = data['server_name'].lower()
        query = self.session.query(OnPremiseServer.id).filter(
            func.lower(OnPremiseServer.server_name).ilike(server_name))
        server_id = query.scalar()
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
            severity_5=severity_5
        )
        try:
            self.session.add(vulnerabilities_statistic)
            self.session.commit()
        except exc.IntegrityError as e:
            self.session.rollback()
            existing_statistic = self.session.query(VulnerabilitiesStatistic).filter_by(
                server_id=server_id).one_or_none()
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
