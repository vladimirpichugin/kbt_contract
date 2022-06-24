# -*- coding: utf-8 -*-
# Author: Vladimir Pichugin <vladimir@pichug.in>
import pymongo
from bson.objectid import ObjectId
import datetime

from utils import logger
from utils.data import *


class Storage:
    def __init__(self, connect, database):
        self.mongo_client = pymongo.MongoClient(connect, authSource='admin')
        self.db = self.mongo_client.get_database(database)
        self.contracts = self.db.get_collection('contracts')

    def get_contract_by_session_id(self, session_id):
        data = self.get_data(self.contracts, session_id, 'session_id')

        if not data:
            return None

        contract = Contract(data)

        return contract

    def save_contract(self, contract: Contract) -> bool:
        if not contract.changed:
            logger.debug(f'Contract <{contract.get_obj_id()}> already saved, data not changed.')
            return True

        save_result = self.save_data(self.contracts, contract.get_obj_id(), contract)

        if save_result:
            logger.debug(f'Contract <{contract.get_obj_id()}> saved, result: {save_result}')
            return True

        logger.error(f'Contract <{contract.get_obj_id()}> not saved, result: {save_result}')

        return False

    @staticmethod
    def get_data(c: pymongo.collection.Collection, value, name="_id"):
        data = c.find_one({name: value})

        if data:
            return SDict(data)

        return None

    @staticmethod
    def save_data(c: pymongo.collection.Collection, value, data: SDict, name="_id"):
        if c.find_one({name: value}):
            operation = c.update_one({name: value}, {"$set": data})
            result = operation.raw_result if operation else None
        else:
            operation = c.insert_one(data)
            result = operation.inserted_id if operation else None

        return result
