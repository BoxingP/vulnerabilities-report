from databases.database import Database
from databases.database_schema import OnPremiseServer


class VulDatabase(Database):
    def __init__(self):
        super(VulDatabase, self).__init__()

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
