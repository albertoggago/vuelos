#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""vuelos"""

import datetime
import time
import json
#import smtplib
from email.mime.text import MIMEText

from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException

from pyproj.seleniumaccess import SeleniumAccess
from pyproj.mongodbaccess import MongoDBAccess
from pyproj.holidays import Holidays
from pyproj.logger import Logger
from pyproj.construirurls import ConstruirUrls


class Vuelos(object):
    """find Flight"""

    eurls = []
    ultimo_dia = datetime.datetime(2000, 01, 01)
    dia_hoy = datetime.datetime(datetime.date.today().year,\
                 datetime.date.today().month, datetime.date.today().day, 0, 0, 0, 0)
    cantidad_ciclo = 500

    seleniumaccess = None
    mongodbaccess = None
    logger = None
    config = None
    holidays = None

    def __init__(self, file_config, level_log):
        self.level_log = level_log
        self.logger = Logger(self.__class__.__name__, level_log).get()
        try:
            self.config = json.loads(open(file_config, "r").read())
            self.mongodbaccess = MongoDBAccess(self.config, level_log)
            self.seleniumaccess = SeleniumAccess(self.config, level_log)
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
            print "-- INFO -- dia: {0}".format(self.dia_hoy)
            borrados = self.vaciar_dia()
            print "-- INFO -- vaciamos informacion -- Vuelos borrados del dia: {0}"\
                  .format(borrados.deleted_count)
            ConstruirUrls(self.mongodbaccess, self.level_log)
        else:
            print "-- INFO -- MODO 0 suave solo si hay datos que ejecutar"
            #proceso soft miramos si hay algo que procesar
            self.cargar_urls()
            self.buscar_dia()
            #si no hay nada que procesar o el dia no se ha ejecutado.
            if len(self.urls) == 0:
                #no hay nada que ejecutar
                if self.ultimo_dia < self.dia_hoy:
                    # ultimo dia es anterior a hoy a las 12... no se ha procesado
                    print "++ WARN ++  1.1 PRIMERA VEZ DEL DIA creamos las URLS y seguimos"
                    ConstruirUrls(self.mongodbaccess, self.level_log)
                else:
                    # ultimo dia posterior hoy a las 12... esta todo Ok
                    print "++ WARN ++  1.2 SE HA PROCESADO TODO Y NO HAY NADA QUE HACER"
            else:
                if self.ultimo_dia < self.dia_hoy:
                    # prblemas en el paraiso ayer la cosa no fue bien. Reiniciamos y procesamos
                    print "** ERROR **  2.1 AYER NO SE EJECUTARON TODOS LOS VUELOS"
                    self.logger.error("AYER no se ejecutaron todos los vuelos")
                    self.alerta_problemas(23, extra="AYER no se ejecutaron todos los vuelos")
                    ConstruirUrls(self.mongodbaccess, self.level_log)
                else:
                    #hay cosas que ejecutar
                    print "++ WARN ++  2.2 HA HABIDO UNA CANCELACION y el "\
                          +"SISTEMA SIGUE DESDE ESE PUNTO"
                    self.logger.error("Ha habido una cancelacion y se sigue desde ese punto")
            if self.ultimo_dia < self.dia_hoy:
                self.alerta_problemas(hora=int(time.strftime("%H")))
        self.cargar_urls()
        cantidad = [0, 0, 0]
        while len(self.urls) > 0:
            cantidad_nueva = self.proceso_urls(self.cantidad_ciclo)
            for i in range(0, len(cantidad)):
                cantidad[i] = cantidad[i] + cantidad_nueva[i]
        print "++ INFO -- TOTAL PROCESO, vuelos guardados: {0}".format(cantidad[0])
        print "++ INFO -- TOTAL PROCESO, errores sin Informacion: {0}".format(cantidad[1])
        print "++ INFO -- TOTAL PROCESO, errores NO ENCONTRADO: {0}".format(cantidad[2])

    def vaciar_dia(self):
        """ delete all info of day """
        return self.mongodbaccess.delete_many("vuelos", {"dBusqueda":{"$gt":self.dia_hoy}})

    def proceso_urls(self, elementos):
        """ doc to explain """
        errores = 0
        error_no_encontrado = 0
        print "++ INFO ++ Procesar cada URL"
        suma_vuelos = 0
        if len(self.urls) < 10:
            elementos = len(self.urls)

        datos = self.urls[:elementos]

        del self.urls[:elementos]
        self.seleniumaccess.open_selenium()
        driver = self.seleniumaccess.driver
        for ele in datos:
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
                       "tipo":tipo, "horaS":hora_s, \
                       "horaLl":"", "company":compania, "duracion":duracion, \
                       "escalas":escalas, "from":ele["from"], "to":ele["to"], \
                           "dateDirect":ele["dateDirect"], "dateReturn":ele["dateReturn"], \
                       "type":ele["type"], "query":ele["query"], \
                       "holidays": self.holidays.get_holidays(ele["dateDirect"], ele["dateReturn"])}
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

    def buscar_dia(self):
        """ doc to explain """
        print "++ INFO ++ buscar_dia"
        datos = self.mongodbaccess.find("vuelos", {}, sort={"dBusqueda":-1}, limite=1)
        for ultimo in datos:
            self.ultimo_dia = ultimo['dBusqueda']
        print "-- INFO -- buscar dia -- dia base de datos: {0}".format(self.ultimo_dia)
        print "-- INFO -- buscar dia -- dia actual: {0}".format(self.dia_hoy)


    def alerta_problemas(self, hora, extra=""):
        """ doc to explain """
        print "++ INFO ++ REVISAMOS SI HAY QUE ENVIAR UN CORREO"
        print "++ INFO ++ hora Ejecucion {0}".format(hora)
        if hora > 12:
            from_email = 'albertoggagocurro@albertoggago.es'
            #ssl_server = 'albertoggago.es'
            #pwd_server = 'Gemaxana1973#'

            print "++ INFO ++ ENVIAMOS CORREO DE ALERTA"
            #smtp_ssl_host = 'mail.albertoggago.es'
            #smtp_ssl_port = 465
            #username = from_email
            #password = pwd_server
            sender = from_email
            targets = ['albertoggago@gmail.com']
            msg = MIMEText('ERROR EN LA CARGA DE VUELOS '+extra)
            msg['Subject'] = 'ERROR EN LA CARGA DE VUELOS '
            msg['From'] = sender
            msg['To'] = ', '.join(targets)

            #agg asteriscamos porque no funciona
            #server = smtplib.SMTP_SSL(smtp_ssl_host, smtp_ssl_port)
            #server.login(username, password)
            #server.sendmail(sender, targets, msg.as_string())
            #server.quit()

    def limpiar(self):
        """ doc to explain """
        print "++INFO -- LIMPIAR FASE I"
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
