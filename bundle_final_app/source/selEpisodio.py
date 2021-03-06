# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import numpy as np
from datetime import datetime
from scipy.stats import pearsonr
import sys
import colores

reload(sys)
sys.setdefaultencoding('utf8')

DEBUG = 0
PRUEBAS = 0

#Definición de tipos
tipoSueno = "sueño"
tipoSedentario = "sedentario"
tipoLigera = "ligero"
tipoModerado = "moderado"
#Lapso de interrupciones en minutos: sueño, sedentario, ligero, moderado
interrupcion = (35, 7, 4, 3)

#Estructura con la información básica de un episodio
class Episodio():
    def __init__(self, ini, fin, tipo, nombre):
        self.ini = ini
        self.fin = fin
        self.tipo = tipo
        self.nombre = nombre
        
#Episodio con más información que del que hereda
class EpisodioCompleto(Episodio):
    def __init__(self, ini, fin, tipo, nombre, tiempo, temperatura, flujo, consumo):
        Episodio.__init__(self, ini, fin, tipo, nombre)
        self.tiempo = tiempo[self.ini:self.fin+1] #datetime
        self.temp = temperatura[self.ini:self.fin+1]
        self.flujo = flujo[self.ini:self.fin+1]
        self.correlacion, p = pearsonr(self.temp, self.flujo)
        self.consumo = consumo[self.ini:self.fin+1]
        self.numCalorias = np.nansum(consumo[self.ini:self.fin+1])        

