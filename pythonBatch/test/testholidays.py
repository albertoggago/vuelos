#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Test holidays"""
import sys
import datetime

sys.path.insert(0, "..")
try:
    from pyproj.holidays import Holidays
except ImportError:
    print 'No Import'

def test_bank_holidays_is():
    """test holidays run ok"""
    holidays = Holidays("DEBUG")
    assert [2018, 5, 7] in holidays.bank_holidays

def test_bank_holidays_not():
    """test holidays run ok"""
    holidays = Holidays("DEBUG")
    assert  [2018, 4, 15] not in holidays.bank_holidays

def test_get_holidays_weekend():
    """test holidays run ok"""
    holidays = Holidays("DEBUG")
    assert  holidays.get_holidays(datetime.datetime(2018, 4, 21),\
                                  datetime.datetime(2018, 4, 22)) == 2

def test_get_holidays_no_weekend():
    """test holidays run ok"""
    holidays = Holidays("DEBUG")
    assert  holidays.get_holidays(datetime.datetime(2018, 4, 23),\
                                  datetime.datetime(2018, 4, 27)) == 0

def test_get_holidays_bankholiday():
    """test holidays run ok"""
    holidays = Holidays("DEBUG")
    assert  holidays.get_holidays(datetime.datetime(2018, 5, 4),\
                                  datetime.datetime(2018, 5, 7)) == 3

def test_get_holiday_weekend():
    """test holidays run ok"""
    holidays = Holidays("DEBUG")
    assert  holidays.get_holiday(datetime.datetime(2018, 4, 21)) == 1

def test_get_holiday_no_weekend():
    """test holidays run ok"""
    holidays = Holidays("DEBUG")
    assert  holidays.get_holiday(datetime.datetime(2018, 4, 23)) == 0

def test_get_holiday_bankholiday():
    """test holidays run ok"""
    holidays = Holidays("DEBUG")
    assert  holidays.get_holiday(datetime.datetime(2018, 5, 7)) == 1
