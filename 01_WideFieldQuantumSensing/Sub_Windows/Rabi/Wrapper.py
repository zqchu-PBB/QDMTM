'''
Created on Sep 15, 2015

@author: Kai
'''
import sys
from Sub_Windows.Rabi.GUI.GUI import Ui_Dialog
from PyQt5 import QtCore, QtWidgets, QtGui
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from Hardwares.Swabian_PulseStreamer import PulseGenerator
from Hardwares.microwave_sources import SMIQ
import numpy
from PIL import Image
import os
import time
from matplotlib import pyplot as plt
from PyQt5.QtWidgets import QMessageBox, QFileDialog

class GUI_Wrapper_Rabi(QtWidgets.QDialog):
    def __init__(self, seq, parent=None):
        QtWidgets.QWidget.__init__(self,parent)
        self.seq=seq  # The self.seq can be appened only. You cannot assign values to self.seq, or the pointer of self.seq will be different with the pointer of seq.
        self.ui=Ui_Dialog()
        self.ui.setupUi(self)
        self.mark = False

        

        # try:
        Current_path = os.path.split(os.path.realpath(__file__))[0]
        png=QtGui.QPixmap(Current_path+'\\sequences.png')
        self.ui.label_picture.setPixmap(png)
        f = open(Current_path+'\\Info.txt','r')
        Info = f.readlines()
        for item in Info:
            item1 = item.replace('\n','')
            parameter = item1.split(':')
            eval('self.ui.lineEdit_'+parameter[0]+".setText('"+parameter[1]+"')")
        f.close()
        self.ui.label_status.setText('Initialized successfully!')
        print('Rabi window initialized successfully!')
        self.Initialize_seq()
        
        png=QtGui.QPixmap(Current_path+'\\sequences.png')
        self.ui.label_picture.setPixmap(png)

        # except:
        #     self.ui.label_status.setText('Initialized unsuccessfully!')
        #     print('Rabi window initialized unsuccessfully!')

        

        self.ui.pushButton_clear.clicked.connect(self.pushButton_clear_clicked)
        self.ui.pushButton_save.clicked.connect(self.pushButton_save_clicked)

    def Initialize_seq(self):
        self.mark = True
        self.MW_power = int(self.ui.lineEdit_MW_power.text())
        self.MW_freq = int(self.ui.lineEdit_MW_freq.text())
        self.aom_duration = int(self.ui.lineEdit_aom_duration.text())
        self.MW_start = int(self.ui.lineEdit_MW_start.text())
        self.MW_sweep_start = int(self.ui.lineEdit_MW_sweep_start.text())
        self.MW_sweep_step = int(self.ui.lineEdit_MW_sweep_step.text())
        self.MW_sweep_end = int(self.ui.lineEdit_MW_sweep_end.text())
        self.repetitions = int(self.ui.lineEdit_repetitions.text())
        self.gap = int(self.ui.lineEdit_gap.text())
        self.aom_power = self.ui.lineEdit_aom_power.text()
        MW_duration_sweeping = range(self.MW_sweep_start, self.MW_sweep_end, self.MW_sweep_step)  #sweep the MW duration time. The first MW duration time is self.MW_sweep_start, the last one is self.MW_sweep_step. 
        self.seq.append(self.MW_power)
        self.seq.append(self.MW_freq)
        self.seq.append(self.aom_duration)
        self.seq.append(self.MW_start)
        self.seq.append(MW_duration_sweeping)
        self.seq.append(self.repetitions)
        self.seq.append(self.gap)
        self.seq.append(self.aom_power)
        
    def pushButton_clear_clicked(self):
        self.ui.lineEdit_MW_power.setText('')
        self.ui.lineEdit_MW_freq.setText('')

        self.ui.lineEdit_aom_duration.setText('')
        self.ui.lineEdit_MW_start.setText('')
        self.ui.lineEdit_MW_sweep_start.setText('')
        self.ui.lineEdit_MW_sweep_step.setText('')
        self.ui.lineEdit_MW_sweep_end.setText('')  
        self.ui.lineEdit_repetitions.setText('')
        self.ui.lineEdit_gap.setText('')
        self.ui.lineEdit_aom_power.setText('')

        self.ui.label_status.setText('Cleared')

    def pushButton_save_clicked(self):
        if self.mark:
            del self.seq[:]
            
        self.mark = True
        self.MW_power = int(self.ui.lineEdit_MW_power.text())
        self.MW_freq = int(self.ui.lineEdit_MW_freq.text())
        self.aom_duration = int(self.ui.lineEdit_aom_duration.text())
        self.MW_start = int(self.ui.lineEdit_MW_start.text())
        self.MW_sweep_start = int(self.ui.lineEdit_MW_sweep_start.text())
        self.MW_sweep_step = int(self.ui.lineEdit_MW_sweep_step.text())
        self.MW_sweep_end = int(self.ui.lineEdit_MW_sweep_end.text())
        self.repetitions = int(self.ui.lineEdit_repetitions.text())
        self.gap = int(self.ui.lineEdit_gap.text())
        self.aom_power = self.ui.lineEdit_aom_power.text()


        #ccd_seq = [(self.camera_start, 0), (self.camera_exposure, 1)]
        MW_duration_sweeping = range(self.MW_sweep_start, self.MW_sweep_end, self.MW_sweep_step)  #sweep the MW duration time. The first MW duration time is self.MW_sweep_start, the last one is self.MW_sweep_step. 
        #MW_seq = [(self.MW_start, 0), (self.MW_sweep_start, 1)]
        #laser_seq = [(self.MW_start + self.MW_sweep_start + self.gap, 0), (self.AOM_duration, 1)]

        #sequences = [[0, laser_seq], [1, MW_seq]]
        
        #mw_power_seq = range(mw_power_start, mw_power_end, mw_power_step)
        self.seq.append(self.MW_power)
        self.seq.append(self.MW_freq)
        self.seq.append(self.aom_duration)
        self.seq.append(self.MW_start)
        self.seq.append(MW_duration_sweeping)
        self.seq.append(self.repetitions)
        self.seq.append(self.gap)
        self.seq.append(self.aom_power)
        self.ui.label_status.setText('Saved')

        Current_path = os.path.split(os.path.realpath(__file__))[0]
        f = open(Current_path+'\\Info.txt','w')         
        f.write('MW_power:'+str(self.MW_power))
        f.write("\n")
        f.write('MW_freq:'+str(self.MW_freq))
        f.write("\n")
        f.write('aom_duration:'+str(self.aom_duration))
        f.write("\n")
        f.write('MW_start:'+str(self.MW_start))
        f.write("\n")
        f.write('MW_sweep_start:'+str(self.MW_sweep_start))
        f.write("\n")
        f.write('MW_sweep_step:'+str(self.MW_sweep_step))
        f.write("\n")
        f.write('MW_sweep_end:'+str(self.MW_sweep_end))
        f.write("\n")
        f.write('repetitions:'+str(self.repetitions))
        f.write("\n")
        f.write('gap:'+str(self.gap))
        f.write("\n")
        f.write('aom_power:'+self.aom_power)
        f.write("\n")
        f.close()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    myClass=GUI_Wrapper()

    myClass.show()


    sys.exit(app.exec_())