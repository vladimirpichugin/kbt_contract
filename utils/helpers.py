# -*- coding: utf-8 -*-
# Author: Vladimir Pichugin <vladimir@pichug.in>
import os
import random
import threading
import datetime

from settings import Settings

from .json import Json


L10n = Json('assets/L10n_ru.json')


def load_assets_file(file) -> str:
    with open(os.path.join(os.getcwd(), 'assets', file), 'r', encoding='utf8') as f:
        return f.read().strip()


def parse_placeholders(placeholders):
    for key, value in placeholders.items():
        if value is None:
            placeholders[key] = 'null'
        elif type(value) != str:
            placeholders[key] = str(value)

    return placeholders


def replace_placeholders(placeholders, html, plain) -> (str, str):
    for placeholder, placeholder_value in placeholders.items():
        html = html.replace(f'%{placeholder}%', str(placeholder_value))
        plain = plain.replace(f'%{placeholder}%', str(placeholder_value))

    return html, plain


def parse_header_feedback_id(message_id, contract_id, message_type, service) -> str:
    header = L10n.get('smtp.header.feedback_id')

    header_feedback_id = header.format(
        message_id=message_id,
        contract_id=contract_id,
        message_type=message_type,
        service=service
    )

    return header_feedback_id


def run_threaded(name, func):
    job_thread = threading.Thread(target=func)
    job_thread.setName(f'{name}Thread')
    job_thread.start()


def format_date(timestamp) -> str:
    dt = datetime.datetime.fromtimestamp(timestamp)

    date = dt.strftime(L10n.get('date_time')).split(' ')

    date[1] = L10n.get("months.{month}".format(month=date[1]))

    date = ' '.join(date)

    return date


def gen_contract_id() -> str:
    contract_id = 'ВП-{rand}-{mY}'.format(
        rand=random.getrandbits(16),
        mY=datetime.datetime.now().strftime('%m-%Y')
    )

    return contract_id


def gen_confirmation_code() -> str:
    return str(random.randint(10000, 100000))
