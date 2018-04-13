#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Load flights"""

import sys
import datetime

from pyproj.vuelos import Vuelos

if __name__ == '__main__':
    PARAM_TYPE = sys.argv[1] if len(sys.argv) > 1 else 0
    PARAM_TYPE = PARAM_TYPE if (PARAM_TYPE in ["0", "1"]) else 0
    print "## INFO ## Inicio: {0}".format(datetime.datetime.now())
    VUELOS = Vuelos("./config/config.json", "DEBUG")
    #cambiamos segunda ejecucion para que se procese
    VUELOS.ejecutar(PARAM_TYPE)
    VUELOS.limpiar()
    print "## INFO ## fin: {0}".format(datetime.datetime.now())


