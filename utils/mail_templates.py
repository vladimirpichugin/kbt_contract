# -*- coding: utf-8 -*-
# Author: Vladimir Pichugin <vladimir@pichug.in>
import datetime
from itertools import zip_longest

from .helpers import L10n, load_assets_file, parse_placeholders, replace_placeholders

from settings import Settings


class MailTemplate:
    @staticmethod
    def make(message_type, message_id, contract):
        plain = load_assets_file('{}.txt'.format(message_type))
        html = load_assets_file('{}.html'.format(message_type))

        subject = L10n.get('{}.subject'.format(message_type))
        preview = L10n.get('{}.preview'.format(message_type))
        text = L10n.get('{}.text'.format(message_type))

        placeholders = dict(zip_longest(Settings.PLACEHOLDERS.get(message_type), []))

        contract_id = contract.get_contract_id()

        to_addr = contract.get_to_addr()
        to_name = contract.get_to_name()
        first_name = contract.get_customer_name()
        confirm_code = contract.get_confirm_code()

        if contract_id:
            preview = preview.replace('%contract_id%', contract_id)
            subject = subject.replace('%contract_id%', contract_id)

        if confirm_code:
            preview = preview.replace('%confirm_code%', confirm_code)
            subject = subject.replace('%confirm_code%', confirm_code)

        placeholders['email'] = to_addr
        placeholders['message_id'] = str(message_id)
        placeholders['first_name'] = first_name
        placeholders['preview'] = preview
        placeholders['text'] = text
        placeholders['year'] = datetime.datetime.now().year

        for key, value in dict(contract).items():
            if key in Settings.CONTRACT_OBJECT:
                if key == 'program':
                    value = L10n.get(f'program.{value}.name', value).replace('\n', '<br>')
                placeholders[key] = str(value)

        placeholders = parse_placeholders(placeholders)
        html, plain = replace_placeholders(placeholders, html, plain)

        return to_addr, to_name, subject, html, plain
