#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Test logger"""
import sys
import os

sys.path.insert(0, "..")
try:
    from pyproj.logger import Logger
except ImportError:
    print 'No Import'

def test_logger_test():
    """Test logger"""
    sys.path.insert(0, "../test")
    try:
        os.remove("log/test.log")
    except OSError:
        print "file don't exist"

    logger = Logger("test", "DEBUG").get()
    logger.error("Error")
    data = open("log/test.log", "r").read()

    assert " ERROR:log_namespace.test Error" in data
