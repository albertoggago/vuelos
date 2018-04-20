#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Test vuelos"""
import sys
import datetime
import json

sys.path.insert(0, "..")
try:
    from pyproj.findflights import FindFlights
    from pyproj.vuelos      import Vuelos
    from pyproj.mongodbaccess import MongoDBAccess
except ImportError:
    print 'No Import'

FILE_CONFIG = "../test/config/configOk.json"
CONFIG5 = json.loads(open(FILE_CONFIG, "r").read())
MONGO_DB_ACCESS5 = MongoDBAccess(CONFIG5, "DEBUG")
FIND_FLIGHTS = FindFlights(CONFIG5, MONGO_DB_ACCESS5, "DEBUG")
VUELOS = Vuelos(FILE_CONFIG, "DEBUG")

def test_find_flights_url_onetrip():
    """test vuelos run bad with file wrong"""

    MONGO_DB_ACCESS5.delete_many("urls", {})
    MONGO_DB_ACCESS5.delete_many("vuelos", {})
    date_direct = datetime.datetime.now() + datetime.timedelta(days=10)
    from_data = "MAD"
    to_data = "DUB"
    url = "https://www.google.es/flights/#flt="+from_data+"."+to_data+"."\
        + date_direct.strftime("%Y-%m-%d")\
        + ";c:EUR;e:1;sd:1;t:f;tt:o"
    insert = {"url" : url, "from" : from_data, "to": to_data, \
              "dateDirect" : date_direct, "dateReturn" : date_direct}
    MONGO_DB_ACCESS5.insert("urls", insert)

    urls = VUELOS.return_urls()
    FIND_FLIGHTS.get_flights(urls)

    vuelos_cursor = MONGO_DB_ACCESS5.find("vuelos", {})
    total_vuelos = sum(1 for result in vuelos_cursor)
    urls_cursor = MONGO_DB_ACCESS5.find("urls", {})
    total_urls = sum(1 for result in urls_cursor)
    vuelo = MONGO_DB_ACCESS5.find_one("vuelos", {})

    assert total_vuelos == 1 or total_urls
    assert vuelo is None

def test_find_flights_url_return():
    """test vuelos run bad with file wrong"""

    MONGO_DB_ACCESS5.delete_many("urls", {})
    MONGO_DB_ACCESS5.delete_many("vuelos", {})
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
    MONGO_DB_ACCESS5.insert("urls", insert)

    urls = VUELOS.return_urls()
    FIND_FLIGHTS.get_flights(urls)

    vuelos_cursor = MONGO_DB_ACCESS5.find("vuelos", {})
    total_vuelos = sum(1 for result in vuelos_cursor)
    urls_cursor = MONGO_DB_ACCESS5.find("urls", {})
    total_urls = sum(1 for result in urls_cursor)
    vuelo = MONGO_DB_ACCESS5.find_one("vuelos", {})

    assert total_vuelos == 1 or total_urls
    assert vuelo is None
