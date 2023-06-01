import sys

import pandas as pd
import psycopg2
from psycopg2 import extras

if len(sys.argv) < 2:
    print("Please provide the config file path as an argument.")
    sys.exit(1)
data_file = sys.argv[1]
data_sheet = 'ServerList'

dfs = pd.read_excel(data_file, sheet_name=[data_sheet])
df = dfs[data_sheet]
values = df[['Name', 'Infra Lookup(Contact)']].values.tolist()

connection = psycopg2.connect(
    host="",
    database="",
    port="",
    user="",
    password=""
)
query = "INSERT INTO on_premise_server (server_name, it_contact) VALUES %s"
with connection.cursor() as cursor:
    extras.execute_values(cursor, query, values)
connection.commit()
connection.close()