"""
Recibe una estructura Datos y unos filtros y particiona en episodios de sueño, sedentario, ligero y moderado
Permite filtrar los episodios por parámetro y mediante la función update

epsCompletos: True para obtener EpisodioCompleto por cada episodio. False para obtener Episodio.
"""
class selEpisodio():
    def __init__(self, csv, epsCompletos=True, sDiurno=True, sNocturno=True, sedentario=True, ligero=True, moderado=True):
        self.csv = csv
        #self.cotas = csv.cotas
        self.epsCompletos = epsCompletos
        
        #Pasar minutos a Datetime. UTIL?
        self.dt = [] 
        for i in self.csv.tiempo:
            #PRUEBAS
            self.dt.append(datetime.fromtimestamp(i))
            #self.dt.append(i)
        
        #Lista de Episodio, sin aplicar filtros
        self.episodios = self.creaEpisodios(self.csv.sueno, self.csv.actsd, self.csv.actli, self.csv.actmd, 5, interrupcion)
        
        #Lista de EpisodioCompleto con los filtros especificados
        self.epFiltro = []
        self.update(sDiurno, sNocturno, sedentario, ligero, moderado)
        
        #Consumo total de todos los datos. UTIL?
        self.totalCal = np.nansum(self.csv.consm)
        
    
    def update(self, sDiurno=True, sNocturno=True, sedentario=True, ligero=True, moderado=True):
        """
        Crea la lista de episodios con los filtros aplicados
        """
        #if(DEBUG>0): print sueno, sedentario, ligero, moderado, len(self.epFiltro)
        if(sDiurno or sNocturno): 
            diurnos, nocturnos = self.getSiestasSuenosIdx()
        
        self.epFiltro = []
        for i in range(len(self.episodios)):
            ep = self.episodios[i]
            if((ep.tipo == tipoSedentario and sedentario)
                or (ep.tipo == tipoLigera and ligero)
                or (ep.tipo == tipoModerado and moderado)
                or (sDiurno and ep.tipo == tipoSueno and self.isDiurno(ep))  #REVISAR
                or (sNocturno and ep.tipo == tipoSueno and not self.isDiurno(ep))):
                if(self.epsCompletos): self.epFiltro.append(EpisodioCompleto(ep.ini, ep.fin, ep.tipo, ep.nombre, 
                                        self.dt, self.csv.temp, self.csv.flujo, self.csv.consm))
                else: self.epFiltro.append(ep)
                    
        if(DEBUG>0):
            print "Total episodios:", len(self.episodios)
            print "Total eps con filtros:", len(self.epFiltro)
            if(DEBUG>2): self.imprimeEpisodios(self.epFiltro)
 
     
    def actualizaEp(self, i, op, lista):
        """
        Elimina episodios de la lista que interrumpen a otro episodio
        incluyéndolos dentro del que interrumpen
        """
        if(op == 2):
            nuevoEp = Episodio(lista[i].ini, lista[i+2].fin, lista[i].tipo, "")
            lista.remove(lista[i+2])
            lista.remove(lista[i+1])
            lista[i] = nuevoEp
        elif(op == 3):
            nuevoEp = Episodio(lista[i].ini, lista[i+3].fin, lista[i].tipo, "")
            lista.remove(lista[i+3])
            lista.remove(lista[i+2])
            lista.remove(lista[i+1])
            lista[i] = nuevoEp
    
    def cortaMinep(self, minep, lista):
        """
        Borra los episodios que no cumplan con el minimo de tamaño
        """
        i = 0
        nums = [0, 0, 0, 0]
        while i < len(lista):
            if lista[i].fin - lista[i].ini + 1 < minep:
                lista.remove(lista[i])
            elif lista[i].tipo == tipoSedentario and lista[i].fin - lista[i].ini + 1 < 7:
                lista.remove(lista[i])
            else:
                i += 1
        i = 0
        while i < len(lista)-1:
            if lista[i].tipo == lista[i+1].tipo:
                lista[i] = Episodio(lista[i].ini, lista[i+1].fin, lista[i].tipo, "")
                lista.remove(lista[i+1])
            self.ponerNombres(lista[i], nums)
            i += 1
        self.ponerNombres(lista[len(lista)-1], nums)
        
    def ponerNombres(self, episodio, nums):
        """
        Pone nombres a los episodios según su tipo y además los enumera
        """
        if episodio.tipo == tipoSueno:
            nums[0] += 1
            episodio.nombre = self.dt[episodio.ini].strftime('%d') + "-Su" + str(nums[0])
        elif episodio.tipo == tipoSedentario:
            nums[1]  += 1
            episodio.nombre = self.dt[episodio.ini].strftime('%d') + "-Se" + str(nums[1])
        elif episodio.tipo == tipoLigera:
            nums[2] += 1
            episodio.nombre = self.dt[episodio.ini].strftime('%d') + "-Li" + str(nums[2])
        elif episodio.tipo == tipoModerado:
            nums[3] += 1
            episodio.nombre = self.dt[episodio.ini].strftime('%d') + "-Mo" + str(nums[3])
        
    def filtraEpisodios(self, minep, intr, lista):
        """
        Crea episodios de las distintas actividades con interrupciones variables
        para cada uno dependiendo de su importancia
        intr son las interrupciones maximas de cada tipo de actividad
            0: maxima interrupcion en un episodio de sueño
            1: maxima interrupcion en un episodio de actv sedentaria
            2: maxima interrupcion en un episodio de actv ligera
            3: maxima interrupcion en un episodio de actv moderada
        """
        i = 0
        while i < len(lista)-3:
            if lista[i].fin - lista[i].ini + 1:
                if lista[i].tipo == lista[i+2].tipo :
                    if(lista[i].tipo == tipoModerado and lista[i+1].fin - lista[i+1].ini < intr[3]):
                        self.actualizaEp(i, 2, lista)
                    elif(lista[i].tipo == tipoSueno and lista[i+1].fin - lista[i+1].ini < intr[0]):
                        self.actualizaEp(i, 2, lista)
                    elif(lista[i].tipo == tipoLigera and lista[i+1].fin - lista[i+1].ini < intr[2]):
                        self.actualizaEp(i, 2, lista)
                    elif(lista[i].tipo == tipoSedentario and lista[i+1].fin - lista[i+1].ini < intr[1]):
                        self.actualizaEp(i, 2, lista)
                    else:
                        i += 1
                elif lista[i].tipo == lista[i+3].tipo :
                    uno = lista[i+1].fin - lista[i+1].ini + 1
                    dos = lista[i+2].fin - lista[i+2].ini + 1
                    if(lista[i].tipo == tipoSueno and uno + dos < intr[0]):
                        self.actualizaEp(i, 3, lista)
                    elif(lista[i].tipo == tipoSedentario and uno + dos < intr[1]):
                        self.actualizaEp(i, 3, lista)
                    elif(lista[i].tipo == tipoLigera and uno + dos < intr[2]):
                        self.actualizaEp(i, 3, lista)
                    elif(lista[i].tipo == tipoModerado and uno + dos < intr[3]):
                        self.actualizaEp(i, 3, lista)
                    else:
                        i += 1
                else:
                    i += 1
            else:
                i += 1
        self.cortaMinep(minep, lista)
        
    
    def encuentraTipo(self, indice, sueno, sed, lig, mod):
        """
        Devuelve el tipo de actividad que se realiza y activa
        el flag de ese tipo
        """
        if(sueno[indice] == 1):
            return tipoSueno, True, False, False, False
        elif(sueno[indice] == 0):
            if(sed[indice] == 1):
                return tipoSedentario, False, True, False, False
            elif(lig[indice] == 1):
                return tipoLigera, False, False, True, False
            elif(mod[indice] == 1):
                return tipoModerado, False, False, False, True

    def selEpisodio(self, sueno, sed, lig, mod):
        """
        Crea los distintos episodios teniendo en cuenta el maximo intervalo
        de interrupcion.
        Devuelve una lista con los indices de inicio y final de cada episodio
        además del tipo de episodio y nombre
        """
        indices = []
        cini, cfin = 0, 0
        tipo, sbool, sedb, ligb, modb = self.encuentraTipo(0, sueno, sed, lig, mod)
        for i in range(len(sueno)-1):
            if(sueno[i+1] == 1 and not sbool):
                cfin = i
                indices.append(Episodio(cini, cfin, tipo, ""))
                tipo, sbool, sedb, ligb, modb = self.encuentraTipo(i+1, sueno, sed, lig, mod)
                cini = i+1
            elif(sueno[i+1] == 0):
                if(sed[i+1] == 1 and not sedb):
                    cfin = i
                    indices.append(Episodio(cini, cfin, tipo, ""))
                    tipo, sbool, sedb, ligb, modb = self.encuentraTipo(i+1, sueno, sed, lig, mod)
                    cini = i+1
                elif(lig[i+1] == 1 and not ligb):
                    cfin = i
                    indices.append(Episodio(cini, cfin, tipo, ""))
                    tipo, sbool, sedb, ligb, modb = self.encuentraTipo(i+1, sueno, sed, lig, mod)
                    cini = i+1
                elif(mod[i+1] == 1 and not modb):
                    cfin = i
                    indices.append(Episodio(cini, cfin, tipo, ""))
                    tipo, sbool, sedb, ligb, modb = self.encuentraTipo(i+1, sueno, sed, lig, mod)
                    cini = i+1
        indices.append(Episodio(cini, len(sueno)-1, tipo, ""))
        return indices
        
    def creaEpisodios(self, sueno, sed, lig, mod, minep, intr):
        """
        listas para crear los episodios: sueño, sedentaria, ligera, moderada
        minep: tamaño minimo de episodio
        intr: interrupciones por actividad
        """
        lista = self.selEpisodio(sueno, sed, lig, mod)
        self.filtraEpisodios(minep, intr, lista)
        return lista
    
        
    def imprimeEpisodios(self, lista):
        for ind in lista:
            if(self.epsCompletos):
                print ind.nombre, ind.ini, ind.fin, "duracion:", ind.fin - ind.ini + 1, ind.tiempo[0], ind.tiempo[-1], 'calorias: ', ind.numCalorias
            else:
                print ind.nombre, ind.ini, ind.fin, "duracion:", ind.fin - ind.ini + 1
    
    def getColorSueno(self, t):
        if(not self.csv.sueno[t]):
            return colores.despierto
        elif(self.csv.clasifSueno[t] == 5):
            return colores.suenoProfundo
        else:
            return "w"
        
    """        
    def getColores(self, ini, fin):
        c = []
        for i in range(ini, fin):
            if(not self.csv.sueno[i]):
                c.append(colores.despierto)
            elif(self.csv.clasifSueno[i] == 5):
                c.append(colores.suenoProfundo)
            else:
                c.append(colores.suenoLigero)
        return c
    """
        
    #Devuelve una lista con los instantes de tiempo donde el paciente está despierto
    def getDespierto(self, ini, fin):
        flag = False
        ii = 0
        rangos = []
        
        for i in range(ini,fin):
            if(not self.csv.sueno[i] and not flag):
                flag = True
                ii = i
            elif(self.csv.sueno[i] and flag):
                flag = False
                rangos.append((self.dt[ii],self.dt[i]))
            elif(i == fin-1 and not self.csv.sueno[i]):
                rangos.append((self.dt[ii],self.dt[i]))
            
        return rangos
    
    #Devuelve una lista con los instantes de tiempo donde el sueño es profundo
    def getProfundo(self, ini, fin):
        flag = False
        ii = 0
        rangos = []
        
        for i in range(ini,fin):
            if(self.csv.clasifSueno[i] ==5 and not flag):
                flag = True
                ii = i
            elif(self.csv.clasifSueno[i] !=5 and flag):
                flag = False
                rangos.append((self.dt[ii],self.dt[i]))
            elif(i == fin-1 and self.csv.clasifSueno[i] ==5):
                rangos.append((self.dt[ii],self.dt[i]))
            
        return rangos
    
    #Devuelve una lista con los índices de los episodios que sean siestas durante el día
    #Teniendo en cuenta que epFiltro contenga los episodios de sueño
    #Se consideran siestas los sueños que empiezan después de las 10 de la mañana y acaban antes
    #de las 10 de la noche
    def getSiestasSuenosIdx(self):
        siestas, suenos = [], []
        eps = self.epFiltro
        for i in range(len(eps)):
            if(eps[i].tiempo[0].hour >= 10 and eps[i].tiempo[0].hour <= 22
                and eps[i].tiempo[-1].hour >= 10 and eps[i].tiempo[-1].hour <= 22):
                siestas.append(i)
            else: suenos.append(i)
        if(DEBUG): 
            print "Sueños diurnos (idx)", siestas
            print "Sueños nocturnos (idx)", suenos
        return siestas, suenos
    
    def isDiurno(self, ep):
        """
        Comprueba si el episodio es diurno o nocturno
        """
        return (self.dt[ep.ini].hour >= 10 and self.dt[ep.ini].hour <= 22
                and self.dt[ep.fin].hour >= 10 and self.dt[ep.fin].hour <= 22)
        
    
