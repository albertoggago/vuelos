#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""vuelos"""

import datetime
import json

from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException

from pyproj.seleniumaccess import SeleniumAccess
from pyproj.mongodbaccess import MongoDBAccess
from pyproj.holidays import Holidays
from pyproj.logger import Logger
from pyproj.buildurls import BuildUrls


class Vuelos(object):
    """find Flight"""

    urls = []
    seleniumaccess = None
    mongodbaccess = None
    logger = None
    holidays = None

    def __init__(self, file_config, level_log):
        self.level_log = level_log
        self.logger = Logger(self.__class__.__name__, level_log).get()
        try:
            config = json.loads(open(file_config, "r").read())
            self.mongodbaccess = MongoDBAccess(config, level_log)
            self.seleniumaccess = SeleniumAccess(config, level_log)
            self.holidays = Holidays(level_log)
        except IOError:
            self.logger.error("File Error: %s", file_config)
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
            self.cargar_urls()
            #si no hay nada que procesar o el dia no se ha ejecutado.
            if len(self.urls) == 0:
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
        self.cargar_urls()
        cantidad = [0, 0, 0]
        while len(self.urls) > 0:
            cantidad_nueva = self.proceso_urls()
            for i in range(0, len(cantidad)):
                cantidad[i] = cantidad[i] + cantidad_nueva[i]
        print "++ INFO -- TOTAL PROCESO, vuelos guardados: {0}".format(cantidad[0])
        print "++ INFO -- TOTAL PROCESO, errores sin Informacion: {0}".format(cantidad[1])
        print "++ INFO -- TOTAL PROCESO, errores NO ENCONTRADO: {0}".format(cantidad[2])

    def vaciar_dia(self):
        """ delete all info of day """
        return self.mongodbaccess.delete_many("vuelos", {"dBusqueda":{"$gt":today()}})

    def proceso_urls(self):
        """ doc to explain """
        errores = 0
        error_no_encontrado = 0
        print "++ INFO ++ Procesar cada URL"
        suma_vuelos = 0

        self.seleniumaccess.open_selenium()
        driver = self.seleniumaccess.driver
        for ele in self.urls:
            url = ele["url"]
            driver.get(url)
            try:
                #print(url)
                d_busqueda = datetime.datetime.now()
                precio_string = driver.find_element_by_class_name("gws-flights-results__price").text
                print precio_string
                precio = float(precio_string[1:].replace(".", "").replace(", ", "."))
                tipo = driver\
                       .find_element_by_class_name("gws-flights-results__price-annotation").text
                hora_s = driver.find_element_by_class_name("gws-flights-results__times").text
                compania = driver.find_element_by_class_name("gws-flights-results__carriers").text
                duracion = driver.find_element_by_class_name("gws-flights-results__duration").text
                escalas = driver\
                        .find_element_by_class_name("gws-flights-results__itinerary-stops").text
                #navigate
                #driver.find_element_by_class_name("gws-flights-results__more").click()
                #driver.find_element_by_xpath("//*[contains(text(), 'SELECT FLIGHT')]").click()
                ele_insert = {"dBusqueda":d_busqueda, "precio":precio, \
                       "type":tipo, "horaS":hora_s, \
                       "horaLl":"", "company":compania, "duracion":duracion, \
                       "escalas":escalas, "from":ele["from"], "to":ele["to"], \
                           "dateDirect":ele["dateDirect"], "dateReturn":ele["dateReturn"], \
                       "holidays": \
                          self.holidays.get_number_holidays(ele["dateDirect"], ele["dateReturn"])}
                #print(ele_insert)
                self.mongodbaccess.insert("vuelos", ele_insert)
                suma_vuelos += 1
                self.mongodbaccess.delete_one("urls", {"url":url})
            except StaleElementReferenceException as error_ref:
                errores += 1
                print "****************************"
                print url
                print error_ref
            except NoSuchElementException as error_no_such:
                errores += 1
                print "****************************"
                print url
                print error_no_such
            except TimeoutException as error_time_out:
                print "-- ERROR -- TimeOut *****************"
                print "****************************"
                print url
                print error_time_out
                errores += 1
        if errores > 0:
            print "-- ERROR -- errores no procesados {0}".format(errores)
        print "-- INFO -- Vuelos guardados: {0:d}".format(suma_vuelos)
        self.seleniumaccess.close_selenium()
        return([suma_vuelos, errores, error_no_encontrado])


    def cargar_urls(self):
        """ doc to explain """
        print "++ INFO ++ cargar urls"
        datos = self.mongodbaccess.find("urls", {})
        self.urls = []
        for url in datos:
            self.urls.append(url)
        print "-- INFO -- cargar urls -- numero de URLS: {0}".format(len(self.urls))

    def find_last_day(self):
        """ doc to explain """
        print "++ INFO ++ find_last_day"
        if self.mongodbaccess.find_one("vuelos", {}, sort={"dBusqueda":-1}) is None:
            return datetime.datetime(2000, 01, 01)
        else:
            return self.mongodbaccess.find_one("vuelos", {}, sort={"dBusqueda":-1}).get("dBusqueda","")

    def limpiar(self):
        """ doc to explain """
        print "++INFO-- LIMPIAR FASE I"
        #detectamos todos los vuelos con mas de 7 dias y me quedo con el mejor precio.
        fecha7 = datetime.datetime.now()-datetime.timedelta(days=7)
        proceso = []
        proceso.append({'$match':{'dateDirect':{'$lt':fecha7}}})
        proceso.append({'$group':{'_id':{'dateDirect':'$dateDirect',\
                        'from':'$from', 'to':'$to', 'horaS':'$horaS'},\
                        'suma':{'$sum':1}, 'precio':{'$min':'$precio'}}})
        proceso.append({'$match':{'suma':{'$gt':1}}})
        aggregate_find = self.mongodbaccess.aggregate("vuelos", proceso)
        suma = 0
        borrados = 0
        movidos = 0
        for elemento in aggregate_find:
            #procedemos a seleccionar copiar a vuelosBK
            vuelos_find = self.mongodbaccess.find("vuelos",\
                                              {'dateDirect':elemento['_id']['dateDirect'],\
                                              'from':elemento['_id']['from'], \
                                              'to':elemento['_id']['to'],\
                                              'horaS':elemento['_id']['horaS']})
            mejor_precio = False
            for ele_mover in vuelos_find:
                if(not mejor_precio) and(ele_mover['precio'] == elemento['precio']):
                    mejor_precio = True
                else:
                    self.mongodbaccess.delete_one("vuelos", {'_id':ele_mover['_id']})
                    borrados += 1
                    del ele_mover['_id']
                    self.mongodbaccess.insert("vuelosBk", ele_mover)
                    movidos += 1
            print elemento
            suma += 1
        print "TOTAL: procesados {0}, borrados {1}, movidos {2}".format(suma, borrados, movidos)

def today():
    """return today format datetime with 0 in hour, ... """
    return datetime.datetime(datetime.date.today().year,\
                             datetime.date.today().month,\
                             datetime.date.today().day, 0, 0, 0, 0)

