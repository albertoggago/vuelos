#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Test vuelos"""
import sys
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
