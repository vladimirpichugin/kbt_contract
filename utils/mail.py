# -*- coding: utf-8 -*-
# Author: Vladimir Pichugin <vladimir@pichug.in>
import smtplib
import time
import datetime
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email import utils as email_utils

from .data import MessageDeliveryReport
from .helpers import parse_header_feedback_id

from settings import Settings


class Mail:
    @staticmethod
    def get_mail_client() -> smtplib.SMTP_SSL:
        ssl_context = ssl.create_default_context(
            purpose=ssl.Purpose.CLIENT_AUTH,
            cafile=Settings.SMTP_SSL_CAFILE
        )

        server = smtplib.SMTP_SSL(
            host=Settings.SMTP_SERVER_HOST,
            port=Settings.SMTP_SERVER_PORT,
            timeout=Settings.SMTP_CONN_TIMEOUT,
            context=ssl_context
        )

        return server

    @staticmethod
    def create_multipart(from_addr: str, from_name: str, to_addr: str, to_name: str, subject: str, html: str, plain: str = '', headers: dict = {}):
        multipart = MIMEMultipart('alternative')

        multipart.set_charset('utf8')
        multipart['Date'] = email_utils.formatdate(time.time())
        multipart['Subject'] = Header(subject, "utf-8")
        multipart['To'] = email_utils.formataddr((str(Header(to_name, 'utf-8')), to_addr))
        multipart['From'] = email_utils.formataddr((str(Header(from_name, 'utf-8')), from_addr))

        for header_name, header in headers.items():
            multipart[header_name] = header

        # Fix SpamAssassin score MIXED_ES (Too many es are not es).
        plain = plain.replace('ё', 'e').replace('е', 'e')
        html = html.replace('ё', 'e').replace('е', 'e')

        plain = MIMEText(plain, 'plain', 'UTF-8')
        html = MIMEText(html, 'html', 'UTF-8')

        multipart.attach(plain)
        multipart.attach(html)

        return multipart

    @staticmethod
    def create_delivery_report(contract_id, message_id, from_addr, to_addr, to_name, subject, headers) -> MessageDeliveryReport:
        delivery_report = MessageDeliveryReport.create({
            '_id': message_id,
            '_v': 1,
            '_type': 'email',
            'contract_id': contract_id,
            'service': Settings.app_name,
            'message': {
                'to_addr': to_addr,
                'to_name': to_name,
                'from_addr': from_addr,
                'subject': subject,
                'feedback_id': headers['Feedback-ID']
            },
            'timestamp': int(datetime.datetime.now().timestamp())
        })

        return delivery_report

    @staticmethod
    def create_headers(message_id, contract_id, message_type, service):
        header_feedback_id = parse_header_feedback_id(
            message_id=message_id,
            contract_id=contract_id,
            message_type=message_type,
            service=service
        )

        headers = {
            'Feedback-ID': header_feedback_id
        }

        return headers

    @staticmethod
    def send(user, password, to_addr, msg) -> smtplib.SMTP:
        mail_client = Mail.get_mail_client()
        mail_client.login(user=user, password=password)

        send_mail = mail_client.sendmail(user, to_addr, msg)
        mail_client.quit()

        return send_mail
