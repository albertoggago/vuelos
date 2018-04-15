#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""process of holidays and date"""

import datetime

from pyproj.logger import Logger


class Holidays(object):
    """ process to calculate holidays """

    logger = None
    bank_holidays = []

    def __init__(self, level_log):
        """load bank holidays 2018 end year """
        self.logger = Logger(self.__class__.__name__, level_log).get()

        self.bank_holidays.append([2018, 5, 7])
        self.bank_holidays.append([2018, 6, 4])
        self.bank_holidays.append([2018, 8, 6])
        self.bank_holidays.append([2018, 10, 29])
        self.bank_holidays.append([2018, 12, 25])
        self.bank_holidays.append([2018, 12, 26])
        self.bank_holidays.append([2018, 12, 27])

    def get_number_holidays(self, date_orig, date_end):
        """ doc to explain """
        num_holidays = 0
        date_index = date_orig
        while date_index <= date_end:
            num_holidays += self.get_holiday(date_index)
            date_index = date_index + datetime.timedelta(days=1)
        return num_holidays

    def get_holiday(self, date):
        """ review if a day is holiday """
        if date.weekday() > 4 or [date.year, date.month, date.day] in self.bank_holidays:
            return 1
        else:
            return 0


