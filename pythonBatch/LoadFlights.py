#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Load flights"""

import sys
import datetime

from pyproj.vuelos import Vuelos
from pyproj.cleanflights import CleanFlights

if __name__ == '__main__':
    PARAM_TYPE = sys.argv[1] if len(sys.argv) > 1 else 0
    PARAM_TYPE = PARAM_TYPE if (PARAM_TYPE in ["0", "1"]) else 0
    print "## INFO ## Inicio: {0}".format(datetime.datetime.now())
    VUELOS = Vuelos("./config/config.json", "DEBUG")
    VUELOS.ejecutar(PARAM_TYPE)
    #cambiamos segunda ejecucion para que se procese
    print "## INFO ## Clean Process"
    RESULT = CleanFlights(VUELOS.mongodbaccess, "DEBUG").clean()
    print "CLEAN: process {0}".format(RESULT.get("total", 0))
    print "CLEAN: deleted {0}".format(RESULT.get("deleted", 0))
    print "CLEAN: moved   {0}".format(RESULT.get("inserted_old", 0))
    print "## INFO ## fin: {0}".format(datetime.datetime.now())
