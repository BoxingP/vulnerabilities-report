import os
import re
import sys

import pandas as pd


def format_name(string):
    pattern = r'^([a-zA-Z0-9-]+).*'
    match = re.match(pattern, string)
    if match:
        formatted_string = match.group(1).upper()
        return formatted_string
    return string


if len(sys.argv) < 2:
    print("Please provide the report file path as an argument.")
    sys.exit(1)
data_file = sys.argv[1]
output_directory = os.path.abspath(os.sep.join([os.path.abspath(os.sep), 'tmp', 'qualys-reports']))
if not os.path.exists(output_directory):
    os.makedirs(output_directory)
excel_file = pd.ExcelFile(data_file)
sheet_names = excel_file.sheet_names
for name in sheet_names:
    if re.search(r'(.*China_\d+)', name):
        data_sheet = name
        break

dfs = pd.read_excel(data_file, sheet_name=[data_sheet])
df = dfs[data_sheet]

groups = df.groupby('Asset Name')
for name, group in groups:
    file_name = f'{format_name(name)}.xlsx'
    file_path = os.path.join(output_directory, file_name)
    group.to_excel(file_path, index=False)
