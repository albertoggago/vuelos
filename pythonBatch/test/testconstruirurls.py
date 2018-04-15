#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Test vuelos"""
import sys
import json
import datetime

sys.path.insert(0, "..")
try:
    from pyproj.buildurls import BuildUrls
    from pyproj.mongodbaccess import MongoDBAccess
except ImportError:
    print 'No Import'

FILE_CONFIG = "../test/config/configOk.json"
CONFIG2 = json.loads(open(FILE_CONFIG, "r").read())
MONGO_DB_ACCESS = MongoDBAccess(CONFIG2, "DEBUG")
CONSTRUIR_URLS = BuildUrls(MONGO_DB_ACCESS, "DEBUG")

def test_construir_error():
    """test vuelos run ok"""
    MONGO_DB_ACCESS.delete_many("urls", {})
    MONGO_DB_ACCESS.delete_many("busquedas", {})
    busqueda = {"activa":True}
    MONGO_DB_ACCESS.insert("busquedas", busqueda)

    sum_urls = CONSTRUIR_URLS.build_urls()
    urls_cursor = MONGO_DB_ACCESS.find_one("urls", {})

    assert urls_cursor is None
    assert sum_urls == 0

def test_construir_min():
    """test vuelos run ok"""
    MONGO_DB_ACCESS.delete_many("urls", {})
    MONGO_DB_ACCESS.delete_many("busquedas", {})
    busqueda = {"activa":True,
                "fromDateInit": datetime.datetime(2019, 1, 1),\
                "fromDateEnd": datetime.datetime(2019, 1, 10)}
    MONGO_DB_ACCESS.insert("busquedas", busqueda)

    sum_urls = CONSTRUIR_URLS.build_urls()
    urls_cursor = MONGO_DB_ACCESS.find("urls", {})
    total = sum(1 for result in urls_cursor)

    assert total == 10
    assert sum_urls == 10

def test_construir_min_return_void():
    """test vuelos run ok"""
    MONGO_DB_ACCESS.delete_many("urls", {})
    MONGO_DB_ACCESS.delete_many("busquedas", {})
    busqueda = {"activa":True,
                "fromDateInit": datetime.datetime(2019, 1, 1),\
                "fromDateEnd": datetime.datetime(2019, 1, 10),\
                "toDateInit": datetime.datetime(2019, 1, 1),\
                "toDateEnd": datetime.datetime(2019, 1, 10),\
                "type":"v"}
    MONGO_DB_ACCESS.insert("busquedas", busqueda)

    sum_urls = CONSTRUIR_URLS.build_urls()
    urls_cursor = MONGO_DB_ACCESS.find("urls", {})
    total = sum(1 for result in urls_cursor)

    assert total == 0
    assert sum_urls == 0

def test_construir_min_return_date():
    """test vuelos run ok"""
    MONGO_DB_ACCESS.delete_many("urls", {})
    MONGO_DB_ACCESS.delete_many("busquedas", {})
    busqueda = {"activa":True,
                "fromDateInit": datetime.datetime(2019, 1, 1),\
                "fromDateEnd": datetime.datetime(2019, 1, 10),\
                "toDateInit": datetime.datetime(2019, 1, 1),\
                "toDateEnd": datetime.datetime(2019, 1, 10),\
                "maxDays": 100000,\
                "type":"v"}
    MONGO_DB_ACCESS.insert("busquedas", busqueda)

    sum_urls = CONSTRUIR_URLS.build_urls()
    urls_cursor = MONGO_DB_ACCESS.find("urls", {})
    total = sum(1 for result in urls_cursor)

    assert total == 55
    assert sum_urls == 55

def test_construir_one():
    """test vuelos run ok"""
    MONGO_DB_ACCESS.delete_many("urls", {})
    MONGO_DB_ACCESS.delete_many("busquedas", {})
    busqueda = {"activa":True,
                "fromDateInit": datetime.datetime(2019, 1, 1),\
                "fromDateEnd": datetime.datetime(2019, 1, 1)}
    MONGO_DB_ACCESS.insert("busquedas", busqueda)

    sum_urls = CONSTRUIR_URLS.build_urls()
    urls_cursor = MONGO_DB_ACCESS.find("urls", {})
    total = sum(1 for result in urls_cursor)

    busquedas = MONGO_DB_ACCESS.find_one("busquedas", {})

    assert total == 1
    assert busquedas["activa"]
    assert sum_urls == 1

