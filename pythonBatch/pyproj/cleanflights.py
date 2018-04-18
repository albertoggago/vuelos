
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""vuelos"""

import datetime

from pyproj.logger import Logger


class CleanFlights(object):
    """clean Flights"""

    mongodbaccess = None
    logger = None

    def __init__(self, mongo_db_access, level_log):
        self.logger = Logger(self.__class__.__name__, level_log).get()
        self.mongodbaccess = mongo_db_access
        self.logger.info("Inicio: %s", datetime.datetime.now())


    def clean(self):
        """ clean Process """
        self.logger.info("++INFO-- CLEAN FASE I")
        result = {"total":0}
        for vuelo in self.mongodbaccess.find("vuelos", {}):
            result = self.analize_each_flight(result, vuelo)
        return result

    def analize_each_flight(self, result, vuelo):
        """each flight analyze each rule"""
        apply(lambda rule: accumulate_dic(result, rule(vuelo)), self.create_all_rules())
        result["total"] += 1
        return result

    def create_all_rules(self):
        """ insert all rules created for run all"""
        return [self.rule_older_than_15days]

    def rule_older_than_15days(self, elemento):
        """First Rule: move all flights from vuelos to vuelosOld older than 15 days """
        date15 = datetime.datetime.now()-datetime.timedelta(days=15)
        deleted = 0
        inserted_old = 0
        if elemento.get("dateDirect", datetime.datetime) < date15:
            if self.mongodbaccess.insert("vuelosOld", elemento) is not None:
                inserted_old = 1
                self.logger.error("Error vuelo not insert backup but delete %s", elemento)
            self.mongodbaccess.delete_one("vuelos", {"_id":elemento.get("_id")})
            deleted = 1
        return {"deleted":deleted, "inserted_old":inserted_old}

def accumulate_dic(dict_big, dict_to_add):
    """get two dicts and add first the data of second"""
    for key, value in dict_to_add.iteritems():
        dict_big[key] = dict_big.get(key, 0) + value
    return dict_big
