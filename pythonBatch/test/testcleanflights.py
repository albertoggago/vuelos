#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Test holidays"""
import json
import datetime
import sys

sys.path.insert(0, "..")
try:
    from pyproj.cleanflights import CleanFlights
    from pyproj.mongodbaccess import MongoDBAccess
except ImportError:
    print 'No Import'

FILE_CONFIG = "../test/config/configOk.json"
CONFIG3 = json.loads(open(FILE_CONFIG, "r").read())
MONGO_DB_ACCESS3 = MongoDBAccess(CONFIG3, "DEBUG")
CLEAN_FLIGHTS = CleanFlights(MONGO_DB_ACCESS3, "DEBUG")

def test_clean_flights_plus_15_days():
    """test clean flights"""
    MONGO_DB_ACCESS3.delete_many("vuelos", {})
    MONGO_DB_ACCESS3.delete_many("vuelosOld", {})
    date = datetime.datetime.now() - datetime.timedelta(days=(15+1))
    insert = {"dBusqueda":"d_busqueda", "precio":100, "type":"x", "horaS":"11:22", \
              "horaLl":"", "company":"ONE", "duracion":"5h 30m", "escalas":"NO", \
              "from":"HOME", "to":"HOLIDAYS", "dateDirect": date, \
              "dateReturn": date, "holidays": 0}
    MONGO_DB_ACCESS3.insert("vuelos", insert)

    sum_urls = CLEAN_FLIGHTS.clean()
    vuelos_cursor = MONGO_DB_ACCESS3.find("vuelos", {})
    total_vuelos = sum(1 for result in vuelos_cursor)
    vuelos_cursor_old = MONGO_DB_ACCESS3.find("vuelosOld", {})
    total_vuelos_old = sum(1 for result in vuelos_cursor_old)

    assert total_vuelos == 0
    assert total_vuelos_old == 1
    assert sum_urls.get("total", 0) == 1
    assert sum_urls.get("deleted", 0) == 1
    assert sum_urls.get("inserted_old", 0) == 1

def test_clean_flights_plus_15_d2():
    """test clean flights"""
    MONGO_DB_ACCESS3.delete_many("vuelos", {})
    MONGO_DB_ACCESS3.delete_many("vuelosOld", {})
    date = datetime.datetime.now() - datetime.timedelta(days=(15+1))
    insert1 = {"dBusqueda":"d_busqueda", "precio":100, "type":"x", "horaS":"11:22", \
              "horaLl":"", "company":"ONE", "duracion":"5h 30m", "escalas":"NO", \
              "from":"HOME", "to":"HOLIDAYS", "dateDirect": date, \
              "dateReturn": date, "holidays": 0}
    date = datetime.datetime.now() - datetime.timedelta(days=(30+1))
    insert2 = {"dBusqueda":"d_busqueda", "precio":1000, "type":"x", "horaS":"11:22", \
              "horaLl":"", "company":"ONE", "duracion":"5h 30m", "escalas":"NO", \
              "from":"HOME", "to":"HOLIDAYS", "dateDirect": date, \
              "dateReturn": date, "holidays": 0}
    MONGO_DB_ACCESS3.insert("vuelos", insert1)
    MONGO_DB_ACCESS3.insert("vuelos", insert2)

    sum_urls = CLEAN_FLIGHTS.clean()
    vuelos_cursor = MONGO_DB_ACCESS3.find("vuelos", {})
    total_vuelos = sum(1 for result in vuelos_cursor)
    vuelos_cursor_old = MONGO_DB_ACCESS3.find("vuelosOld", {})
    total_vuelos_old = sum(1 for result in vuelos_cursor_old)

    assert total_vuelos == 0
    assert total_vuelos_old == 2
    assert sum_urls.get("total", 0) == 2
    assert sum_urls.get("deleted", 0) == 2
    assert sum_urls.get("inserted_old", 0) == 2

def test_clean_flights_plus_15_rep():
    """test clean flights"""
    MONGO_DB_ACCESS3.delete_many("vuelos", {})
    MONGO_DB_ACCESS3.delete_many("vuelosOld", {})
    date = datetime.datetime.now() - datetime.timedelta(days=(15+1))
    insert = {"dBusqueda":"d_busqueda", "precio":100, "type":"x", "horaS":"11:22", \
              "horaLl":"", "company":"ONE", "duracion":"5h 30m", "escalas":"NO", \
              "from":"HOME", "to":"HOLIDAYS", "dateDirect": date, \
              "dateReturn": date, "holidays": 0}
    MONGO_DB_ACCESS3.insert("vuelos", insert)
    vuelo_insert = MONGO_DB_ACCESS3.find_one("vuelos", {})
    MONGO_DB_ACCESS3.insert("vuelosOld", vuelo_insert)

    sum_urls = CLEAN_FLIGHTS.clean()
    vuelos_cursor = MONGO_DB_ACCESS3.find("vuelos", {})
    total_vuelos = sum(1 for result in vuelos_cursor)
    vuelos_cursor_old = MONGO_DB_ACCESS3.find("vuelosOld", {})
    total_vuelos_old = sum(1 for result in vuelos_cursor_old)

    assert total_vuelos == 0
    assert total_vuelos_old == 1
    assert sum_urls.get("total", 0) == 1
    assert sum_urls.get("deleted", 0) == 1
    assert sum_urls.get("inserted_old", 0) == 0

