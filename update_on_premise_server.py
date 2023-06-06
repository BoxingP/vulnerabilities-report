import sys

import pandas as pd

from databases.vul_database import VulDatabase

if len(sys.argv) < 2:
    print("Please provide the config file path as an argument.")
    sys.exit(1)
data_file = sys.argv[1]
data_sheet = 'ServerList'

dfs = pd.read_excel(data_file, sheet_name=[data_sheet])
df = dfs[data_sheet]
values = df[['Name', 'Infra Lookup(Contact)']].values.tolist()
vul_database = VulDatabase()
for value in values:
    vul_database.insert_on_premise_server_info(value[0], value[1])
