# -*- coding: utf-8 -*-

"""
v.01
Prueba para insertar la prueba de gráfico de barras con episodio de sueño
utilizando Qt designer y generando el código dinámicamente, es decir, sin 
compilar previamente

"""

import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import numpy as np
import os
import selecepisodio

pg.mkQApp()

path = os.path.dirname(os.path.abspath(__file__))
uiFile = os.path.join(path, 'interfaz.ui')
WindowTemplate, TemplateBaseClass = pg.Qt.loadUiType(uiFile)


class DateAxis(pg.AxisItem):
    def tickStrings(self, values, scale, spacing):
        strns = []
        rng = max(values)-min(values)
        #if rng < 120:
        #    return pg.AxisItem.tickStrings(self, values, scale, spacing)
        if rng < 3600*24:
            string = '%H:%M:%S'
            label1 = '%b %d -'
            label2 = ' %b %d, %Y'
        elif rng >= 3600*24 and rng < 3600*24*30:
            string = '%d'
            label1 = '%b - '
            label2 = '%b, %Y'
        elif rng >= 3600*24*30 and rng < 3600*24*30*24:
            string = '%b'
            label1 = '%Y -'
            label2 = ' %Y'
        elif rng >=3600*24*30*24:
            string = '%Y'
            label1 = ''
            label2 = ''
        for x in values:
            try:
                strns.append(time.strftime(string, time.localtime(x)))
            except ValueError:  ## Windows can't handle dates before 1970
                strns.append('')
        try:
            label = time.strftime(label1, time.localtime(min(values)))+time.strftime(label2, time.localtime(max(values)))
        except ValueError:
            label = ''
        #self.setLabel(text=label)
        return strns


class MainWindow(TemplateBaseClass):  
    def __init__(self):
        TemplateBaseClass.__init__(self)
        self.ui = WindowTemplate()
        self.ui.setupUi(self)
        
        #Configurar la gráfica de barras de episodios de sueño
        self.plt = pg.PlotItem()
        self.plt.getViewBox().setMouseEnabled(False, False)
        self.ui.plotBarSueno.setCentralItem(self.plt)
        self.selep = selecepisodio.SelecEpisodio()
        self.barSuenio = self.selep.barSuenio
        self.plt.addItem(self.barSuenio)
        
        #Configurar las gráficas de consumo energético
        win = self.ui.plotConsumo
        self.barConsumo = self.selep.barConsumo
        self.p1 = win.addPlot()
        self.p1.addItem(self.barConsumo)
        self.p1.hideAxis('left')
        self.p1.hideAxis('bottom')
        
        win.nextRow()
        
        axis = DateAxis(orientation='bottom')
        
        self.p2 = win.addPlot()
        self.p2.plot(self.selep.consumoData, pen=(255,0,0), name="Curva consumo", axisItems={'bottom': axis})
        
        #Configurar los botones
        self.ui.next_e_btn.clicked.connect(self.nextEp)
        self.ui.prev_e_btn.clicked.connect(self.prevEp)
        
        
        
        
        """
        #Configurar la gráfica de consumo energético
        self.ui.plotConsumo.setLabel('left', 'Tipo de sueño', units='');
        self.ui.plotConsumo.setLabel('bottom', 'Instante', units='minutos');
        self.ui.plotConsumo.setLabel('left', 'Tipo de sueño', units='');
        self.ui.plotConsumo.setLabel('bottom', 'Instante', units='minutos');
        """
        
        self.show()
        
    def nextEp(self):
        self.plt.clear()
        self.selep.episodioSiguiente()
        self.barSuenio = self.selep.barSuenio
        self.plt.addItem(self.barSuenio)
        self.p1.clear()
        self.p1.addItem(self.selep.barConsumo)
        self.p2.clear()
        self.p2.plot(self.selep.consumoData, pen=(255,0,0), name="Curva consumo")
        
    def prevEp(self):
        self.plt.clear()
        self.selep.episodioAnterior()
        self.barSuenio = self.selep.barSuenio
        self.plt.addItem(self.barSuenio)
        self.p1.clear()
        self.p1.addItem(self.selep.barConsumo)
        self.p2.clear()
        self.p2.plot(self.selep.consumoData, pen=(255,0,0), name="Curva consumo")


#Inicializar interfaz
win = MainWindow()

## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
