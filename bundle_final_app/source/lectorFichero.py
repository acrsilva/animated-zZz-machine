# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import numpy as np
#import codecs
#import sys
from datetime import datetime as dt
import math
#from PyQt4 import QtGui

DEBUG = 0
PRUEBAS = 0

class Cotas():
    def __init__(self, flujo, temp, consm, acltrans):
        self.flujo_min = 400
        self.flujo_max = 0
        self.temp_min = 100
        self.temp_max = -20
        self.consm_min = 10000
        self.consm_max = 0
        self.acltrans_min = 10000
        self.acltrans_max = 0
        
        for i in range(len(flujo)):
            if(flujo[i] < self.flujo_min):
                self.flujo_min = flujo[i]
            elif(flujo[i] > self.flujo_max):
                self.flujo_max = flujo[i]
            
            if(temp[i] < self.temp_min):
                self.temp_min = temp[i]
            elif(temp[i] > self.temp_max):
                self.temp_max = temp[i]
                
            if(consm[i] < self.consm_min):
                self.consm_min = consm[i]
            elif(consm[i] > self.consm_max):
                self.consm_max = consm[i]    
            
            if(acltrans[i] < self.acltrans_min):
                self.acltrans_min = acltrans[i]
            elif(acltrans[i] > self.acltrans_max):
                self.acltrans_max = acltrans[i]
        

"""
Almacena los valores puros de un fichero csv
Puede separar los datos en días
"""
class Datos():
    def __init__(self, sueno, clasifSueno, flujo, temp, tiempo, actli, actsd, actmd, consm, acltrans, acostado):
        self.sueno = sueno
        self.clasifSueno = clasifSueno
        self.flujo = flujo
        self.temp = temp
        self.tiempo = tiempo #int
        self.actli = actli
        self.actsd = actsd
        self.actmd = actmd
        self.consm = consm
        self.acltrans = acltrans
        self.acostado = acostado
        
        self.cotas = Cotas(self.flujo, self.temp, self.consm, self.acltrans)
    
    #Crea una lista días particionando los datos
    def creaDias(self):
        #Devuelve una lista con los datos de un día concreto
        def datosDia(dia):
            return Datos(self.sueno[dia[0]:dia[1]+1],
                        self.clasifSueno[dia[0]:dia[1]+1],
                        self.flujo[dia[0]:dia[1]+1],
                        self.temp[dia[0]:dia[1]+1],
                        self.tiempo[dia[0]:dia[1]+1],
                        self.actli[dia[0]:dia[1]+1],
                        self.actsd[dia[0]:dia[1]+1],
                        self.actmd[dia[0]:dia[1]+1],
                        self.consm[dia[0]:dia[1]+1],
                        self.acltrans[dia[0]:dia[1]+1],
                        self.acostado[dia[0]:dia[1]+1])
        
        datos_dias = []
        ini, fin = 0, 0
        for i in range(len(self.tiempo)-1):
            fecha1 = dt.fromtimestamp(self.tiempo[i])
            fecha2 = dt.fromtimestamp(self.tiempo[i+1])
            #Nuevo dia si cambia el dia o si es el último
            #if(fecha1.day != fecha2.day or i == len(self.tiempo)-2):
            if((fecha1.day != fecha2.day and fecha1 < fecha2) or i == len(self.tiempo)-2):
                fin = i
                datos_dias.append(datosDia((ini, fin)))
                if(DEBUG == 1):
                    print "ini", dt.fromtimestamp(self.tiempo[ini]), "fin", dt.fromtimestamp(self.tiempo[fin])
                
                ini = i+1
                
        return datos_dias
        
            
