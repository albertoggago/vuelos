#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Test vuelos"""
import sys

sys.path.insert(0, "..")
try:
    from pyproj.vuelos import Vuelos
except ImportError:
    print 'No Import'

def test_vuelos_ok_buld():
    """test vuelos run ok"""
    vuelos = Vuelos("../config/config.json", "DEBUG")
    assert vuelos.mongodbaccess.status()

def test_vuelos_error_buld():
    """test vuelos run bad with file wrong"""
    vuelos = Vuelos("../config/configXX.json", "DEBUG")
    assert not vuelos.mongodbaccess.status()
