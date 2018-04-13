#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Clase unique AnalyzerWebJobs """

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

#own classes
from pyproj.logger import Logger


class SeleniumAccess(object):
    """Analyze information of each scrapint of a job and contruct information for save"""

    logger = None
    config = None
    driver = None

    def __init__(self, config, level_log):
        self.logger = Logger(self.__class__.__name__, level_log).get()
        self.config = config

    def open_selenium(self):
        """open driver for scraping"""
        self.logger.debug("Open Selenium")
        self.driver = webdriver.Remote(\
                      command_executor=self.config.get("urlSelenium"),\
                      desired_capabilities=DesiredCapabilities.CHROME)
        self.logger.debug("IS selenium open %r", self.driver != None)

    def close_selenium(self):
        """close driver for scraping"""
        if self.driver != None:
            self.driver.stop_client()
            self.driver.close()
            self.driver = None
