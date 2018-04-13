
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

        fecha_actual = datetime.datetime.now()
        borrados = self.mongodbaccess.delete_many("urls", {})
        self.logger.warn("-- INFO -- vaciamos informacion -- URLS borradas: %d",\
              borrados.deleted_count)
        suma_urls = 0
        for ele in self.buscar_elementos_busquedas():
            busqueda_activa = False
            date_direct = ele["fromDateInit"]
            while date_direct <= ele["fromDateEnd"]:
                if ele["type"] == "o":
                    if date_direct > fecha_actual:
                        busqueda_activa = True
                        suma_urls += self.crear_guardar_url(ele, date_direct, date_direct)
                else:
                    date_return = ele["toDateInit"]
                    while date_return <= ele["toDateEnd"]:
                        if (date_direct <= date_return) and(date_direct > fecha_actual):
                            dif = (date_return - date_direct) + datetime.timedelta(days=1)
                            if dif <= datetime.timedelta(days=ele["maxDays"]) and\
                               dif >= datetime.timedelta(days=ele["minDays"]) and\
                               (self.holidays.get_holidays(date_direct, date_return)\
                                       >= ele["minHolidays"]):
                                suma_urls += self.crear_guardar_url(ele, date_direct, date_return)
                                busqueda_activa = True
                        date_return = date_return+datetime.timedelta(days=1)
                date_direct = date_direct+datetime.timedelta(days=1)
            if not busqueda_activa:
                print "-- INFO -- desactivamos la busqueda: {0}".format(ele)
                self.mongodbaccess.update_one("busquedas", {"_id":ele["_id"]}, {"activa":False})

        print "-- INFO -- construir urls -- numero de URLS: {0}".format(suma_urls)

    def buscar_elementos_busquedas(self):
        """ doc to explain """
        return self.mongodbaccess.find("busquedas", {"activa":True})

    def crear_guardar_url(self, datos, date_direct, date_return):
        """ doc to explain """
        if datos["type"] == "o":
            url = "https://www.google.es/flights/#flt="+datos["from"]+"."+datos["to"]+"."\
                +date_direct.strftime("%Y-%m-%d")\
                + "*"+datos["to"]+"."+datos["from"]+"."\
                +";c:EUR;e:1;sd:1;t:f;tt:o"
        else:
            url = "https://www.google.es/flights/#flt="+datos["from"]+"."+datos["to"]+"."\
                +date_direct.strftime("%Y-%m-%d")\
                + "*"+datos["to"]+"."+datos["from"]+"."\
                +date_return.strftime("%Y-%m-%d")\
                +";c:EUR;e:1;sd:1;t:f"
        existe = self.mongodbaccess.find_one("urls", {"url":url})
        if existe is None:
            self.mongodbaccess.insert("urls", {"url":url, "from":datos["from"], "to":datos["to"],\
                                 "dateDirect":date_direct, "dateReturn":date_return,\
                                 "type":datos["type"], "query":datos["query"]})
            return 1
        return 0
