
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""process of holidays and date"""

import datetime

from pyproj.logger import Logger
from pyproj.holidays import Holidays


class BuildUrls(object):
    """ process to calculate holidays """

    logger = None
    holidays = None
    mongodbaccess = None

    def __init__(self, mongodbaccess, level_log):
        """ Build urls to review """
        self.logger = Logger(self.__class__.__name__, level_log).get()
        self.holidays = Holidays(level_log)
        self.mongodbaccess = mongodbaccess

    def build_urls(self):
        """Build all urls"""
        deleted = self.mongodbaccess.delete_many("urls", {})
        self.logger.warn("-- INFO -- URLS deleted: %d",\
              deleted.deleted_count)
        return sum(self.build_urls_one_search(search) for search in self.find_elements_search())

    def find_elements_search(self):
        """ doc to explain """
        return self.mongodbaccess.find("busquedas", {"activa":True})

    def build_urls_one_search(self, search):
        """each element of busqueda create urls"""
        self.logger.warn("new element %s", search)
        sum_per_search = 0
        date_direct = search.get("fromDateInit",\
                              datetime.datetime.now()+datetime.timedelta(days=1))
        while date_direct <= search.get("fromDateEnd", datetime.datetime.now()):
            if search.get("type", "o") == "o":
                sum_per_search += \
                    self.review_save_url_onetrip(search, date_direct)
            else:
                sum_per_search += self.process_date_return(search, date_direct)
            date_direct = date_direct+datetime.timedelta(days=1)
        if sum_per_search == 0:
            self.logger.warn("-- INFO -- desactivate search, no generate urls: %s", search)
            self.mongodbaccess.update_one("busquedas", {"_id":search["_id"]}, {"activa":False})
        return sum_per_search

    def process_date_return(self, search, date_direct):
        """fixed date init find all posibilities date return"""
        suma = 0
        date_return = search.get("toDateInit", datetime.datetime.now()+datetime.timedelta(days=1))
        while date_return <= search.get("toDateEnd", datetime.datetime.now()):
            suma += self.review_save_url_return(search, date_direct, date_return)
            date_return = date_return+datetime.timedelta(days=1)
        return suma

    def review_save_url_onetrip(self, search, date_direct):
        """review for return flights if can save"""
        if (date_direct > datetime.datetime.now()) and \
           (self.holidays.get_number_holidays(date_direct, date_direct)\
            >= search.get("minHolidays", 0)):
            return self.save_url(create_url(search, date_direct, date_direct))
        return 0

    def review_save_url_return(self, search, date_direct, date_return):
        """review for return flights if can save"""
        if (date_direct <= date_return) and(date_direct > datetime.datetime.now()):
            dif = (date_return - date_direct) + datetime.timedelta(days=1)
            if dif <= datetime.timedelta(days=search.get("maxDays", 0)) and\
               dif >= datetime.timedelta(days=search.get("minDays", 0)) and\
               (self.holidays.get_number_holidays(date_direct, date_return)\
                >= search.get("minHolidays", 0)):
                return self.save_url(create_url(search, date_direct, date_return))
        return 0

    def save_url(self, urls):
        """ doc to explain """
        if self.mongodbaccess.find_one("urls", {"url":urls.get("url", "ERROR")}) is None:
            self.mongodbaccess.insert("urls", urls)
            return 1
        return 0

def create_url(datos, date_direct, date_return):
    """ doc to explain """
    if datos.get("type", "o") == "o":
        url = "https://www.google.es/flights/#flt="+datos.get("from", "XXX")+"."\
            +datos.get("to", "XXX")+"."\
            +date_direct.strftime("%Y-%m-%d")\
            +";c:EUR;e:1;sd:1;t:f;tt:o"
    else:
        url = "https://www.google.es/flights/#flt="+datos.get("from", "XXX")+"."\
            +datos.get("to", "XXX")+"."\
            +date_direct.strftime("%Y-%m-%d")\
            + "*"+datos.get("to", "XXX")+"."+datos.get("from", "XXX")+"."\
            +date_return.strftime("%Y-%m-%d")\
            +";c:EUR;e:1;sd:1;t:f"

    return {"url":url, "from":datos.get("from", "XXX"), "to":datos.get("to", "XXX"),\
            "dateDirect":date_direct, "dateReturn":date_return,\
            "type":datos.get("type", "XXX")}
