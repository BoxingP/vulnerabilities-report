import os
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from decouple import config as decouple_config


class Emails(object):
    def __init__(self):
        self.smtp_server = decouple_config('SMTP_SERVER')
        self.port = decouple_config('SMTP_PORT', cast=int)
        self.sender_email = decouple_config('EMAIL_SENDER')
        self.subject = decouple_config('EMAIL_SUBJECT')
        with open(os.path.join(os.path.dirname(__file__), 'logo.png'), 'rb') as file:
            self.logo_img = file.read()
        with open(os.path.join(os.path.dirname(__file__), 'email_template.html'), 'r', encoding='UTF-8') as file:
            self.html = file.read()

    def extract_names(self, email_list):
        names = [email.split('@')[0] for email in email_list]
        names = [name.split('.')[0].capitalize() for name in names]
        if len(names) == 1:
            return names[0]
        elif len(names) == 2:
            return names[0] + ' and ' + names[1]
        else:
            return ', '.join(names[:-1]) + ', and ' + names[-1]

    def send_email(self, data):
        message = MIMEMultipart("alternative")
        message["Subject"] = self.subject
        message["From"] = self.sender_email
        message["To"] = ",".join(data['contact_email'])
        html_part = MIMEMultipart("related")
        first_names = self.extract_names(data['contact_email'])
        self.html = self.html.replace('${FIRST_NAME}', first_names)
        severity_totals = {
            item['level']: item['total']
            for item in data['vulnerabilities_severity']
        }
        self.html = self.html.replace('${CRITICAL_NUMBER}', str(severity_totals.get(5, 0)))
        self.html = self.html.replace('${HIGH_NUMBER}', str(severity_totals.get(4, 0)))
        html_part.attach(MIMEText(self.html, "html"))
        logo_image = MIMEImage(self.logo_img)
        logo_image.add_header('Content-ID', '<logo>')
        html_part.attach(logo_image)
        message.attach(html_part)

        with open(data['report_path'], 'rb') as attachment:
            attachment_obj = MIMEBase('application', 'octet-stream')
            attachment_obj.set_payload(attachment.read())
        encoders.encode_base64(attachment_obj)
        attachment_obj.add_header('Content-Disposition', f"attachment; filename= {data['server_name']}.xlsx")
        message.attach(attachment_obj)

        with smtplib.SMTP(self.smtp_server, self.port) as server:
            server.sendmail(from_addr=self.sender_email, to_addrs=data['contact_email'], msg=message.as_string())
