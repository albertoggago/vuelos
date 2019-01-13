#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Only a Class MongoDBAccess"""

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure, \
                           ConfigurationError, DuplicateKeyError
from pyproj.logger import Logger

class MongoDBAccess(object):
    """Class to access to MongoDB allow access and review connections"""

    db_access = None
    _client = None

    def __init__(self, config, levelLog):
        """Need a file where has got all parameters and level of Loggin"""
        self.logger = Logger(self.__class__.__name__, levelLog).get()
        self.logger.setLevel('INFO')

        try:
            self.logger.debug(config.get("url", ""))
            self._client = MongoClient(config.get("url", ""))
            self.db_access = self._client[config.get("nameDB")]
            self.logger.info("-- INFO -- DATA BASE CONECT OK")
        except ConfigurationError:
            self.logger.error("ConfigurationErr")
        except ConnectionFailure:
            self.logger.error("ConnectionFailure")
        except OperationFailure:
            self.logger.error("Authentication failure")

    def status(self):
        """Determinate True is connect or False if is not connect"""
        if self._client is None:
            return False
        try:
            self.logger.debug(self._client.server_info())
            return True
        except ConnectionFailure:
            self.logger.error("ConnectionFailure")
            return False
        except OperationFailure:
            self.logger.error("Authentication failure")
            return False

    def find_one(self, collection, query, sort=None):
        """Find one element only return a json element"""
        if self.status():
            sort = None if sort is None else sort.items()
            self.logger.info("Access to collection: %s, query %s", collection, query)
            return self.db_access[collection].find_one(query, sort=sort)
        self.logger.error("Database Not INIT Find_one")
        return None

    def find(self, collection, query, sort=None, limite=None):
        """Find several elements is a cursor, atention for line in cursor is better"""
        if self.status():
            self.logger.info("Access to collection Multi: %s, query: %s, sort: %s, limit: %s",\
                collection, query, sort, limite)
            limite = 0 if limite is None else limite
            sort = None if sort is None else sort.items()
            return self.db_access[collection].find(query, sort=sort, limit=limite)
        self.logger.error("Database Not INIT Find")
        return None

    def update_one(self, collection, query, change, is_set="set"):
        """Update One return status of update"""
        if self.status():
            self.logger.info("Modify collection: %s, query: %s, modify: %s, set: %s",\
                collection, query, change, is_set)
            setdollar = "$"+is_set
            return self.db_access[collection].update_one(query, {setdollar:change})
        self.logger.error("Database Not INIT Update_one")
        return None

    def update_many(self, collection, query, change, is_set="set"):
        """Update Many return status of update"""
        if self.status():
            self.logger.info("Modify Many collection: %s, query: %s, modify: %s, set: %s",\
                collection, query, change, is_set)
            setdollar = "$"+is_set
            return self.db_access[collection].update_many(query, {setdollar:change})
        self.logger.error("Database Not INIT Update_one")
        return None

    def insert(self, collection, element):
        """Insert return status of insert"""
        if self.status():
            self.logger.debug("Insert collection: %s, data: %s", collection, element)
            #control duplicated
            try:
                return self.db_access[collection].insert(element)
            except DuplicateKeyError:
                return None
        self.logger.error("Database Not INIT Find")
        return None

    def delete_one(self, collection, element):
        """delete One return status of delete"""
        if self.status():
            self.logger.info("Remove collection: %s, data: %s", collection, element)
            return self.db_access[collection].delete_one(element)
        self.logger.error("Database Not INIT Find")
        return None

    def delete_many(self, collection, element):
        """delete return status of delete"""
        if self.status():
            self.logger.info("Remove collection: %s, data: %s", collection, element)
            return self.db_access[collection].delete_many(element)
        self.logger.error("Database Not INIT Find")
        return None

    def aggregate(self, collection, element):
        """delete return status of delete"""
        if self.status():
            self.logger.info("Aggregate collection: %s, data: %s", collection, element)
            return self.db_access[collection].aggregate(element)
        self.logger.error("Database Not INIT Find")
        return None

    def drop(self, collection):
        """Drop a collection return status of drop"""
        if self.status():
            self.logger.info("Drop collection: %s", collection)
            return self.db_access[collection].drop()
        self.logger.error("Database Not INIT Find")
        return None
