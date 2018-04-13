cd pythonBatch
rm -R logOld
mv log logOld
mkdir log  
python LoadFlights.py "$@"