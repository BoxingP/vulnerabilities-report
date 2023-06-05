import os
import re
import sys

import pandas as pd
import psycopg2

from emails.emails import Emails


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
    connection = psycopg2.connect(
        host="",
        database="",
        port="",
        user="",
        password=""
    )
    query = "SELECT server_name, it_contact FROM on_premise_server"
    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()
    results = []
    for row in rows:
        result = {
            'server_name': row[0],
            'it_contact': row[1]
        }
        results.append(result)
    connection.close()
    return results


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
        "contact_email": it_contact,
        "report_path": file_path,
        "vulnerabilities_severity": [
            {"level": severity, "total": count}
            for severity, count in severity_counts.items()
        ]
    }
    if it_contact:
        Emails().send_email(summary)
