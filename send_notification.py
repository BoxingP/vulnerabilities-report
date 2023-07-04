import datetime
import os
import re
from pathlib import Path

from decouple import config as decouple_config

from databases.vul_database import VulDatabase
from emails.emails import Emails


def format_contact(contact):
    values = re.split(r'[;\n]', contact)
    return [value.strip() for value in values if re.match(r'[^@\s]+@[^@\s]+\.[^@\s]+', value)]


def generate_server_contact(contacts, files):
    for contact in contacts:
        server_name = contact['server_name'].upper()
        matching_paths = [path for path in files if server_name in path.upper()]
        if matching_paths:
            contact['report_path'] = matching_paths[0]
        else:
            contact['report_path'] = None
    return contacts


def get_report_path(parent_folder):
    current_date = datetime.datetime.now().date()
    current_month = current_date.strftime('%Y%m')
    files_in_folder = []
    for folder in os.listdir(parent_folder):
        folder_path = Path(parent_folder, folder)
        if folder.startswith(current_month):
            for file in os.listdir(folder_path):
                file_path = str(Path(folder_path, file))
                files_in_folder.append(file_path)
    return files_in_folder


vul_database = VulDatabase('VUL_DATABASE')
server_contacts = vul_database.get_on_premise_server_contact()
output_directory = Path('/', *decouple_config('OUTPUT_DIRECTORY', cast=lambda x: x.split(','))).resolve().absolute()
report_path = get_report_path(output_directory)
server_contacts = generate_server_contact(server_contacts, report_path)
for server_contact in server_contacts:
    if server_contact['contact_email'] is not None and server_contact['report_path'] is not None:
        server_contact['contact_email'] = format_contact(server_contact['contact_email'])
        if server_contact['contact_email']:
            server_contact['vulnerabilities_severity'] = vul_database.get_vulnerabilities_statistic(
                server_contact['server_name'], datetime.datetime.now().year, datetime.datetime.now().month)
            Emails().send_email(server_contact)