def test_no_clean_flights_min_15_d():
    """test clean flights"""
    MONGO_DB_ACCESS3.delete_many("vuelos", {})
    MONGO_DB_ACCESS3.delete_many("vuelosOld", {})
    date = datetime.datetime.now() - datetime.timedelta(days=(15))
    insert = {"dBusqueda":"d_busqueda", "precio":100, "type":"x", "horaS":"11:22", \
              "horaLl":"", "company":"ONE", "duracion":"5h 30m", "escalas":"NO", \
              "from":"HOME", "to":"HOLIDAYS", "dateDirect": date, \
              "dateReturn": date, "holidays": 0}
    MONGO_DB_ACCESS3.insert("vuelos", insert)

    sum_urls = CLEAN_FLIGHTS.clean()
    vuelos_cursor = MONGO_DB_ACCESS3.find("vuelos", {})
    total_vuelos = sum(1 for result in vuelos_cursor)
    vuelos_cursor_old = MONGO_DB_ACCESS3.find("vuelosOld", {})
    total_vuelos_old = sum(1 for result in vuelos_cursor_old)

    assert total_vuelos == 0
    assert total_vuelos_old == 1
    assert sum_urls.get("total", 0) == 1
    assert sum_urls.get("deleted", 0) == 1
    assert sum_urls.get("inserted_old", 0) == 1

def test_no_clean_flights_min_14_d():
    """test clean flights"""
    MONGO_DB_ACCESS3.delete_many("vuelos", {})
    MONGO_DB_ACCESS3.delete_many("vuelosOld", {})
    date = datetime.datetime.now() - datetime.timedelta(days=(14))
    insert = {"dBusqueda":"d_busqueda", "precio":100, "type":"x", "horaS":"11:22", \
              "horaLl":"", "company":"ONE", "duracion":"5h 30m", "escalas":"NO", \
              "from":"HOME", "to":"HOLIDAYS", "dateDirect": date, \
              "dateReturn": date, "holidays": 0}
    MONGO_DB_ACCESS3.insert("vuelos", insert)

    sum_urls = CLEAN_FLIGHTS.clean()
    vuelos_cursor = MONGO_DB_ACCESS3.find("vuelos", {})
    total_vuelos = sum(1 for result in vuelos_cursor)
    vuelos_cursor_old = MONGO_DB_ACCESS3.find("vuelosOld", {})
    total_vuelos_old = sum(1 for result in vuelos_cursor_old)

    assert total_vuelos == 1
    assert total_vuelos_old == 0
    assert sum_urls.get("total", 0) == 1
    assert sum_urls.get("deleted", 0) == 0
    assert sum_urls.get("inserted_old", 0) == 0

def test_no_clean_flights_actual():
    """test clean flights"""
    MONGO_DB_ACCESS3.delete_many("vuelos", {})
    MONGO_DB_ACCESS3.delete_many("vuelosOld", {})
    date = datetime.datetime.now()
    insert = {"dBusqueda":"d_busqueda", "precio":100, "type":"x", "horaS":"11:22", \
              "horaLl":"", "company":"ONE", "duracion":"5h 30m", "escalas":"NO", \
              "from":"HOME", "to":"HOLIDAYS", "dateDirect": date, \
              "dateReturn": date, "holidays": 0}
    MONGO_DB_ACCESS3.insert("vuelos", insert)

    sum_urls = CLEAN_FLIGHTS.clean()
    vuelos_cursor = MONGO_DB_ACCESS3.find("vuelos", {})
    total_vuelos = sum(1 for result in vuelos_cursor)
    vuelos_cursor_old = MONGO_DB_ACCESS3.find("vuelosOld", {})
    total_vuelos_old = sum(1 for result in vuelos_cursor_old)

    assert total_vuelos == 1
    assert total_vuelos_old == 0
    assert sum_urls.get("total", 0) == 1
    assert sum_urls.get("deleted", 0) == 0
    assert sum_urls.get("inserted_old", 0) == 0
