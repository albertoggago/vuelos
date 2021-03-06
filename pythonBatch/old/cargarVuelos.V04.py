#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import datetime
import time
import pprint
import re

from pymongo import MongoClient

from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import TimeoutException

import smtplib
from email.mime.text import MIMEText

#import imaplib
#import email
#from email.header import decode_header
#from lxml import html
#from lxml import etree
#from selenium.webdriver.common.keys import Keys
#from selenium.common.exceptions import NoSuchElementException
#import requests
#import string
#import nltk
#from nltk.collocations import *
#from nltk.tokenize import word_tokenize
#from nltk.corpus import stopwords
#from nltk.corpus import brown
#from nltk.probability import FreqDist
#import unicodedata
#import ipgetter





def recursivo (x):
	print x
	if not(x.text is None):
		print x.text.encode('utf-8')
	for z in x:
		recursivo(z)



class Vuelos:

	busquedas = []
	urls = []
	ultimo_dia = datetime.date(2000,01,01)
	dia_hoy    = datetime.datetime(datetime.date.today().year,datetime.date.today().month,datetime.date.today().day,0,0,0,0)
	cantidad_ciclo = 500

	def __init__(self,name):
		self.pp =pprint.PrettyPrinter(depth=6)
  		client = MongoClient('localhost:27017', ssl=True, ssl_ca_certs='/home/alberto/datos/ssl/mongodb.pem', ssl_match_hostname=False) 
  		client.the_database.authenticate("vuelos","vuelosX",source="admin")
  		self.db = client[name]
  		self.param = self.db.busquedas.find_one()
  		if self.param == None:
			print "base de datos parada o param no inicializado"
		else:
			print "-- INFO -- Conexion a base de datos OK"


	def crear_guardar_url(self,datos,dateDirect,dateReturn):
		#url = "https://www.google.es/flights/#search;f=MAD;t=DUB;d=2018-01-10;r=2018-01-31;tt=o;q=madrid+to+dublin"
		url = "https://www.google.es/flights/#search;f="+datos["from"]+";t="+datos["to"]+";d="+dateDirect.strftime("%Y-%m-%d")+";r"+ \
		      "="+dateReturn.strftime("%Y-%m-%d")+";tt="+datos["type"]+";q="+datos["query"]
		existe = self.db.urls.find_one({"url":url})
		if existe == None:
			self.db.urls.insert({"url":url,"from":datos["from"],"to":datos["to"],"dateDirect":dateDirect,\
				                 "dateReturn":dateReturn,"type":datos["type"],"query":datos["query"]})
			return 1
		return 0

	def RepresentsInt(self,s):
		try: 
			int(s)
			return True
		except ValueError:
			return False 
				
	def proceso_urls(self, elementos,visible):
		#ojo ya borra solo
		errores = 0
		errorNoEncontrado = 0
		print "++ INFO ++ Procesar cada URL"
		sumaVuelos = 0
		if len(self.urls)<10:
			elementos = len(self.urls)

		datos = self.urls[:elementos]												
		
		del self.urls[:elementos] 
		if not (visible):
			display = Display(visible=0, size=(1024, 768))
			display.start()
		else:
			print "++ INFO ++ Datos a Procesar {0}".format(len(datos))
		driver = webdriver.Chrome()
		for idx, ele in enumerate(datos):
			if (visible):
				sys.stdout.write("\r" + "progreso {0}/{1}".format(idx,len(datos)))
				sys.stdout.flush()
			url = ele["url"]
			driver.get(url)
			#analizar url:
			#m = re.compile('Mejor(es)? vuelo(s)?')
			m = re.compile("(DESACTIVADO)|(OFF)")
			precios = driver.find_elements_by_tag_name('div')
			for precio in precios:
				#print '******************************************************'
				#print precio.text.encode("ascii","ignore")
				try:
					res = m.search(precio.text)
					if res != None:
						texto = precio.text
						#buscar donde empezar a trabajar
						pos1 = texto.find("Mejor vuelo") 
						pos2 = texto.find("Mejores vuelos") 
						posP = pos1 if pos1 > pos2 else pos2
						posP = texto.find("DESACTIVADO") if posP == -1 else posP
						pos  = texto.find("\n",posP)
						texto=texto[pos+1:]
						pos = texto.find("Mostrar") 
						texto = texto[:pos-1]
						texto = texto.replace("escala\n","escala ")
						texto = texto.replace("escalas\n","escalas ")
						#texto = texto.replace("Cambio de aeropuerto\n","Cambio de aeropuerto ")
						data = texto.split('\n')
						dataNew= []
						for ele2 in data:
							if ele2!="":
								dataNew.append(ele2.encode("ascii","ignore"))
						#colocamos un control por si los primeros datos no son buenos.
						dataNew = dataNew[:(len(dataNew)/6)*6]
						num = 0
						while num*6 < len(dataNew):
							if not (self.RepresentsInt(dataNew[num*6].replace(".","").replace(",",".")) and
								    (len(dataNew[num*6+2].split("  "))>1)):
								print "-- ERROR -- procesar URL *****************"
								print url
								print "texto INIT"
								print texto
								print "texto END"
								print "data INIT"
								print data
								print "data END"
								for numero in range(0,len(dataNew)/6):
									print "precio: {0}, Tipo: {1}, Horas: {2}, Compañia: {3}, Duracin: {4}, Escalas: {5}".\
						            	                                    format(dataNew[numero*6],dataNew[numero*6+1],\
					                    	                                dataNew[numero*6+2],dataNew[numero*6+3],
						                    	                            dataNew[numero*6+4],dataNew[numero*6+5])
								errorNoEncontrado +=1						                    	                            
								if num == 0:						                    	                            
									dataNew = []
									print "NUEVA LONGITUD "
									print len(dataNew)
								else:
									dataNew = dataNew[:num*6]
									print "NUEVA LONGITUD "
									print len(dataNew)
							num +=1

						for numero in range(0,len(dataNew)/6):
							dBusqueda = datetime.datetime.now()
							precio = float(dataNew[numero*6].replace(".","").replace(",","."))
							tipo   = dataNew[numero*6+1]
							horas  = dataNew[numero*6+2].split("  ")
							compania = dataNew[numero*6+3]
							duracion = dataNew[numero*6+4]
							escalas = dataNew[numero*6+5]
							ele = {"dBusqueda":dBusqueda,"precio":precio,"tipo":tipo,"horaS":horas[0],"horaLl":horas[1],\
							       "compañia":compania,"duracion":duracion,"escalas":escalas,"from":ele["from"],"to":ele["to"],\
							       "dateDirect":ele["dateDirect"],"dateReturn":ele["dateReturn"],"type":ele["type"],"query":ele["query"]}
							#print ele
							self.db.vuelos.insert(ele)
							sumaVuelos +=1
						break
				except StaleElementReferenceException as e:
					#print "-- ERROR -- procesar URL *****************"
					#print url
					#los errores son de dias sin vuelos por ejemplo el día 25 de diciembre
					errores +=1
				except TimeoutException as e:
					print "-- ERROR -- TimeOut *****************"
					print url
					errores +=1
				 	

			#print "precio.break2******"
			self.db.urls.remove({"url":url})
		if errores > 0:
			print "-- ERROR -- errores no procesados {0}".format(errores)
		print "-- INFO -- Vuelos guardados: {0:d}".format(sumaVuelos)
		driver.close()
		return ([sumaVuelos,errores,errorNoEncontrado])

	def vaciar_dia(self):
		print "++ INFO ++ Vaciamos informacion del dia"
		print "-- INFO -- dia: {0}".format(self.dia_hoy)
		borrados = self.db.vuelos.delete_many({"dBusqueda":{"$gt":self.dia_hoy}})
		print "-- INFO -- vaciamos informacion -- Vuelos borrados del dia: {0}".format(borrados.deleted_count)
		
	def buscar_elementos_busquedas(self):
		#no buscamos en un correo cargamos los datos de la tabla busquedas y creamos las busquedas
		print "++ INFO ++ BUSCAR_PARAMETROS DE BUSQUEDA"
		#buscar = self.db.busquedas.find()				
		buscar = self.db.busquedas.find({"activa":True})
		self.busquedas = []
		for ele in buscar:
			self.busquedas.append(ele)
		print "-- INFO -- VUELOS A BUSCAR: {0}".format(len(self.busquedas))
			
	def construir_urls(self):
		print "++ INFO ++ construir urls"
		fechaActual = datetime.datetime.now()
		print "-- FECHA ACTUAL: {0}".format(fechaActual)				
		borrados2 = self.db.urls.delete_many({})
		print "-- INFO -- vaciamos informacion -- URLS borradas: {0}".format(borrados2.deleted_count)
		sumaUrls = 0
		for ele in self.busquedas:
			busquedaActiva = False
			dateD = ele["fromDateInit"]
			while (dateD <= ele["fromDateEnd"]):
				if ele["type"]=="o":
					if (dateD>fechaActual):
						#print "Date direct {0}".format(dateD)
						busquedaActiva = True
						sumaUrls += self.crear_guardar_url(ele,dateD,dateD)
				else: 
					dateR = ele["toDateInit"]
					while (dateR <= ele["toDateEnd"]):
						if ((dateD <= dateR) and (dateD>fechaActual)):
							print "Date direct: {0}, return: {1}".format(dateD,dateR)
							sumaUrls += self.crear_guardar_url(ele,dateD,dateR)
							busquedaActiva = True
						dateR = dateR+datetime.timedelta(days=1)
				dateD = dateD+datetime.timedelta(days=1)
			if not busquedaActiva:
				print "-- INFO -- desactivamos la busqueda: {0}".format(ele)		
				self.db.busquedas.update_one({"_id":ele["_id"]},{"$set":{"activa":False}})

		print "-- INFO -- construir urls -- numero de URLS: {0}".format(sumaUrls)

	def cargar_urls(self):
		print "++ INFO ++ cargar urls"
		datos = self.db.urls.find()
		self.urls = []												
		for a in datos:
			self.urls.append(a)
		print "-- INFO -- cargar urls -- numero de URLS: {0}".format(len(self.urls))

	def buscar_dia(self):
		print "++ INFO ++ buscar_dia"
		datos = self.db.vuelos.find().sort([("dBusqueda",-1)]).limit(1)
		for ultimo in datos:
			self.ultimo_dia = ultimo['dBusqueda']
		print "-- INFO -- buscar dia -- dia base de datos: {0}".format(self.ultimo_dia)
		print "-- INFO -- buscar dia -- dia actual: {0}".format(self.dia_hoy)


	def alertaProblemas(self, hora, extra=""):  
		print "++ INFO ++ REVISAMOS SI HAY QUE ENVIAR UN CORREO"
		print "++ INFO ++ hora Ejecucion {0}".format(hora)
		if hora > 12:
			fromEmail = 'albertoggagocurro@albertoggago.es'
			sslServer = 'albertoggago.es'
			pwdServer= 'Gemaxana1973#'

			print "++ INFO ++ ENVIAMOS CORREO DE ALERTA".format(hora)
			smtp_ssl_host = 'mail.albertoggago.es'
			smtp_ssl_port = 465
			username = fromEmail
			password = pwdServer
			sender = fromEmail
			targets = ['albertoggago@gmail.com']
			msg = MIMEText('ERROR EN LA CARGA DE VUELOS '+extra)
			msg['Subject'] = 'ERROR EN LA CARGA DE VUELOS '
			msg['From'] = sender
			msg['To'] = ', '.join(targets)

			server = smtplib.SMTP_SSL(smtp_ssl_host, smtp_ssl_port)
			#server.set_debuglevel(2)
			server.login(username, password)
			server.sendmail(sender, targets, msg.as_string())
			#print msg.as_string()
			server.quit()

	def guardarLog(self, level, texto):
		print "++ INFO ++ GUARDAR LOG"
		error = {}
		error["dBusqueda"] = datetime.datetime.now()
		error["level"] = level
		error["texto"] = texto
		self.db.logs.insert(error)



	def ejecutar(self, nivel,visible=False):
		print "++ INFO ++ MODULO PRINCIPAL MODO DE EJECUCION: {0}".format(nivel)
		

		self.buscar_elementos_busquedas()
		if nivel == "1":
			print "-- INFO -- MODO 1 duro ejecuta y limpia los datos del dia"
			#proceso duro vaciamos informacion y empezamos
			self.vaciar_dia()
			self.construir_urls()
		else:
			print "-- INFO -- MODO 0 suave solo si hay datos que ejecutar"
			#proceso soft miramos si hay algo que procesar 
			self.cargar_urls()
			self.buscar_dia()
			#si no hay nada que procesar o el dia no se ha ejecutado.
			if len(self.urls)==0:
				#no hay nada que ejecutar
				if self.ultimo_dia < self.dia_hoy:
					# ultimo dia es anterior a hoy a las 12... no se ha procesado
					print "++ WARN ++  1.1 PRIMERA VEZ DEL DIA creamos las URLS y seguimos"
					self.construir_urls()
				else:
					# ultimo dia posterior hoy a las 12... esta todo Ok
					print "++ WARN ++  1.2 SE HA PROCESADO TODO Y NO HAY NADA QUE HACER"
					
			else:
				if self.ultimo_dia < self.dia_hoy:
					# prblemas en el paraiso ayer la cosa no fue bien. Reiniciamos y procesamos
					print "** ERROR **  2.1 AYER NO SE EJECUTARON TODOS LOS VUELOS"
					self.guardarLog("ERROR","AYER no se ejecutaron todos los vuelos")
					self.alertaProblemas(23,extra="AYER no se ejecutaron todos los vuelos")
					self.construir_urls()
				else:
					#hay cosas que ejecutar	
					print "++ WARN ++  2.2 HA HABIDO UNA CANCELACION y el SISTEMA SIGUE DESDE ESE PUNTO"
					self.guardarLog("WARN","Ha habido una cancelacion y se sigue desde ese punto")
			if self.ultimo_dia < self.dia_hoy:
				self.alertaProblemas(hora = int(time.strftime("%H")))
			
		self.cargar_urls()
		cantidad = [0,0,0]
		
		while (len(self.urls) > 0):
			cantidadNueva = self.proceso_urls(self.cantidad_ciclo, visible)
			for i in range(0,len(cantidad)):
				cantidad[i] = cantidad[i] + cantidadNueva[i]
		print "++ INFO -- TOTAL PROCESO, vuelos guardados: {0}".format(cantidad[0])
		print "++ INFO -- TOTAL PROCESO, errores sin Informacion: {0}".format(cantidad[1])
		print "++ INFO -- TOTAL PROCESO, errores NO ENCONTRADO: {0}".format(cantidad[2])

if __name__ == '__main__':
	param_type = sys.argv[1] if len(sys.argv)>1 else 0
	param_type = param_type if (param_type in ["0","1"]) else 0
	param_visible = True if len(sys.argv)>2 else False
	print "## INFO ## Inicio: {0}".format(datetime.datetime.now())
	vuelos = Vuelos("vuelos")
	#vuelos.ejecutar(1, visible=True)
	#cambiamos segunda ejecucion para que se procese
	#vuelos.ejecutar(0, visible=True)
	vuelos.ejecutar(param_type, visible=param_visible)
	print "## INFO ## fin: {0}".format(datetime.datetime.now())

