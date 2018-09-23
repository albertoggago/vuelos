#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Find Flights"""

import datetime
import time

from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException

from pyproj.seleniumaccess import SeleniumAccess
from pyproj.holidays import Holidays
from pyproj.logger import Logger


class FindFlights(object):
    """find Flight"""

    seleniumaccess = None
    mongodbaccess = None
    logger = None
    holidays = None

    def __init__(self, config, mongo_db_access, level_log):
        self.logger = Logger(self.__class__.__name__, level_log).get()
        self.mongodbaccess = mongo_db_access
        self.seleniumaccess = SeleniumAccess(config, level_log)
        self.holidays = Holidays(level_log)
        self.logger.info("Inicio: %s", datetime.datetime.now())

    def get_flights(self, urls):
        """ doc to explain """
        self.logger.info("Process each url")
        result = {"save":0, "warn":0, "error":0}

        self.seleniumaccess.open_selenium()
        driver = self.seleniumaccess.driver
        time.sleep(1)
        driver.get("http://www.google.com")
        time.sleep(1)

        for url in urls:
            accumulate_dic(result, self.url_to_flight(url, driver))

        self.seleniumaccess.close_selenium()
        return result

    def url_to_flight(self, url, driver):
        """process each url"""
        driver.get(url.get("url", "http://google.es"))
        try:
            precio_string = driver.find_element_by_class_name("gws-flights-results__price").text
            #navigate
            #driver.find_element_by_class_name("gws-flights-results__more").click()
            #driver.find_element_by_xpath("//*[contains(text(), 'SELECT FLIGHT')]").click()
            if url.get("type", "") == "o":
                type_flight = driver\
                  .find_element_by_class_name("gws-flights-form__menu-label").text
            else:
                type_flight = driver\
                  .find_element_by_class_name("gws-flights-results__price-annotation").text

            url_insert = \
              {"dBusqueda":datetime.datetime.now(),  \
               "precio":float(precio_string[1:].replace(".", "").replace(", ", ".")), \
               "type": type_flight,\
               "horaS":driver.find_element_by_class_name("gws-flights-results__times").text,\
               "horaLl":"",\
               "company":driver.find_element_by_class_name("gws-flights-results__carriers").text,\
               "duracion":driver.find_element_by_class_name("gws-flights-results__duration").text, \
               "escalas":driver \
                .find_element_by_class_name("gws-flights-results__itinerary-stops").text, \
               "from":url.get("from", "XXX"), \
               "to":url.get("to", "XXX"), \
               "dateDirect":url.get("dateDirect", "XXX"), \
               "dateReturn":url.get("dateReturn", "YYY"), \
               "holidays": \
                 self.holidays.get_number_holidays(url.get("dateDirect", "XXX"), \
                                                   url.get("dateReturn", "YYY"))}
            self.logger.debug("Insert url elemento: %s", url_insert)
            self.mongodbaccess.insert("vuelos", url_insert)
            self.mongodbaccess.delete_one("urls", {"url":url.get("url", "")})
            print "from: {0}, to: {1}, dateDirect: {2}, dateReturn: {3}, price: {4}".format(\
                   url_insert["from"], url_insert["to"], \
                   url_insert["dateDirect"].strftime("%Y-%m-%d"), \
                   url_insert["dateReturn"].strftime("%Y-%m-%d"), \
                   url_insert["precio"])
        except StaleElementReferenceException as error_ref:
            print "****************************"
            print url
            print error_ref
            time.sleep(1)
            return {"save":0, "warn":0, "error":1}
        except NoSuchElementException as error_no_such:
            print "****************************"
            print url
            print error_no_such
            time.sleep(1)
            return {"save":0, "warn":1, "error":0}
        except TimeoutException as error_time_out:
            print "-- ERROR -- TimeOut *****************"
            print "****************************"
            print url
            print error_time_out
            return {"save":0, "warn":0, "error":1}
        return {"save":1, "warn":0, "error":0}

def accumulate_dic(dict_big, dict_to_add):
    """get two dicts and add first the data of second"""
    for key, value in dict_to_add.iteritems():
        dict_big[key] = dict_big.get(key, 0) + value
    return dict_big
