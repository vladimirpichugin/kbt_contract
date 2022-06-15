# -*- coding: utf-8 -*-
# Author: Vladimir Pichugin <vladimir@pichug.in>
import traceback
import time
import uuid

from flask import Flask, request, Response, abort, request_started, request_finished, \
    got_request_exception, request_tearing_down

from utils import *

logger.debug(f"Initializing {Settings.app_name} (v{Settings.app_version})..")

from settings import Settings as settings


class ContractAPI:
    def request_state(self, request, response=None, error=None):
        message = "{event} {remote_addr} {protocol}: \"{http_method} {path}\"{http_status}{error}{time}".format(
            event="RESPONSE for" if response else "REQUEST from",
            protocol=request.environ.get('SERVER_PROTOCOL'),
            remote_addr=request.headers.get('X-Real-IP', request.remote_addr),
            http_method=request.method,
            path=request.path,
            http_status=" — " + response.status if response else "",
            error=" — " + error if error else "",
            time=(" — %1.2f sec " % (time.time() - request.start_time)) if response else ""
        )

        if error:
            logger.error(message)
        else:
            logger.info(message)

        return True

    def run(self):
        metrics = {
            "start_time": int(time.time()),
            "exceptions": {
                "app": 0,
                "routes": 0,
                "requests": 0,
                "database": 0
            },
            "requests": {
                "total": 0,
                "active": 0
            },
            "response_codes": {
            }
        }

        def before_request(sender, **extra):
            nonlocal metrics
            request.start_time = time.time()

            self.request_state(request=request, response=None)

            if settings.authorization_header:
                authorization_header = request.headers.get('authorization', None)
                if authorization_header != f'Bearer {settings.authorization_header}':
                    return abort(failed(response="Unauthorized", status=401))

            metrics["requests"]["active"] += 1

        def after_request(sender, response, **extra):
            nonlocal metrics

            metrics["requests"]["active"] -= 1
            if metrics["requests"]["active"] < 0:
                metrics["requests"]["active"] = 0

            self.request_state(request=request, response=response)

            metrics["requests"]["total"] += 1

            if response.status_code not in metrics["response_codes"]:
                metrics["response_codes"][response.status_code] = 0
            metrics["response_codes"][response.status_code] += 1

        def exception_request(sender, exception, **extra):
            pass

        def down_request(sender, **extra):
            pass

        app = Flask(settings.app_name)

        # Отключает внутренние логи Flask.
        logging.getLogger('werkzeug').setLevel(logging.DEBUG if settings.werkzeug_logs else logging.ERROR)

        # Отключает сортировку ключей при парсинге JSON-строки.
        app.config['JSON_SORT_KEYS'] = False

        app.config['TESTING'] = False

        request_started.connect(before_request, app)
        request_finished.connect(after_request, app)
        request_tearing_down.connect(down_request, app)
        got_request_exception.connect(exception_request, app)

        def ok(response=None, status=200):
            try:
                if type(response) == str:
                    response = {'message': response}

                return Response(
                    response=json.dumps({
                        "ok": True,
                        "response": response
                    }),
                    status=status,
                    headers=settings.headers,
                    content_type='application/json',
                    direct_passthrough=True
                )
            except:
                logger.error("Unexpected error occurred while creating Response (failed), connection aborted.")
                if traceback.format_exc():
                    logger.error(traceback.format_exc())
                return abort(500)  # Internal Server Error

        def failed(response=None, status=400, code=None):
            logger.debug(response)
            try:
                if type(response) == str:
                    response = {'message': response, 'code': code}

                return Response(
                    response=json.dumps({
                        "ok": False,
                        "response": response
                    }),
                    status=status,
                    headers=settings.headers,
                    content_type='application/json',
                    direct_passthrough=True
                )
            except:
                logger.error("Unexpected error occurred while creating Response (failed), connection aborted.")
                if traceback.format_exc():
                    logger.error(traceback.format_exc())
                return abort(500)  # Internal Server Error

        @app.route("/", methods=['GET', 'OPTIONS'])
        def index():
            return ok({
                "app": {
                    "name": settings.app_name,
                    "version": settings.app_version,
                    "author": settings.app_author,
                    "license": {

                    },
                    "uptime": int(time.time() - metrics["start_time"]),
                    "start_time": metrics["start_time"]
                }
            }, 200)

        @app.route('/favicon.ico')
        def favicon():
            return Response(
                response='Not Found',
                status=404,
                headers=settings.headers,
                content_type='text/html'
            )

        @app.route('/v1/contract', endpoint='contract_route_post', methods=['POST'])
        def contract_route_post():
            try:
                f = request.form

                args = {
                    'program': {},
                    'agreement': {},

                    'customer[role]': {'allowed': ['1', '2', '3', '4', '5', '6', '7']},
                    'customer[lastName]': {},
                    'customer[firstName]': {},
                    'customer[middleName]': {'empty': True},
                    'customer[birthDate]': {},
                    'customer[docType]': {},
                    'customer[docSerial]': {},
                    'customer[docNumber]': {},
                    'customer[docIssued]': {},
                    'customer[docWhenIssued]': {},
                    'customer[address]': {},
                    'customer[email]': {},
                    'customer[phone]': {}
                }

                if f.get('customer[role]') != '1':
                    args.update({
                        'student[lastName]': {},
                        'student[firstName]': {},
                        'student[middleName]': {'empty': True},
                        'student[birthDate]': {},
                        'student[docType]': {},
                        'student[docSerial]': {},
                        'student[docNumber]': {},
                        'student[docIssued]': {},
                        'student[docWhenIssued]': {},
                        'student[address]': {},
                        'student[email]': {},
                        'student[phone]': {}
                    })

                invalid_args = []
                f = f.to_dict()
                for key, value in f.items():
                    f[key] = value.strip()

                for r_arg in args.keys():
                    if r_arg not in f.keys():
                        invalid_args.append({'argument': r_arg, 'errorMessage': 'Required argument not found.', 'errorCode': 'REQUIRED_ARGUMENT_NOT_FOUND'})
                    elif f.get(r_arg).strip() == '' and not args.get(r_arg).get('empty'):
                        invalid_args.append({'argument': r_arg, 'errorMessage': 'Empty argument value.', 'errorCode': 'EMPTY_ARGUMENT_VALUE'})

                if f.get('agreement') != 'accept':
                    invalid_args.append({'argument': 'agreement', 'errorMessage': 'Agreement not accepted.', 'errorCode': 'AGREEMENT_NOT_ACCEPTED'})

                if invalid_args:
                    return failed({
                        "message": "Bad Request: Invalid Form Data",
                        "code": "INVALID_FORM_DATA",
                        "invalid_args": invalid_args
                    }, status=400)

                contract = Contract().create_from_form_data(f)
                contract['_id'] = str(uuid.uuid4())
                contract['confirm_code'] = gen_confirmation_code()

                contract['timestamp_created'] = contract['timestamp_agreement_accepted'] = int(time.time())

                contract_id = contract.get_obj_id()

                contract['contract_id'] = gen_contract_id()
                contract_file = ContractGenerator.create_contract('example', contract)

                from_addr = Settings.SMTP_USER
                from_pass = Settings.SMTP_PASS

                message_id = str(uuid.uuid4())
                message_type = 'contract_confirm'

                to_addr, to_name, subject, html, plain = MailTemplate.make(
                    message_id=message_id, message_type=message_type, contract=contract
                )

                logger.debug(f"[message id:{message_id}] Preparing mail-{message_type} ({contract_id})")

                headers = Mail.create_headers(message_id=message_id, contract_id=contract_id, message_type=message_type, service=Settings.app_name)

                multipart = Mail.create_multipart(from_addr, Settings.SMTP_NAME, to_addr, to_name, subject, html, plain,
                                                  headers)
                msg = multipart.as_string()

                delivery_report = Mail.create_delivery_report(contract_id, message_id, from_addr, to_addr, to_name, subject, headers)

                logger.debug(f"delivery_report: {delivery_report}")

                logger.info(f"[message id:{message_id}] Sending mail-{message_type} to <{to_addr}> ({contract_id})`")

                response = Mail.send(
                    user=from_addr,
                    password=from_pass,
                    to_addr=to_addr,
                    msg=msg
                )
                logger.debug(f"response: {response}")

                resp = {
                    'email': contract.get_to_addr()
                }

                return ok(resp)
            except:
                logger.error("An error occurred while running the route:")
                logger.error(traceback.format_exc())
                return failed("Internal Server Error", 500)

        @app.route('/v1/contract/confirm', endpoint='contract_confirm_route', methods=['POST'])
        def contract_confirm_route():
            try:
                #contract_link = 'https://kbt.moscow/example.pdf'
                contract_link = 'http://localhost:63342/kbt.moscow/contracts/example.pdf?_ijt=15tbd1187ngmnk8nmqlvgbgp7k&_ij_reload=RELOAD_ON_SAVE'

                resp = {
                    'contract_link': contract_link
                }

                return ok(resp)
            except:
                logger.error("An error occurred while running the route:")
                logger.error(traceback.format_exc())
                return failed("Internal Server Error", 500)

        # Errors
        @app.errorhandler(400)
        def code_400(reason=None):
            return failed({
                "message": "Bad Request",
                "code": "BAD_REQUEST"
            }, status=400)

        @app.errorhandler(403)
        def code_400(reason=None):
            return failed({
                "message": "Forbidden",
                "code": "FORBIDDEN"
            }, status=403)

        @app.errorhandler(404)
        def code_400(reason=None):
            return failed({
                "message": "Not Found",
                "code": "NOT_FOUND"
            }, status=404)

        @app.errorhandler(405)
        def code_400(reason=None):
            return failed({
                "message": "Method Not Allowed",
                "code": "METHOD_NOT_ALLOWED"
            }, status=405)

        @app.errorhandler(500)
        def code_500(reason=None):
            return failed({
                "message": "Internal Server Error",
                "code": "INTERNAL_SERVER_ERROR"
            }, status=500)

        logger.info(f"{settings.app_name} (v{Settings.app_version}) successfully initialized, listen {settings.host}:{settings.port}")

        app.run(
            host=settings.host,
            port=settings.port,
            debug=settings.flask_debug
        )
