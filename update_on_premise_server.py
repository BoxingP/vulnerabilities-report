import os

import pandas as pd

from databases.vul_database import VulDatabase

terry_list = os.path.join(os.path.dirname(__file__), 'terry_ye_list.xlsx')
terry_list_data_sheet = 'ServerList'

dfs = pd.read_excel(terry_list, sheet_name=[terry_list_data_sheet])
df = dfs[terry_list_data_sheet]
values = df[['Name', 'Infra Lookup', 'Infra Lookup(Contact)', 'OS Name']].values.tolist()
vul_database = VulDatabase('VUL_DATABASE')
for value in values:
    vul_database.insert_or_update_on_premise_server_info(
        name=value[0], application_name=value[1], it_contact=value[2], os_info=value[3], updated_by='terry ye list')

benson_list = os.path.join(os.path.dirname(__file__), 'benson_wang_list.xlsx')
benson_list_data_sheet = 'Sheet1'
dfs = pd.read_excel(benson_list, sheet_name=[benson_list_data_sheet])
df = dfs[benson_list_data_sheet]
values = df[['Server Name', 'IP Address', 'Application Usage', 'Environment', 'Owner', 'OS']].values.tolist()
vul_database = VulDatabase('VUL_DATABASE')
for value in values:
    vul_database.insert_or_update_on_premise_server_info(
        name=value[0], ip_address=value[1], application_name=value[2], environment=value[3], it_contact=value[4],
        os_info=value[5], updated_by='benson wang list')
