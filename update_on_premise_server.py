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
    vul_database.insert_on_premise_server_info(value[0], value[1], value[2], value[3], 'terry ye list')
