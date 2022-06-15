import requests
import json

from utils import logger

from settings import Settings


class License:
    def __init__(self):
        self.license_server = "https://pichug.in/app_version?v=2"
        self.license_server_errors = {
            'LICENSE_BANNED': 'Лицензия на использование продукта отозвана. Обратитесь к разработчику.',
            'LICENSE_EXPIRED': 'Лицензия на использование продукта истекла. Обратитесь к разработчику.',
            'LICENSE_NOT_FOUND': 'Лицензия не найдена на сервере.'
        }

    def check_license_status(self):
        try:
            logger.info('Разработчик: {}'.format(Settings.app_author))

            l = self.request_license()

            status_code = l.status_code

            if status_code == 200:
                ld = json.loads(l.text)

                if ld.get('ErrorMessage'):
                    logger.error('Сервер не подтвердил лицензию, ошибка: {}'.format(self.license_server_errors.get(ld.get('ErrorMessage'), ld.get('ErrorMessage'))))
                else:
                    logger.info('Сервер подтвердил лицензию.')
                    logger.info('- Продукт: {}'.format(ld.get('License', {}).get('Product', 'UNKNOWN PRODUCT')))
                    logger.info('- Тип лицензии: {}'.format(ld.get('License', {}).get('Type', 'UNKNOWN TYPE')))
                    logger.info('- Истекает: {}'.format(ld.get('License', {}).get('Expires', 'UNKNOWN DATE')))

                    if not ld.get('AppVersionLatest'):
                        logger.info('Доступна новая версия приложения, скачайте: {}'.format(ld.get('AppRepo')))

                    if not ld.get('AppSupported'):
                        logger.info('Приложение больше не поддерживается разработчиком. Вы можете использовать данную версию приложения, но работоспособность может быть приостановлена в любой момент.')

                    return True
            elif status_code == 404:
                logger.error('Сервер не подтвердил лицензию на использование продукта (приложение {} не найдено на сервере).'.format(Settings.app_name))
            elif status_code == 400:
                logger.error('Не могу проверить лицензию продукта, неверный запрос к серверу.')
            else:
                logger.error('Не могу проверить лицензию продукта, неизвестная ошибка.')
        except:
            logger.error('Не могу проверить лицензию продукта, неизвестная ошибка.')

        logger.error('Запуск приложения отменён. Попробуйте позже или обратитесь к разработчику.')

        return False

    def request_license(self):
        headers = {
            'Appname': Settings.app_name,
            'Appversion': Settings.app_version,
            'License': Settings.app_license_key,
            'User-Agent': f'{Settings.app_name}/{Settings.app_version}'
        }

        return requests.get(self.license_server, headers=headers)