def test_construir_one_return():
    """test vuelos run ok"""
    MONGO_DB_ACCESS.delete_many("urls", {})
    MONGO_DB_ACCESS.delete_many("busquedas", {})
    busqueda = {"activa":True,
                "fromDateInit": datetime.datetime(2019, 1, 1),\
                "fromDateEnd": datetime.datetime(2019, 1, 1),\
                "toDateInit": datetime.datetime(2019, 1, 1),\
                "toDateEnd": datetime.datetime(2019, 1, 1),\
                "maxDays": 100000,\
                "type":"v"}
    MONGO_DB_ACCESS.insert("busquedas", busqueda)

    sum_urls = CONSTRUIR_URLS.build_urls()
    urls_cursor = MONGO_DB_ACCESS.find("urls", {})
    total = sum(1 for result in urls_cursor)

    busquedas = MONGO_DB_ACCESS.find_one("busquedas", {})

    assert total == 1
    assert busquedas["activa"]
    assert sum_urls == 1

def test_construir_two_five_days():
    """test vuelos run ok"""
    MONGO_DB_ACCESS.delete_many("urls", {})
    MONGO_DB_ACCESS.delete_many("busquedas", {})
    busqueda = {"activa":True,
                "fromDateInit": datetime.datetime(2019, 1, 1),\
                "fromDateEnd": datetime.datetime(2019, 1, 10),\
                "toDateInit": datetime.datetime(2019, 1, 1),\
                "toDateEnd": datetime.datetime(2019, 1, 10),\
                "maxDays": 5,\
                "minDays" : 2,\
                "type":"v"}
    MONGO_DB_ACCESS.insert("busquedas", busqueda)

    sum_urls = CONSTRUIR_URLS.build_urls()
    urls_cursor = MONGO_DB_ACCESS.find("urls", {})
    total = sum(1 for result in urls_cursor)
    urls_cursor2 = MONGO_DB_ACCESS.find("urls", {})
    for result in urls_cursor2:
        print result

    assert total == 30
    assert sum_urls == 30

def test_construir_2_5_1_holiday():
    """test vuelos run ok"""
    MONGO_DB_ACCESS.delete_many("urls", {})
    MONGO_DB_ACCESS.delete_many("busquedas", {})
    busqueda = {"activa":True,
                "fromDateInit": datetime.datetime(2019, 1, 1),\
                "fromDateEnd": datetime.datetime(2019, 1, 10),\
                "toDateInit": datetime.datetime(2019, 1, 1),\
                "toDateEnd": datetime.datetime(2019, 1, 10),\
                "maxDays": 5,\
                "minDays" : 2,\
                "minHolidays" : 1,\
                "type":"v"}
    MONGO_DB_ACCESS.insert("busquedas", busqueda)

    sum_urls = CONSTRUIR_URLS.build_urls()
    urls_cursor = MONGO_DB_ACCESS.find("urls", {})
    total = sum(1 for result in urls_cursor)
    urls_cursor2 = MONGO_DB_ACCESS.find("urls", {})
    for result in urls_cursor2:
        print result

    assert total == 18
    assert sum_urls == 18

def test_construir_2_5_2_holiday():
    """test vuelos run ok"""
    MONGO_DB_ACCESS.delete_many("urls", {})
    MONGO_DB_ACCESS.delete_many("busquedas", {})
    busqueda = {"activa":True,
                "fromDateInit": datetime.datetime(2019, 1, 1),\
                "fromDateEnd": datetime.datetime(2019, 1, 10),\
                "toDateInit": datetime.datetime(2019, 1, 1),\
                "toDateEnd": datetime.datetime(2019, 1, 10),\
                "maxDays": 5,\
                "minDays" : 2,\
                "minHolidays" : 2,\
                "type":"v"}
    MONGO_DB_ACCESS.insert("busquedas", busqueda)

    sum_urls = CONSTRUIR_URLS.build_urls()
    urls_cursor = MONGO_DB_ACCESS.find("urls", {})
    total = sum(1 for result in urls_cursor)
    urls_cursor2 = MONGO_DB_ACCESS.find("urls", {})
    for result in urls_cursor2:
        print result

    assert total == 10
    assert sum_urls == 10

