# -*- coding: utf-8 -*-
# Author: Vladimir Pichugin <vladimir@pichug.in>

class Settings:
    app_name = 'kbt_contract'
    app_version = '1.0'
    app_author = 'Владимир Пичугин <vladimir@pichug.in>'

    app_license_key = ''

    debug = True  # Debug Log
    flask_debug = False  # Flask Debug Log
    werkzeug_logs = False  # Flask Default Logs

    # MongoDB Settings
    mongo = 'mongodb://kbt_bot:password@localhost:27017'
    database = 'kbt'

    # Network Settings
    host = 'localhost'
    port = 32929

    authorization_header = None

    allowed_http_methods = ['OPTIONS', 'HEAD', 'GET', 'POST']
    content_type = 'application/json'
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': '*',
        'Access-Control-Allow-Headers': 'Origin, X-Requested-With, Content-Type, Cache-Control',
        'Content-Security-Policy': 'default-src \'self\'',
        'Content-Security-Policy-Report-Only': '',
        'X-Powered-By': 'KBT Contract',
        'X-App-Author': 'Vladimir Pichugin <vladimir@pichug.in>'
    }

    SMTP_SSL_CAFILE = 'assets/cert.pem'

    SMTP_NAME = 'Колледж бизнес-технологий'

    SMTP_SERVER_HOST = 'mail.pichug.in'
    SMTP_SERVER_PORT = 465
    SMTP_CONN_TIMEOUT = 5
    SMTP_SSL_CAFILE = 'assets/cert.pem'

    CONTRACT_TEMPLATE = 'assets/contract_template.docx'

    SAVE_CONTRACTS_FOLDER = ''

    SMTP_USER = 'noreply@kbt.moscow'
    SMTP_PASS = 'password'

    ADMIN_EMAIL = 'contract@kbt.moscow'

    PLACEHOLDERS = {
        'contract_confirm': [
            'email', 'year', 'first_name', 'program', 'contract_id', 'confirm_code'
        ],
        'contract': [
            'email', 'year', 'first_name', 'program', 'contract_id', 'contract_link'
        ],
        'contract_admin': [
            'email', 'year', 'program', 'contract_id', 'contract_link'
        ]
    }

    CONTRACT_OBJECT = {
        '_id': None,
        'contract_id': None,
        'confirm_code': None,

        'status': 'CREATED',

        'program': None,
        'program_code': None,

        'customer_email': None,
        'customer_phone': None,
        'customer_role': None,
        'customer_lastName': None,
        'customer_firstName': None,
        'customer_middleName': None,
        'customer_birthDate': None,
        'customer_sex': None,
        'customer_docType': None,
        'customer_docSerial': None,
        'customer_docNumber': None,
        'customer_docIssued': None,
        'customer_docWhenIssued': None,
        'customer_address': None,

        'student_email': None,
        'student_phone': None,
        'student_lastName': None,
        'student_firstName': None,
        'student_middleName': None,
        'student_birthDate': None,
        'student_sex': None,
        'student_docType': None,
        'student_docSerial': None,
        'student_docNumber': None,
        'student_docIssued': None,
        'student_docWhenIssued': None,
        'student_address': None,

        'timestamp_agreement_accepted': None,
        'timestamp_created': None,
        'timestamp_confirmed': None,
        'code_sent_attempts': [],
        'code_wrong_attempts': [],

        'file': None,
        'file_hash': None,

        '_v': 1
    }
