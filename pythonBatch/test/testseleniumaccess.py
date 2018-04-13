#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Test Selenium Access"""
import sys
import json
import urllib2
from selenium.common.exceptions import WebDriverException

sys.path.insert(0, "..")
from pyproj.seleniumaccess import SeleniumAccess


def test_selenium_ok():
    """test_selenium_Ok"""
    config_text = open("../test/config/configOk.json", "r").read()
    config = json.loads(config_text)
    seleniumaccess = SeleniumAccess(config, "DEBUG")
    seleniumaccess.open_selenium()
    assert seleniumaccess.driver != None
    seleniumaccess.close_selenium()

def test_selenium_error():
    """test_selenium_Error"""
    config_text = open("../test/config/configMongoDBError.json", "r").read()
    config = json.loads(config_text)
    seleniumaccess = SeleniumAccess(config, "DEBUG")
    try:
        seleniumaccess.open_selenium()
        assert False
    except urllib2.URLError:
        assert True

def test_selenium_close():
    """test_selenium_close"""
    config_text = open("../test/config/configOk.json", "r").read()
    config = json.loads(config_text)
    seleniumaccess = SeleniumAccess(config, "DEBUG")
    seleniumaccess.open_selenium()
    seleniumaccess.close_selenium()
    assert seleniumaccess.driver is None

def test_driver_ok():
    """test_Driver_Ok"""
    config_text = open("../test/config/configOk.json", "r").read()
    config = json.loads(config_text)
    seleniumaccess = SeleniumAccess(config, "DEBUG")
    seleniumaccess.open_selenium()
    try:
        seleniumaccess.driver.get("http://www.google.es")
        assert True
    except WebDriverException:
        assert False
    seleniumaccess.close_selenium()

def test_driver_malformed_url():
    """test_Driver_Malformed_URL"""
    config_text = open("../test/config/configOk.json", "r").read()
    config = json.loads(config_text)
    seleniumaccess = SeleniumAccess(config, "DEBUG")
    seleniumaccess.open_selenium()
    try:
        seleniumaccess.driver.get("www.google.es")
        assert False
    except WebDriverException:
        assert True
    seleniumaccess.close_selenium()