def test_construir_with_data_real():
    """test vuelos run ok"""
    MONGO_DB_ACCESS.delete_many("urls", {})
    MONGO_DB_ACCESS.delete_many("busquedas", {})
    busqueda = {"activa":True,
                "fromDateInit": datetime.datetime(2019, 1, 1),\
                "fromDateEnd": datetime.datetime(2019, 1, 1),\
                "from":"MAD",\
                "to":"DUB",
                "type":"o"}
    MONGO_DB_ACCESS.insert("busquedas", busqueda)

    sum_urls = CONSTRUIR_URLS.build_urls()
    urls_cursor = MONGO_DB_ACCESS.find("urls", {})
    url = urls_cursor.next()

    assert url.get("url", "") == "https://www.google.es/flights/#flt=MAD.DUB.2019-01-01;"\
                               + "c:EUR;e:1;sd:1;t:f;tt:o"
    assert url.get("from", "") == "MAD"
    assert url.get("to", "") == "DUB"
    assert url.get("dateDirect", "") == datetime.datetime(2019, 1, 1)
    assert url.get("dateReturn", "") == datetime.datetime(2019, 1, 1)
    assert url.get("type", "") == "o"
    assert sum_urls == 1

def test_construir_with_data_real_r():
    """test vuelos run ok"""
    MONGO_DB_ACCESS.delete_many("urls", {})
    MONGO_DB_ACCESS.delete_many("busquedas", {})
    busqueda = {"activa":True,
                "fromDateInit": datetime.datetime(2019, 1, 1),\
                "fromDateEnd": datetime.datetime(2019, 1, 1),\
                "toDateInit": datetime.datetime(2019, 1, 2),\
                "toDateEnd": datetime.datetime(2019, 1, 2),\
                "from":"MAD",\
                "to":"DUB",\
                "maxDays": 100000,\
                "type":"v"}
    MONGO_DB_ACCESS.insert("busquedas", busqueda)

    sum_urls = CONSTRUIR_URLS.build_urls()
    urls_cursor = MONGO_DB_ACCESS.find("urls", {})
    url = urls_cursor.next()

    assert url.get("url", "") == "https://www.google.es/flights/#flt=MAD.DUB.2019-01-01*"\
                               + "DUB.MAD.2019-01-02;"\
                               + "c:EUR;e:1;sd:1;t:f"
    assert url.get("from", "") == "MAD"
    assert url.get("to", "") == "DUB"
    assert url.get("dateDirect", "") == datetime.datetime(2019, 1, 1)
    assert url.get("dateReturn", "") == datetime.datetime(2019, 1, 2)
    assert url.get("type", "") == "v"
    assert sum_urls == 1

def test_construir_desactivate():
    """test vuelos run ok"""
    MONGO_DB_ACCESS.delete_many("urls", {})
    MONGO_DB_ACCESS.delete_many("busquedas", {})
    busqueda = {"activa":True,
                "fromDateInit": datetime.datetime(2018, 1, 1),\
                "fromDateEnd": datetime.datetime(2018, 1, 1),\
                "type":"0"}
    MONGO_DB_ACCESS.insert("busquedas", busqueda)

    sum_urls = CONSTRUIR_URLS.build_urls()
    urls_cursor = MONGO_DB_ACCESS.find("urls", {})
    total = sum(1 for result in urls_cursor)
    busquedas = MONGO_DB_ACCESS.find_one("busquedas", {})

    assert total == 0
    assert not busquedas["activa"]
    assert sum_urls == 0

def test_construir_desactivate_ret():
    """test vuelos run ok"""
    MONGO_DB_ACCESS.delete_many("urls", {})
    MONGO_DB_ACCESS.delete_many("busquedas", {})
    busqueda = {"activa":True,
                "fromDateInit": datetime.datetime(2018, 1, 1),\
                "fromDateEnd": datetime.datetime(2018, 1, 1),\
                "toDateInit": datetime.datetime(2018, 1, 1),\
                "toDateEnd": datetime.datetime(2018, 1, 1),\
                "maxDays": 100000,\
                "type":"v"}
    MONGO_DB_ACCESS.insert("busquedas", busqueda)

    sum_urls = CONSTRUIR_URLS.build_urls()
    urls_cursor = MONGO_DB_ACCESS.find("urls", {})
    total = sum(1 for result in urls_cursor)

    busquedas = MONGO_DB_ACCESS.find_one("busquedas", {})

    assert total == 0
    assert not busquedas["activa"]
    assert sum_urls == 0
