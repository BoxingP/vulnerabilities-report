import os
import re
from pathlib import Path

import pandas as pd
from decouple import config as decouple_config

from databases.vul_database import VulDatabase


def format_name(string):
    pattern = r'^([a-zA-Z0-9-]+).*'
    match = re.match(pattern, string)
    if match:
        formatted_string = match.group(1).upper()
        return formatted_string
    return string


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


def create_output_directory():
    directory = Path('/', *decouple_config('OUTPUT_DIRECTORY', cast=lambda x: x.split(','))).resolve().absolute()
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def get_qualys_reports(path):
    files = path.glob('*.xlsx')
    return [file.absolute() for file in files]


reports_directory = Path('/', *decouple_config('REPORT_DIRECTORY', cast=lambda x: x.split(','))).resolve().absolute()
output_directory = create_output_directory()
reports = get_qualys_reports(reports_directory)
vul_database = VulDatabase('VUL_DATABASE')
for report in reports:
    date = get_date_from_filename(str(report))
    excel_file = pd.ExcelFile(report)
    sheet_names = excel_file.sheet_names
    for name in sheet_names:
        if re.search(r'(.*China_\d+)', name):
            data_sheet = name
            break

    dfs = pd.read_excel(report, sheet_name=[data_sheet])
    df = dfs[data_sheet]

    groups = df.groupby('Asset Name')
    details = []
    for name, group in groups:
        server_name = format_name(name)
        file_name = f'{server_name}.xlsx'
        file_directory_path = Path(output_directory, f'{date[0]}{date[1]}{date[2]}')
        os.makedirs(file_directory_path, exist_ok=True)
        file_path = str(Path(file_directory_path, file_name).absolute())
        group.to_excel(file_path, index=False)
        severity_counts = group['Severity'].value_counts().to_dict()
        detail = {
            "server_name": server_name,
            "year": date[0],
            "month": date[1],
            "day": date[2],
            "vulnerabilities_severity": [
                {"level": severity, "total": count}
                for severity, count in severity_counts.items()
            ]
        }
        details.append(detail)

    for detail in details:
        vul_database.insert_or_update_vulnerabilities_statistic(detail)