"""
Obtiene los datos de un fichero csv y crea los episodios
"""
class LectorFichero(object):
    """
    Inicializa la matriz con los valores del csv
    
    Parametros de entrada
    - nombre: nombre del fichero csv que contiene los datos
    - dias: además de todos los datos, obtener los de cada día separados en 24h de 00 a 00
    
    Atributos:
    - datos_total: una estructura Datos que contiene todos los datos originales del fichero csv
    - datos_dias: una estructura Datos por cada día natural
    """
    def __init__(self, nombre):
        csv = np.genfromtxt(open(nombre, 'r'), delimiter="," , names=True)
        #self.nomCols = self.csv.dtype.names
        #self.nparams = len(self.nomCols)
        self.nombre = nombre
        
        self.sueno = csv['Sueño'.encode('iso8859-15')]
        self.clasifSueno = csv['Clasificaciones_del_sueño'.encode('iso8859-15')]
        self.flujo = csv['Flujo_térmico__media'.encode('iso8859-15')]
        self.temp = csv['Temp_cerca_del_cuerpo__media']
        self.tiempo = csv['Time'] / 1000
        self.actli = csv['Ligera']
        self.actsd = csv['Sedentaria']
        self.actmd = csv['Moderada']
        self.consm = csv['Gasto_energético'.encode('iso8859-15')]
        self.acltrans = csv['Acel_transversal__picos']
        self.acostado = csv['Acostado']
        
        #Filtrar datos erroneos
        self.filtrarDatos()
        #self.comprobarDatos()
        
        #Datos tal cual vienen en el csv, sin particiones
        self.datos_total = Datos(self.sueno, self.clasifSueno, self.flujo, self.temp, self.tiempo, self.actli, self.actsd, self.actmd, self.consm, self.acltrans, self.acostado)
    
    def filtrarDatos(self):
        """ Actualiza los arrays de datos descartando aquellos incorrectos o incompletos """
        def appendValues():
            """ Inserta los datos de una fila completa, que corresponde a un minuto """
            tiempo.append(self.tiempo[i])
            sueno.append(self.sueno[i])
            clasifSueno.append(self.clasifSueno[i])
            flujo.append(self.flujo[i])
            temp.append(self.temp[i])
            actli.append(self.actli[i])
            actsd.append(self.actsd[i])
            actmd.append(self.actmd[i])
            consm.append(self.consm[i])
            acltrans.append(self.acltrans[i])
            acostado.append(self.acostado[i])
        
        def checkNan():
            return math.isnan(self.sueno[i]) or math.isnan(self.clasifSueno[i]) or math.isnan(self.flujo[i]) or math.isnan(self.temp[i]) or math.isnan(self.actli[i]) or math.isnan(self.actsd[i]) or math.isnan(self.actmd[i]) or math.isnan(self.consm[i]) or math.isnan(self.acltrans[i]) or math.isnan(self.acostado[i]) 
            
        numDatos = len(self.tiempo)
        i = 0
        tiempo, sueno, clasifSueno, flujo, temp, actli, actsd, actmd, consm, acltrans, acostado = [], [], [], [], [], [], [], [], [], [], []
        
        #Descartar los datos que no vayan al minuto
        while(i < numDatos-1):
            if(self.tiempo[i] % 60 == 0 and not checkNan()):
                appendValues()
            else:
                if(DEBUG): print "Dato incorrecto: ", i
            i += 1
        
        if(DEBUG): print "Datos originales:", numDatos, "Datos filtrados:", len(tiempo)
        
        self.sueno = sueno
        self.clasifSueno = clasifSueno
        self.flujo = flujo
        self.temp = temp
        self.tiempo = tiempo
        self.actli = actli
        self.actsd = actsd
        self.actmd = actmd
        self.consm = consm
        self.acltrans =  acltrans    
        self.acostado = acostado
        
    def comprobarDatos(self):
        def appendNan():
            sueno.append(np.NaN)
            clasifSueno.append(np.NaN)
            flujo.append(np.NaN)
            temp.append(np.NaN)
            actli.append(np.NaN)
            actsd.append(np.NaN)
            actmd.append(np.NaN)
            consm.append(np.NaN)
            acltrans.append(np.NaN)
        def appendValues():
            sueno.append(self.sueno[i])
            clasifSueno.append(self.clasifSueno[i])
            flujo.append(self.flujo[i])
            temp.append(self.temp[i])
            actli.append(self.actli[i])
            actsd.append(self.actsd[i])
            actmd.append(self.actmd[i])
            consm.append(self.consm[i])
            acltrans.append(self.acltrans[i])
               
        numDatos = len(self.tiempo)
        i=10
        incorrectos = 0
        
        while(self.tiempo[i] % 60 != 0):
            i += 1
        t = self.tiempo[i]
        tiempo, sueno, clasifSueno, flujo, temp, actli, actsd, actmd, consm, acltrans = [], [], [], [], [], [], [], [], [], []

        if(DEBUG == 3):
            print i, self.tiempo[i], t
            raw_input() # PAUSE
            print "----Comprobar datos ", self.nombre, "----"
            print self.tiempo[i], t
            raw_input() # PAUSE
        
        """
        x = i
        while(x < 10):
            print self.tiempo[x+1] - self.tiempo[x]
            x += 1
        raw_input() # PAUSE    
        """
        
        while(i < numDatos-1):
            if(self.tiempo[i] % 60 != 0):
                if(DEBUG == 3):
                    print i
                    raw_input() # PAUSE
                    incorrectos += 1
                #tiempo.append(t)
                #appendNan()
            elif(self.tiempo[i] != t):
                if(DEBUG == 3):
                    print "Desajuste de tiempo en ", i, " ", t, " ", self.tiempo[i]
                    raw_input() # PAUSE
                    incorrectos +=1
                if(self.tiempo[i] > t):
                    k = 0
                    #Si hay un salto de tiempo, rellenar el hueco con NaN
                    while(self.tiempo[i] > t):
                        #print i, self.tiempo[i], t
                        tiempo.append(t)
                        appendNan()
                        t+=60
                        k+=1
                    if(DEBUG == 3):
                        print "nan insertados: ", k
                        raw_input() # PAUSE
                tiempo.append(t)
                appendValues()
                t+=60
            else:
                tiempo.append(t)
                appendValues()
                t += 60
            i += 1
               
        if(DEBUG == 3):
            print "Datos totales: ", numDatos, " incorrectos: ", incorrectos, " datos nuevos: ", len(tiempo)
        self.sueno, self.clasifSueno, self.flujo, self.temp, self.tiempo, self.actli, self.actsd, self.actmd, self.consm, self.acltrans = sueno, clasifSueno, flujo, temp, tiempo, actli, actsd, actmd, consm, acltrans    
       

    def getDatos(self):
        return self.datos_total
        
    def getDatosDias(self):
        datos_dias = self.datos_total.creaDias()
        if(DEBUG == 2):
            print len(datos_dias), 'dias'
            for i in datos_dias:
                print "ini", i.tiempo[0], "fin", i.tiempo[-1]
        return datos_dias



if(PRUEBAS):
    fname = 'Ejemplos/carmen.csv'
    
    fichero = LectorFichero(fname)

    #fichero.getDatosDias()
    #raw_input('Press <ENTER> to continue')
    
    """
    datos.datosPorDia(datos.dias[2], 'sueno')
    print len(datos.datosPorDia(datos.dias[6], 'sueno'))
    for i in datos.dias:
        dia = datos.datosPorDia(i, 'tiempo')
        print dt.utcfromtimestamp(dia[0])
        print dt.utcfromtimestamp(dia[len(dia)-1])
    """
               

