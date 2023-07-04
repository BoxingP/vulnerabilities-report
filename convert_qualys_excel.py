import os
import re
import sys

import pandas as pd

from databases.vul_database import VulDatabase
from emails.emails import Emails


def store_vulnerabilities_statistic(data):
    vul_database = VulDatabase('VUL_DATABASE')
    vul_database.insert_or_update_vulnerabilities_statistic(data)


def format_emails(contacts):
    values = re.split(r'[;\n]', contacts)
    emails = [value.strip() for value in values if re.match(r'[^@\s]+@[^@\s]+\.[^@\s]+', value)]
    return emails


def get_it_contact(server_list, server_name):
    for server in server_list:
        if server['server_name'].upper() == server_name.upper():
            return format_emails(server['it_contact'])
    return []


def get_server_contact():
    vul_database = VulDatabase('VUL_DATABASE')
    return vul_database.get_on_premise_server_contact()


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


def get_date_from_filename(file):
    pattern = r'(\d{4})(\d{2})(\d{2})'
    match = re.search(pattern, file)
    if match:
        year = match.group(1)
        month = match.group(2)
        day = match.group(3)
    else:
        year = ''
        month = ''
        day = ''
    return year, month, day


date = get_date_from_filename(data_file)
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

server_contact = get_server_contact()

groups = df.groupby('Asset Name')
for name, group in groups:
    server_name = format_name(name)
    file_name = f'{server_name}.xlsx'
    it_contact = get_it_contact(server_contact, server_name)
    file_path = os.path.join(output_directory, file_name)
    group.to_excel(file_path, index=False)
    severity_counts = group['Severity'].value_counts().to_dict()

    summary = {
        "server_name": server_name,
        "year": date[0],
        "month": date[1],
        "day": date[2],
        "contact_email": it_contact,
        "report_path": file_path,
        "vulnerabilities_severity": [
            {"level": severity, "total": count}
            for severity, count in severity_counts.items()
        ]
    }
    store_vulnerabilities_statistic(summary)
    if it_contact:
        Emails().send_email(summary)
