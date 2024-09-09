'''
Created on Sep 15, 2015

@author: Kai
'''
import sys
from Sub_Windows.CW_ODMR.GUI.GUI import Ui_Dialog
from PyQt5 import QtCore, QtWidgets
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

class GUI_Wrapper_CW_ODMR(QtWidgets.QDialog):
    def __init__(self, seq, parent=None):
        QtWidgets.QWidget.__init__(self,parent)
        self.seq=seq  # The self.seq can be appened only. You cannot assign values to self.seq, or the pointer of self.seq will be different with the pointer of seq.
        self.ui=Ui_Dialog()
        self.ui.setupUi(self)
        self.ui.pushButton_clear.clicked.connect(self.pushButton_clear_clicked)
        self.ui.pushButton_save.clicked.connect(self.pushButton_save_clicked)
        self.mark = False

        try:
            Current_path = os.path.split(os.path.realpath(__file__))[0]
            f = open(Current_path+'\\Info.txt','r')
            Info = f.readlines()
            for item in Info:
                item1 = item.replace('\n', '')
                parameter = item1.split(':')
                parameter[1].replace('\n', '')
                eval('self.ui.lineEdit_'+parameter[0]+".setText('"+parameter[1]+"')")
            f.close()
            self.ui.label_status.setText('Initialized successfully!')
            self.Initialize_seq()
        except:
            self.ui.label_status.setText('Initialized unsuccessfully!')
            print('Rabi window initialized unsuccessfully!')
    
    def Initialize_seq(self):
        self.mark = True
        self.MW_power = int(self.ui.lineEdit_MW_power.text())
        self.freq_start = int(self.ui.lineEdit_freq_start.text())
        self.freq_step = int(self.ui.lineEdit_freq_step.text())
        self.freq_end = int(self.ui.lineEdit_freq_end.text())
        self.camera_exposure = int(self.ui.lineEdit_camera_exposure.text())
        self.aomVoltage = self.ui.lineEdit_AOM_Voltage.text()
        self.aomCurrent = '1'

        MW_freq_seq = range(self.freq_start, self.freq_end, self.freq_step)
        self.seq.append(self.MW_power)
        self.seq.append(MW_freq_seq)
        self.seq.append(self.camera_exposure)
        self.seq.append(self.aomVoltage)
        self.seq.append(self.aomCurrent)
        
    def pushButton_clear_clicked(self):
        self.ui.lineEdit_MW_power('')
        self.ui.lineEdit_freq_start('')
        self.ui.lineEdit_freq_step('')
        self.ui.lineEdit_freq_end('')
        self.ui.lineEdit_camera_exposure.setText('')
        self.ui.lineEdit_AOM_start.setText('')
        self.ui.lineEdit_AOM_end.setText('')
        self.ui.lineEdit_AOM_duration.setText('')
        self.ui.lineEdit_repetitions.setText('')
        self.ui.lineEdit_AOM_Voltage.setText('')
        self.ui.lineEdit_AOM_Current.setText('')
        self.ui.label_status.setText('Cleared')

    def pushButton_save_clicked(self):
        if self.mark:
            del self.seq[:]
            
        self.mark = True
        self.MW_power = int(self.ui.lineEdit_MW_power.text())
        self.freq_start = int(self.ui.lineEdit_freq_start.text())
        self.freq_step = int(self.ui.lineEdit_freq_step.text())
        self.freq_end = int(self.ui.lineEdit_freq_end.text())
        self.camera_exposure = int(self.ui.lineEdit_camera_exposure.text())
        self.aomVoltage = self.ui.lineEdit_AOM_Voltage.text()
        self.aomCurrent = '1'

        MW_freq_seq = range(self.freq_start, self.freq_end, self.freq_step)
        self.seq.append(self.MW_power)
        self.seq.append(MW_freq_seq)
        self.seq.append(self.camera_exposure)
        self.seq.append(self.aomVoltage)
        self.seq.append(self.aomCurrent)

        Current_path = os.path.split(os.path.realpath(__file__))[0]
        f = open(Current_path+'\\Info.txt','w')  #If the file doesn't exist, it will be created automatically. 若文件不存在，系统自动创建。'a'表示可连续写入到文件，保留原内容，在原内容之后写入。可修改该模式（'w+','w','wb'等）
        f.write('MW_power:'+str(self.MW_power))
        f.write("\n")
        f.write('freq_start:'+str(self.freq_start))
        f.write("\n")
        f.write('freq_step:'+str(self.freq_step))
        f.write("\n")
        f.write('freq_end:'+str(self.freq_end))
        f.write("\n")
        f.write('camera_exposure:'+str(self.camera_exposure))
        f.write("\n")
        f.write('AOM_Voltage:'+str(self.aomVoltage))
        f.write("\n")
        f.close()

        self.ui.label_status.setText('Saved')
        #print(self.seq)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    myClass=GUI_Wrapper()

    myClass.show()


    sys.exit(app.exec_())