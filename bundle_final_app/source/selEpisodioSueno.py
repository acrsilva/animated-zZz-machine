# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import sys
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import numpy as np
import time
import datetime
import lectorFichero as lf
import colores

from selEpisodio import Episodio, selEpisodio


PRUEBAS = 0
DEBUG = 0

#FALTA NORMALIZAR LOS DATOS!

class EpisodioSueno():
    def __init__(self, nombre, ep_ini, ep_fin, sueno_ini, sueno_fin, 
            colors, colsAcostado, tiempo, consumo, flujo, temperatura, acelerometro):
        
        self.nombre = nombre
        self.ep_ini = ep_ini
        self.ep_fin = ep_fin
        self.sueno_ini = sueno_ini
        self.sueno_fin = sueno_fin
        
        self.colors = colors
        self.colsAcostado = colsAcostado
        #self.barraSuenio = pg.BarGraphItem(x0=tiempo, width=60, height=1, brushes=colors, pens=colors)
        self.horas = tiempo #Horas int
        self.consumoData = consumo
        self.flujoData = flujo
        #self.flujoDataNA = []
        self.tempData = temperatura
        #self.tempDataNA = []
        self.acelData = acelerometro #Aceler�metro transversal
        #self.metsData = []
        #self.activiData = []
        
        self.totCal = np.nansum(consumo)
        
"""
Obtiene una lista de EpisodioSueno 
"""
class SelEpisodioSueno(object):
    def __init__(self, suenos, csv):
        """
        if(filename != ''):
            self.csv = lf.LectorFichero(filename).getDatos()
            selep = selEpisodio(self.csv, sedentario=False, ligero=False, moderado=False).epFiltro
        else:
        """
        selep = suenos.epFiltro
        self.csv = csv.getDatos()
        self.eps_sueno= []
        for i in selep:
            self.eps_sueno.append(self.initEpisodio(i))
        
        self.limConsumo = self.calculaLimites()
        
    #Crea un EpisodioSueno a partir de un episodio dado
    def initEpisodio(self, episodio):
        #Obtener indices de inicio y fin del episodio completo
        rango = 6 * 60 #Horas antes y despu�s del episodio de sue�o
        ultimo = len(self.csv.tiempo)-1
        if(episodio.ini >= rango):
            ep_ini = episodio.ini-rango
        else:
            ep_ini = 0
        if(episodio.fin + rango > ultimo):
            ep_fin = ultimo
        else:
            ep_fin = episodio.fin + rango
        su_ini, su_fin = episodio.ini, episodio.fin
        
        #COMPROBAR RANGOS
        #Obtener colores antes, durante y despues del episodio
        colors = []
        colors.extend(self.coloreaActividades(ep_ini, su_ini-1))
        colors.extend(self.coloreaSueno(su_ini, su_fin))
        colors.extend(self.coloreaActividades(su_fin+1, ep_fin))    
        
        colsAcostado = self.coloreaAcostado(ep_ini, ep_fin)
        
        return EpisodioSueno(episodio.nombre, ep_ini, ep_fin, su_ini, su_fin, 
                    colors, colsAcostado, self.csv.tiempo[ep_ini:ep_fin+1],
                    self.csv.consm[ep_ini:ep_fin+1], self.csv.flujo[ep_ini:ep_fin+1],
                    self.csv.temp[ep_ini:ep_fin+1], self.csv.acltrans[ep_ini:ep_fin+1])
    
    #Devuelve una lista de colores seg�n la clasificaci�n de sue�o 
    #en el intervalo especificado    
    def coloreaSueno(self, ini, fin):
        colors = []
        num = 0
        for i in self.csv.clasifSueno[ini:fin+1]:
            if(i == 2): #Sue�o ligero
                c = colores.suenoLigero
            elif(i == 4): #Sue�o profundo
                c = colores.suenoProfundo
            elif(i == 5): #Sue�o muy profundo
                c = colores.suenoMuyProfundo
            else: #Despierto
                c = colores.despierto
            colors.append(c)
            num = num + 1
        return colors
    
    #Devuelve una lista de colores seg�n la clasificaci�n de actividad
    #en el intervalo especificado
    #COMPROBAR RANGOS Y VALORES 
    def coloreaActividades(self, ini, fin):
        colors = []
        i = ini
        while(i <= fin):
            if(self.csv.actsd[i]):
                c = colores.sedentario
            elif(self.csv.actli[i]):
                c = colores.ligero
            elif(self.csv.actmd[i]):
                c = colores.moderado
            else:
                print "Error al colorear actividad", i
                c = 'r'
            colors.append(c)
            i += 1
        return colors
    
    def coloreaAcostado(self, ini, fin):
        col_acostado = []
        i = ini
        while(i <= fin):
            if(self.csv.acostado[i]):
                col_acostado.append(colores.acostado)
            else:
                col_acostado.append(colores.despierto)
            i+=1    
        return col_acostado
    
    #Obtiene el mayor consumo de todos los minutos en todos los episodios de sue�o
    def calculaLimites(self):
        M = []
        for i in self.eps_sueno:
            M.append(max(i.consumoData))
        return max(M)
    
if(PRUEBAS==1):
    selep = SelEpisodioSueno('../data.csv').eps_sueno
    for i in selep:
        print i.totCal