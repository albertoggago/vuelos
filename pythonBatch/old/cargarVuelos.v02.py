#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pymongo import MongoClient
#import imaplib
import datetime
import pprint
import re
#import email
#import re
#from email.header import decode_header
#from lxml import html
#from lxml import etree
from selenium import webdriver
#from selenium.webdriver.common.keys import Keys
#from selenium.common.exceptions import NoSuchElementException
from pyvirtualdisplay import Display
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
#import smtplib
#from email.mime.text import MIMEText

def recursivo (x):
	print x
	if not(x.text is None):
		print x.text.encode('utf-8')
	for z in x:
		recursivo(z)



class Vuelos:

	def __init__(self,name):
		self.pp =pprint.PrettyPrinter(depth=6)
  		client = MongoClient('localhost:27017') 
  		client.the_database.authenticate("vuelos","vuelosX",source="admin")
  		self.db = client[name]
  		self.param = self.db.busquedas.find_one()
  		if self.param == None:
			print "base de datos parada o param no inicializado"
		else:
			print "-- INFO -- Conexion a base de datos OK"

	def buscar_elementos_buscar(self):
		#no buscamos en un correo cargamos los datos de la tabla busquedas y creamos las busquedas
		print "-- INFO -- BUSCAR_PARAMETROS DE BUSQUEDA"
		buscar = self.db.busquedas.find()				
		self.busquedas = []
		for ele in buscar:
			self.busquedas.append(ele)
		print "-- INFO -- PARAMETROS A BUSCAR: {0}".format(len(self.busquedas))
			
	def construir_urls(self):
		#ojo ya borra solo
		print "-- INFO -- construir urls"
		#quitamos todas las urls anteriores
		self.db.urls.remove()
		fechaActual = datetime.datetime.now()
		print "-- FECHA ACTUAL: {0}".format(fechaActual)				
		sumaUrls = 0
		for ele in self.busquedas:
			dateD = ele["fromDateInit"]
			while (dateD <= ele["fromDateEnd"]):
				if ele["type"]=="o":
					if (dateD>fechaActual):
						#print "Date direct {0}".format(dateD)
						sumaUrls +=1
						self.crear_guardar_url(ele,dateD,dateD)
				else: 
					dateR = ele["toDateInit"]
					while (dateR <= ele["toDateEnd"]):
						if ((dateD <= dateR) and (dateD>fechaActual)):
							print "Date direct: {0}, return: {1}".format(dateD,dateR)
							sumaUrls +=1
							self.crear_guardar_url(ele,dateD,dateR)
						dateR = dateR+datetime.timedelta(days=1)
				dateD = dateD+datetime.timedelta(days=1)
		print "-- INFO -- construir urls -- numero de URLS: {0}".format(sumaUrls)

	def crear_guardar_url(self,datos,dateDirect,dateReturn):
		#url = "https://www.google.es/flights/#search;f=MAD;t=DUB;d=2018-01-10;r=2018-01-31;tt=o;q=madrid+to+dublin"
		url = "https://www.google.es/flights/#search;f="+datos["from"]+";t="+datos["to"]+";d="+dateDirect.strftime("%Y-%m-%d")+";r"+ \
		      "="+dateReturn.strftime("%Y-%m-%d")+";tt="+datos["type"]+";q="+datos["query"]
		existe = self.db.urls.find_one({"url":url})
		if existe == None:
			self.db.urls.insert({"url":url,"from":datos["from"],"to":datos["to"],"dateDirect":dateDirect,\
				                 "dateReturn":dateReturn,"type":datos["type"],"query":datos["query"]})
				
	def buscar_urls(self):
		#ojo ya borra solo
		print "-- INFO -- Buscar informacion de las urls"
		sumaVuelos = 0
		#self.db.vuelos.remove({})
		datos = self.db.urls.find()												
		display = Display(visible=0, size=(1024, 768))
		display.start()
		driver = webdriver.Chrome()
		for ele in datos:
			url = ele["url"]
			driver.get(url)
			#analizar url:
			m = re.compile('Mejores vuelos')
			precios = driver.find_elements_by_tag_name('div')
			for precio in precios:
				res = m.search(precio.text)
				if res != None:
					texto = precio.text
					pos = texto.find("Mejores vuelos") 
					texto=texto[pos+30:]
					pos = texto.find("Mostrar") 
					texto = texto[:pos-1]
					texto = texto.replace("escala\n","escala ")
					data = texto.split('\n')
					dataNew= []
					for ele2 in data:
						if ele2!="":
							dataNew.append(ele2.encode("ascii","ignore"))
							#dataNew.append(ele2.encode("utf-8"))
					#print len(dataNew)/6
					#print len(dataNew)/6.0
					for numero in range(0,len(dataNew)/6):
						#print "precio: {0}, Tipo: {1}, Horas: {2}, Compañia: {3}, Duracin: {4}, Escalas: {5}".\
						#                                                   format(dataNew[numero*6],dataNew[numero*6+1],\
						#	                                                      dataNew[numero*6+2],dataNew[numero*6+3],
						#	                                                      dataNew[numero*6+4],dataNew[numero*6+5])
						dBusqueda = datetime.datetime.now()
						precio = int(dataNew[numero*6])
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
			#print "precio.break2******"

		print "-- INFO -- Vuelos guardados: {0:d}".format(sumaVuelos)
		driver.close()



if __name__ == '__main__':
	print "## INFO ## Inicio: {0}".format(datetime.datetime.now())
	vuelos = Vuelos("vuelos")
	vuelos.buscar_elementos_buscar()
	vuelos.construir_urls()
	vuelos.buscar_urls()
	print "## INFO ## fin: {0}".format(datetime.datetime.now())