if(PRUEBAS==1):
    import lectorFichero as lf
    csv = lf.LectorFichero('../data.csv').getDatos()
    selep = selEpisodio(csv, sDiurno=True, sNocturno=True, sedentario=False, ligero=False, moderado=False)
    selep.imprimeEpisodios(selep.epFiltro)
    
    
if(PRUEBAS==2):
    eps = selEpisodio('../data.csv')
    print len(eps.episodios)
    print "Agrupados"
    for i in range(len(eps.episodios)):
        print eps.episodios[i].nombre, "duracion:", eps.episodios[i].fin - eps.episodios[i].ini + 1
    print len(eps.episodios)


    vs = 0
    for i in range(len(eps.episodios)):
        if (eps.episodios[i].tipo == tipoSueno):
            vs += 1
            print eps.episodios[i].nombre, eps.episodios[i].ini, eps.episodios[i].fin, "duracion:", eps.episodios[i].fin - eps.episodios[i].ini+1

    print len(eps.epsDias)
    for i in range(len(eps.epsDias)):
        print "Dia", i+1
        eps.imprimeEpisodios(eps.epsDias[i])

if(PRUEBAS==3):
    import lectorFichero as lf
    csv = lf.LectorFichero('../data.csv').getDatosDias()
    print len(csv), 'dias'
    
    
