#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Test vuelos"""
import sys
import datetime
import json

sys.path.insert(0, "..")
try:
    from pyproj.vuelos import Vuelos
    from pyproj.mongodbaccess import MongoDBAccess
except ImportError:
    print 'No Import'

FILE_CONFIG = "../test/config/configOk.json"
CONFIG4 = json.loads(open(FILE_CONFIG, "r").read())
MONGO_DB_ACCESS4 = MongoDBAccess(CONFIG4, "DEBUG")

def test_vuelos_ok_buld():
    """test vuelos run ok"""
    vuelos = Vuelos("../test/config/configOk.json", "DEBUG")
    assert vuelos.mongodbaccess.status()

def test_vuelos_error_buld():
    """test vuelos run bad with file wrong"""
    vuelos = Vuelos("../test/config/configXX.json", "DEBUG")
    assert not vuelos.mongodbaccess.status()

def test_vuelos_process_url_onetrip():
    """test vuelos run bad with file wrong"""
    vuelos = Vuelos("../test/config/configOk.json", "DEBUG")

    MONGO_DB_ACCESS4.delete_many("urls", {})
    MONGO_DB_ACCESS4.delete_many("vuelos", {})
    date_direct = datetime.datetime.now() + datetime.timedelta(days=10)
    from_data = "MAD"
    to_data = "DUB"
    url = "https://www.google.es/flights/#flt="+from_data+"."+to_data+"."\
        + date_direct.strftime("%Y-%m-%d")\
        + ";c:EUR;e:1;sd:1;t:f;tt:o"
    insert = {"url" : url, "from" : from_data, "to": to_data, \
              "dateDirect" : date_direct, "dateReturn" : date_direct}
    MONGO_DB_ACCESS4.insert("urls", insert)

    vuelos.proceso_urls()

    vuelos_cursor = MONGO_DB_ACCESS4.find("vuelos", {})
    total_vuelos = sum(1 for result in vuelos_cursor)
    urls_cursor = MONGO_DB_ACCESS4.find("urls", {})
    total_urls = sum(1 for result in urls_cursor)
    vuelo = MONGO_DB_ACCESS4.find_one("vuelos", {})

    assert total_vuelos == 1 or total_urls
    assert vuelo is None

def test_vuelos_process_url_return():
    """test vuelos run bad with file wrong"""
    vuelos = Vuelos("../test/config/configOk.json", "DEBUG")

    MONGO_DB_ACCESS4.delete_many("urls", {})
    MONGO_DB_ACCESS4.delete_many("vuelos", {})
    date_direct = datetime.datetime.now() + datetime.timedelta(days=10)
    date_return = datetime.datetime.now() + datetime.timedelta(days=15)
    from_data = "MAD"
    to_data = "DUB"
    url = "https://www.google.es/flights/#flt="+from_data+"."+to_data+"."\
        + date_direct.strftime("%Y-%m-%d")\
        + "*"+to_data+"."+from_data+"."\
        + date_return.strftime("%Y-%m-%d")\
        +";c:EUR;e:1;sd:1;t:f"
    insert = {"url" : url, "from" : from_data, "to": to_data, \
              "dateDirect" : date_direct, "dateReturn" : date_return}
    MONGO_DB_ACCESS4.insert("urls", insert)

    vuelos.proceso_urls()

    vuelos_cursor = MONGO_DB_ACCESS4.find("vuelos", {})
    total_vuelos = sum(1 for result in vuelos_cursor)
    urls_cursor = MONGO_DB_ACCESS4.find("urls", {})
    total_urls = sum(1 for result in urls_cursor)
    vuelo = MONGO_DB_ACCESS4.find_one("vuelos", {})

    assert total_vuelos == 1 or total_urls
    assert vuelo is None
