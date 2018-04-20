#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""vuelos"""

import datetime
import json


from pyproj.mongodbaccess import MongoDBAccess
from pyproj.logger import Logger
from pyproj.buildurls import BuildUrls
from pyproj.findflights import FindFlights


class Vuelos(object):
    """find Flight"""

    level_log = None
    config = None
    mongodbaccess = None
    logger = None

    def __init__(self, file_config, level_log):
        self.level_log = level_log
        self.logger = Logger(self.__class__.__name__, level_log).get()
        try:
            self.config = json.loads(open(file_config, "r").read())
            self.mongodbaccess = MongoDBAccess(self.config, level_log)
        except IOError:
            self.logger.error("File Error: %s", file_config)
            self.config = {}
            self.mongodbaccess = MongoDBAccess({}, level_log)
        self.logger.info("Inicio: %s", datetime.datetime.now())


    def ejecutar(self, nivel):
        """ run load process """
        print "++ INFO ++ MODULO PRINCIPAL MODO DE EJECUCION: {0}".format(nivel)
        if nivel == "1":
            print "-- INFO -- MODO 1 duro ejecuta y limpia los datos del dia"
            #proceso duro vaciamos informacion y empezamos
            print "++ INFO ++ Vaciamos informacion del dia"
            print "-- INFO -- dia: {0}".format(today())
            borrados = self.vaciar_dia()
            print "-- INFO -- vaciamos informacion -- Vuelos borrados del dia: {0}"\
                  .format(borrados.deleted_count)
            urls = BuildUrls(self.mongodbaccess, self.level_log).build_urls()
            print "-- INFO -- construir urls -- numero de URLS: {0}".format(urls)
        else:
            print "-- INFO -- MODO 0 suave solo si hay datos que ejecutar"
            #proceso soft miramos si hay algo que procesar
            #si no hay nada que procesar o el dia no se ha ejecutado.
            if self.return_urls().count() == 0:
                #no hay nada que ejecutar
                if self.find_last_day() < today():
                    # ultimo dia es anterior a hoy a las 12... no se ha procesado
                    print "++ WARN ++  1.1 PRIMERA VEZ DEL DIA creamos las URLS y seguimos"
                    urls = BuildUrls(self.mongodbaccess, self.level_log).build_urls()
                    print "-- INFO -- construir urls -- numero de URLS: {0}".format(urls)
                else:
                    # ultimo dia posterior hoy a las 12... esta todo Ok
                    print "++ WARN ++  1.2 SE HA PROCESADO TODO Y NO HAY NADA QUE HACER"
            else:
                if self.find_last_day() < today():
                    # prblemas en el paraiso ayer la cosa no fue bien. Reiniciamos y procesamos
                    print "** ERROR **  2.1 AYER NO SE EJECUTARON TODOS LOS VUELOS"
                    self.logger.error("AYER no se ejecutaron todos los vuelos")
                    urls = BuildUrls(self.mongodbaccess, self.level_log).build_urls()
                    print "-- INFO -- construir urls -- numero de URLS: {0}".format(urls)

                else:
                    #hay cosas que ejecutar
                    print "++ WARN ++  2.2 HA HABIDO UNA CANCELACION y el "\
                          +"SISTEMA SIGUE DESDE ESE PUNTO"
                    self.logger.error("Ha habido una cancelacion y se sigue desde ese punto")
        result = FindFlights(self.config, self.mongodbaccess, self.level_log)\
                   .get_flights(self.return_urls())
        print "++ INFO -- TOTAL PROCESO, Save: {0}".format(result.get("save", 0))
        print "++ INFO -- TOTAL PROCESO, errores sin Informacion: {0}".format(result.get("warn", 0))
        print "++ INFO -- TOTAL PROCESO, errores NO ENCONTRADO: {0}".format(result.get("error", 0))

    def vaciar_dia(self):
        """ delete all info of day """
        return self.mongodbaccess.delete_many("vuelos", {"dBusqueda":{"$gt":today()}})



    def return_urls(self):
        """ doc to explain """
        return self.mongodbaccess.find("urls", {})

    def find_last_day(self):
        """ doc to explain """
        print "++ INFO ++ find_last_day"
        if self.mongodbaccess.find_one("vuelos", {}, sort={"dBusqueda":-1}) is None:
            return datetime.datetime(2000, 01, 01)
        else:
            return self.mongodbaccess.find_one("vuelos", {}, sort={"dBusqueda":-1})\
                                     .get("dBusqueda", "")

def today():
    """return today format datetime with 0 in hour, ... """
    return datetime.datetime(datetime.date.today().year,\
                             datetime.date.today().month,\
                             datetime.date.today().day, 0, 0, 0, 0)

