#!/bin/bash
tiempo=1
while :
do
	echo "Presiona [CTRL+C] para parar.."
	python /home/alberto/Documentos/BigData/vuelos/cargarVuelos.py >> /home/alberto/Documentos/BigData/vuelos/cargarVuelos.log
	sleep $tiempo
	((tiempo++))
	echo $tiempo
done