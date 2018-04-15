
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""process of holidays and date"""

import datetime

from pyproj.logger import Logger
from pyproj.holidays import Holidays


class ConstruirUrls(object):
    """ process to calculate holidays """

    logger = None
    holidays = None
    mongodbaccess = None

    def __init__(self, mongodbaccess, level_log):
        """ Build urls to review """
        self.logger = Logger(self.__class__.__name__, level_log).get()
        self.holidays = Holidays(level_log)
        self.mongodbaccess = mongodbaccess

    def construir(self):
        """Run all process"""
        borrados = self.mongodbaccess.delete_many("urls", {})
        self.logger.warn("-- INFO -- vaciamos informacion -- URLS borradas: %d",\
              borrados.deleted_count)
        return sum(self.build_one_search(search) for search in self.buscar_elementos_busquedas())

    def build_one_search(self, ele):
        """each element of busqueda create urls"""
        self.logger.warn("new element %s", ele)
        suma_por_busqueda = 0
        date_direct = ele.get("fromDateInit",\
                              datetime.datetime.now()+datetime.timedelta(days=1))
        while date_direct <= ele.get("fromDateEnd", datetime.datetime.now()):
            if ele.get("type", "o") == "o":
                suma_por_busqueda += \
                    self.revisar_guardar_url_only(ele, date_direct)
            else:
                date_return = ele.get("toDateInit",\
                              datetime.datetime.now()+datetime.timedelta(days=1))
                while date_return <= ele.get("toDateEnd", datetime.datetime.now()):
                    suma_por_busqueda += \
                         self.revisar_guardar_url_return(ele, date_direct, date_return)
                    date_return = date_return+datetime.timedelta(days=1)
            date_direct = date_direct+datetime.timedelta(days=1)
        if suma_por_busqueda == 0:
            self.logger.warn("-- INFO -- desactivamos la busqueda: %s", ele)
            self.mongodbaccess.update_one("busquedas", {"_id":ele["_id"]}, {"activa":False})
        return suma_por_busqueda

    def buscar_elementos_busquedas(self):
        """ doc to explain """
        return self.mongodbaccess.find("busquedas", {"activa":True})

    def revisar_guardar_url_only(self, ele, date_direct):
        """review for return flights if can save"""
        if (date_direct > datetime.datetime.now()) and \
           (self.holidays.get_number_holidays(date_direct, date_direct)\
            >= ele.get("minHolidays", 0)):
            return self.guardar_url(crear_url(ele, date_direct, date_direct))
        return 0

    def revisar_guardar_url_return(self, ele, date_direct, date_return):
        """review for return flights if can save"""
        if (date_direct <= date_return) and(date_direct > datetime.datetime.now()):
            dif = (date_return - date_direct) + datetime.timedelta(days=1)
            if dif <= datetime.timedelta(days=ele.get("maxDays", 0)) and\
               dif >= datetime.timedelta(days=ele.get("minDays", 0)) and\
               (self.holidays.get_number_holidays(date_direct, date_return)\
                >= ele.get("minHolidays", 0)):
                return self.guardar_url(crear_url(ele, date_direct, date_return))
        return 0

    def guardar_url(self, urls):
        """ doc to explain """
        existe = self.mongodbaccess.find_one("urls", {"url":urls.get("url", "ERROR")})
        if existe is None:
            self.mongodbaccess.insert("urls", urls)
            return 1
        return 0

def crear_url(datos, date_direct, date_return):
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
