#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Only a class Logger"""

import logging
import os

class Logger(object):
    """Logger Activate object of logg create a file per name with level log"""

    LOGGING_DIR = "log"

    def __init__(self, name, levelLog):
        name = name.replace('.log', '')
        logger = logging.getLogger('log_namespace.%s' % name)

        logger.setLevel(levelLog)
        if not logger.handlers:
            file_name = os.path.join(self.LOGGING_DIR, '%s.log' % name)
            handler = logging.FileHandler(file_name)
            formatter = logging.Formatter('%(asctime)s %(levelname)s:%(name)s %(message)s')
            handler.setFormatter(formatter)
            handler.setLevel(logging.DEBUG)
            logger.addHandler(handler)
        self._logger = logger

    def get(self):
        """Get the logger for use in a class"""
        return self._logger
