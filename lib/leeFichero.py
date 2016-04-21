# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import numpy as np
import codecs
import sys
from datetime import datetime as dt
from PyQt4 import QtGui

class LeeFichero(object):
    """
    Inicializa la matriz con los valores del csv
    
    Parametros de entrada
    - nombre: nombre del fichero csv que contiene los datos
    """
    def __init__(self, nombre):
        self.nombreFichero = nombre
        self.csv = np.genfromtxt(nombre, delimiter="," , names=True)
        self.nomCols = self.csv.dtype.names
        self.nparams = len(self.nomCols)
        self.sueno = self.csv['Sueño'.encode('iso8859-15')]
        self.clasifSueno = self.csv['Clasificaciones_del_sueño'.encode('iso8859-15')]
        self.flujo = self.csv['Flujo_térmico__media'.encode('iso8859-15')]
        self.temp = self.csv['Temp_cerca_del_cuerpo__media']
        self.tiempo = self.csv['Time'] / 1000
        self.actli = self.csv['Ligera']
        self.actsd = self.csv['Sedentaria']
        self.actmd = self.csv['Moderada']
        self.consm = self.csv['Gasto_energético'.encode('iso8859-15')]
        self.acltrans = self.csv['Acel_transversal__picos']
        self.dias = self.creaDias()
        
    def creaDias(self):
        indices = []
        ini, fin = 0, 0
        for i in range(len(self.tiempo)-1):
            fecha1 = dt.utcfromtimestamp(self.tiempo[i])
            fecha2 = dt.utcfromtimestamp(self.tiempo[i+1])
            if(fecha1.day != fecha2.day):
                fin = i
                indices.append((ini, fin))
                ini = i+1
        indices.append((ini, len(self.tiempo)-1))
        return indices
        #print "Hay %i dias" % len(indices)
        
    def datosPorDia(self, dia, act):
        if(act == 'sueno'):
            return self.sueno[dia[0]:dia[1]+1]
        elif(act == 'tiempo'):
            return self.tiempo[dia[0]:dia[1]+1]
        elif(act == 'temp'):
            return self.temp[dia[0]:dia[1]+1]
        elif(act == 'flujo'):
            return self.flujo[dia[0]:dia[1]+1]
        elif(act == 'actli'):
            return self.actli[dia[0]:dia[1]+1]
        elif(act == 'actsd'):
            return self.actsd[dia[0]:dia[1]+1]
        elif(act == 'actmd'):
            return self.actmd[dia[0]:dia[1]+1]
        elif(act == 'actsd'):
            return self.actsd[dia[0]:dia[1]+1]
        elif(act == 'consm'):
            return self.consm[dia[0]:dia[1]+1]
        elif(act == 'acltrans'):
            return self.acltrans[dia[0]:dia[1]+1]

"""
datos = LeeFichero('../data2.csv')
datos.datosPorDia(datos.dias[2], 'sueno')
print len(datos.datosPorDia(datos.dias[6], 'sueno'))
for i in datos.dias:
    dia = datos.datosPorDia(i, 'tiempo')
    print dt.utcfromtimestamp(dia[0])
    print dt.utcfromtimestamp(dia[len(dia)-1])
           
"""
"""        
class Example(QtGui.QMainWindow):
    def __init__(self):
        super(Example, self).__init__() 
    
        fname = QtGui.QFileDialog.getOpenFileName(self, 'Open file')
        lee = LeeFichero(open(fname, 'r'))
        print lee.nomCols[19]
        print lee.actli
        print lee.nomCols[15]
        print lee.sueno
        print lee.nomCols[17]
        print lee.consm
    
    
app = QtGui.QApplication(sys.argv)
ex = Example()
sys.exit(app.exec_())        

"""