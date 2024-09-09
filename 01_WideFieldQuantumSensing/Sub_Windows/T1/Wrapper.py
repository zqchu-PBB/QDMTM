'''
Created on Sep 15, 2015

@author: Kai
'''
import sys
from Sub_Windows.T1.GUI.GUI import Ui_Dialog
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

class GUI_Wrapper_T1(QtWidgets.QDialog):
    def __init__(self, seq, parent=None):
        QtWidgets.QWidget.__init__(self,parent)
        self.seq=seq  # The self.seq can be appened only. You cannot assign values to self.seq, or the pointer of self.seq will be different with the pointer of seq.
        self.ui=Ui_Dialog()
        self.ui.setupUi(self)
        self.mark = False

        try:
            Current_path = os.path.split(os.path.realpath(__file__))[0]
            f = open(Current_path+'\\Info.txt','r')
            Info = f.readlines()
            for item in Info:
                item1 = item.replace('\n','')
                parameter = item1.split(':')
                eval('self.ui.lineEdit_'+parameter[0]+".setText('"+parameter[1]+"')")
            f.close()
            self.ui.label_status.setText('Initialized successfully!')
            print('T1 window initialized successfully!')
            self.Initialize_seq()
            
            png=QtGui.QPixmap(Current_path+'\\sequences.png')
            self.ui.label_picture.setPixmap(png)
        except:
            self.ui.label_status.setText('Initialized unsuccessfully!')
            print('T1 window initialized unsuccessfully!')

        

        self.ui.pushButton_clear.clicked.connect(self.pushButton_clear_clicked)
        self.ui.pushButton_save.clicked.connect(self.pushButton_save_clicked)

    def Initialize_seq(self):
        self.mark = True
        self.MW_power = int(self.ui.lineEdit_MW_power.text())
        self.MW_freq = int(self.ui.lineEdit_MW_freq.text())
        self.aom_duration = int(self.ui.lineEdit_aom_duration.text())
        self.MW_duration = int(self.ui.lineEdit_MW_duration.text())
        self.gap_1 = int(self.ui.lineEdit_gap_1.text())
        self.gap_2 = int(self.ui.lineEdit_gap_2.text())
        self.delay_sweep_start = int(self.ui.lineEdit_delay_sweep_start.text())
        self.delay_sweep_number = int(self.ui.lineEdit_delay_sweep_number.text())
        self.delay_sweep_end = int(self.ui.lineEdit_delay_sweep_end.text())
        self.repetitions = int(self.ui.lineEdit_repetitions.text())
        self.aom_power = self.ui.lineEdit_aom_power.text()

        #delay_duration_sweeping = range(self.delay_sweep_start, self.delay_sweep_end, self.delay_sweep_step)
        t = numpy.linspace(numpy.log(self.delay_sweep_start+1), numpy.log(self.delay_sweep_end+1), self.delay_sweep_number)
        delay_duration_sweeping = numpy.exp(t)
        self.seq.append(self.MW_power)
        self.seq.append(self.MW_freq)
        self.seq.append(self.aom_duration)
        self.seq.append(self.MW_duration)
        self.seq.append(self.gap_1)
        self.seq.append(self.gap_2)
        self.seq.append(delay_duration_sweeping)
        self.seq.append(self.repetitions)
        self.seq.append(self.aom_power)
        
    def pushButton_clear_clicked(self):
        self.ui.lineEdit_MW_power.setText('')
        self.ui.lineEdit_MW_freq.setText('')
        self.ui.lineEdit_aom_duration.setText('')
        self.ui.lineEdit_MW_duration.setText('')
        self.ui.lineEdit_gap_1.setText('')
        self.ui.lineEdit_gap_2.setText('')
        self.ui.lineEdit_delay_sweep_start.setText('')
        self.ui.lineEdit_delay_sweep_number.setText('')  
        self.ui.lineEdit_delay_sweep_end.setText('')
        self.ui.lineEdit_repetitions.setText('')
        self.ui.lineEdit_aom_power.setText('')

        self.ui.label_status.setText('Cleared')

    def pushButton_save_clicked(self):
        if self.mark:
            del self.seq[:]
            
        self.mark = True
        self.MW_power = int(self.ui.lineEdit_MW_power.text())
        self.MW_freq = int(self.ui.lineEdit_MW_freq.text())
        self.aom_duration = int(self.ui.lineEdit_aom_duration.text())
        self.MW_duration = int(self.ui.lineEdit_MW_duration.text())
        self.gap_1 = int(self.ui.lineEdit_gap_1.text())
        self.gap_2 = int(self.ui.lineEdit_gap_2.text())
        self.delay_sweep_start = int(self.ui.lineEdit_delay_sweep_start.text())
        self.delay_sweep_end = int(self.ui.lineEdit_delay_sweep_end.text())
        self.delay_sweep_number = int(self.ui.lineEdit_delay_sweep_number.text())
        self.repetitions = int(self.ui.lineEdit_repetitions.text())
        self.aom_power = self.ui.lineEdit_aom_power.text()


        delay_duration_sweeping = [0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ]
        if self.ui.radioButton_linear.isChecked() == True:
            # delay_duration_sweeping_1 = range(self.delay_sweep_start, self.delay_sweep_end, self.delay_sweep_step)
            # delay_duration_sweeping.extend(delay_duration_sweeping_1)
            pass
            #delay_duration_sweeping.extend(numpy.flipud(delay_duration_sweeping_1))
            delay_duration_sweeping.extend([0, 0, 0, 0, 0])
        elif self.ui.radioButton_log.isChecked() == True:
            t = numpy.linspace(numpy.log(self.delay_sweep_start+6), numpy.log(self.delay_sweep_end), self.delay_sweep_number)
            delay_duration_sweeping_1 = numpy.exp(t).astype(numpy.int)
            delay_duration_sweeping.extend(delay_duration_sweeping_1)
            #delay_duration_sweeping.extend(numpy.flipud(delay_duration_sweeping_1))
            delay_duration_sweeping.extend([0, 0, 0, 0, 0])
        elif self.ui.radioButton_square.isChecked() == True:
            t = numpy.linspace(numpy.sqrt(self.delay_sweep_start+6), numpy.sqrt(self.delay_sweep_end), self.delay_sweep_number)
            delay_duration_sweeping_1 = (t**2).astype(numpy.int)
            delay_duration_sweeping.extend(delay_duration_sweeping_1)
            #delay_duration_sweeping.extend(numpy.flipud(delay_duration_sweeping_1))
            delay_duration_sweeping.extend([0, 0, 0, 0, 0])
        #delay_duration_sweeping = numpy.arange(6,7,0.01)
        print('111111111111111111111111111111111111111111111111111111111111111111111')
        print(numpy.round(delay_duration_sweeping),0)

        self.seq.append(self.MW_power)
        self.seq.append(self.MW_freq)
        self.seq.append(self.aom_duration)
        self.seq.append(self.MW_duration)
        self.seq.append(self.gap_1)
        self.seq.append(self.gap_2)
        self.seq.append(delay_duration_sweeping)
        self.seq.append(self.repetitions)
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
        f.write('MW_duration:'+str(self.MW_duration))
        f.write("\n")
        f.write('gap_1:'+str(self.gap_1))
        f.write("\n")
        f.write('gap_2:'+str(self.gap_2))
        f.write("\n")
        f.write('delay_sweep_start:'+str(self.delay_sweep_start))
        f.write("\n")
        f.write('delay_sweep_end:'+str(self.delay_sweep_end))
        f.write("\n")
        f.write('delay_sweep_number:'+str(self.delay_sweep_number))
        f.write("\n")
        f.write('repetitions:'+str(self.repetitions))
        f.write("\n")
        f.write('aom_power:'+self.aom_power)
        f.write("\n")
        f.close()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    myClass=GUI_Wrapper()

    myClass.show()


    sys.exit(app.exec_())