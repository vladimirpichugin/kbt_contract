# -*- coding: utf-8 -*-
# Author: Vladimir Pichugin <vladimir@pichug.in>
import datetime
import dateutil.parser

from bson.objectid import ObjectId

from settings import Settings


class SDict(dict):
    def __init__(self, *args, **kwargs):
        self.changed = False
        super().__init__(*args, **kwargs)

    def __getitem__(self, item):
        return super().__getitem__(item)

    def __setitem__(self, item, value):
        try:
            if super().__getitem__(item) != value:
                self.changed = True
        except KeyError:
            self.changed = True

        return super().__setitem__(item, value)

    def __delitem__(self, item):
        self.changed = True
        super().__delitem__(item)

    def getraw(self, item, default=None):
        try:
            return super().__getitem__(item)
        except KeyError:
            return default

    def setraw(self, item, value):
        super().__setitem__(item, value)

    def delraw(self, item):
        super().__delitem__(item)


class Contract(SDict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @staticmethod
    def create_from_form_data(form):
        f = Settings.CONTRACT_OBJECT
        f.update(form)

        return Contract(
            program=f.get('program'),

            customer_email=f.get('customer[email]'),
            customer_phone=f.get('customer[phone]'),
            customer_role=f.get('customer[role]'),
            customer_lastName=f.get('customer[lastName]'),
            customer_firstName=f.get('customer[firstName]'),
            customer_middleName=f.get('customer[firstName]'),
            customer_birthDate=f.get('customer[birthDate]'),
            customer_sex=f.get('customer[sex]'),
            customer_docType=f.get('customer[docType]'),
            customer_docSerial=f.get('customer[docSerial]'),
            customer_docNumber=f.get('customer[docNumber]'),
            customer_docIssued=f.get('customer[docIssued]'),
            customer_docWhenIssued=f.get('customer[docWhenIssued]'),
            customer_address=f.get('customer[address]'),

            student_email=f.get('student[email]'),
            student_phone=f.get('student[phone]'),
            student_lastName=f.get('student[lastName]'),
            student_firstName=f.get('student[firstName]'),
            student_middleName=f.get('student[middleName]'),
            student_sex=f.get('student[sex]'),
            student_birthDate=f.get('student[birthDate]'),
            student_docType=f.get('student[docType]'),
            student_docSerial=f.get('student[docSerial]'),
            student_docNumber=f.get('student[docNumber]'),
            student_docIssued=f.get('student[docIssued]'),
            student_docWhenIssued=f.get('student[docWhenIssued]'),
            student_address=f.get('student[address]')
        )

    def get_obj_id(self) -> ObjectId:
        return self.getraw('_id')

    def get_contract_id(self):
        return self.getraw('contract_id')

    def get_program(self):
        return self.getraw('program')

    def get_confirm_code(self):
        return self.getraw('confirm_code')

    def get_to_addr(self):
        return self.getraw('customer_email')

    def get_to_name(self):
        return self.get_name()

    def get_customer_name(self):
        return self.getraw('customer_firstName')

    def get_customer_age(self):
        return self.get_age()

    def get_customer_role(self):
        return self.getraw('customer_role')

    def get_student_age(self):
        return self.get_age('student')

    def get_name(self, t='customer', include_middle_name=False) -> str:
        name = []

        if t:
            t += '_'
        else:
            t = ''

        if self.getraw(f'{t}firstName'):
            name.append(self.getraw(f'{t}firstName'))
        if self.getraw(f'{t}middleName') and include_middle_name:
            name.append(self.getraw(f'{t}middleName'))
        if self.getraw(f'{t}lastName'):
            name.append(self.getraw(f'{t}lastName'))

        if name:
            return ' '.join(name)

        return ''

    def get_age(self, t='customer') -> int:
        birth_date = self._decode_date(f'{t}_birthDate')

        if not birth_date:
            return 0

        today = datetime.date.today()

        return (today.year - birth_date.year -
                ((today.month, today.day) <
                 (birth_date.month,
                  birth_date.day)))

    def get_sex(self, t='customer') -> str:
        value = self.getraw(f'{t}_sex')

        return 'female' if value == '2' else 'male'

    def get_dt(self, key, default=None):
        return self._decode_date(key) or default

    def _decode_date(self, key):
        birth_date = self.getraw(key)

        if not birth_date:
            return None

        return dateutil.parser.parse(birth_date)

    def created_dt(self) -> datetime.datetime:
        return datetime.datetime.fromtimestamp(self.getraw('timestamp_created'))


class MessageDeliveryReport(SDict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.id = self.getraw('_id')

    @staticmethod
    def create(data):
        return MessageDeliveryReport(data)

