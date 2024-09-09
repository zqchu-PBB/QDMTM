import sys
import os
print(os.getcwd())
loadpath = os.path.dirname(__file__)
os.chdir(loadpath)
print(os.getcwd())
import numpy
import time
from scipy.optimize import curve_fit
import math
from PIL import Image, ImageQt
from numpy.fft import fft2
from GUI.GUI import Ui_MainWindow
from ctypes import *
from PyQt5 import QtWidgets,QtCore, QtGui
from PyQt5.QtWidgets import QMessageBox, QFileDialog

#from Sub_Windows.DelayTimeCalibration.Wrapper import GUI_Wrapper
from Sub_Windows.CW_ODMR.Wrapper import GUI_Wrapper_CW_ODMR
from Sub_Windows.Rabi.Wrapper import GUI_Wrapper_Rabi
from Sub_Windows.T1.Wrapper import GUI_Wrapper_T1

from Threads.Camera_Thread import CameraThread
from Threads.CW_ODMR_Thread import CW_Thread
from Threads.Rabi_Thread import rabi_thread
from Threads.T1_Thread import T1_thread
from Threads.Camera_temperature_monitoring_thread import CameraTemperatureMonitoringThread


from Hardwares.microwave_sources import SMIQ
from Hardwares.Swabian_PulseStreamer import PulseGenerator
from Hardwares.Andor_Camera import CCD
from Hardwares.PI_Stage import PiStage

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure


class mainGUI(QtWidgets.QMainWindow):
    def __init__(self,parent=None):
        QtWidgets.QWidget.__init__(self,parent)
        self.ui=Ui_MainWindow()
        self.ui.setupUi(self)

        #global variables
        self.last_path = None

        self.ODMR_X = []
        self.ODMR_Y = []
        self.ODMR_X_fit = []
        self.ODMR_Y_fit = []
        self.Rabi_X_WithOutMW = []
        self.Rabi_Y_WithOutMW = []
        self.folder_path = []

        self.ROI = numpy.ones((512,512), numpy.uint16)

        self.t1 = 0

        self.image = []
        self.image_save_path = []

    # ODMR Panel
        fig=Figure()
        self.ui.mplPlotODMR=FigureCanvas(fig)
        self.ui.mplPlotODMR.setParent(self.ui.widget_ODMR)
        self.ui.mplPlotODMR.axes=fig.add_subplot(111)
        self.ui.mplPlotODMR.setGeometry(QtCore.QRect(QtCore.QPoint(0,0),self.ui.widget_ODMR.size()))

        # Initialize counts plot. The global variable self.Rabi_Plot_WithOutMW is also used for the OMDR_Fitting drawing
        # And the global variable self.ODMR_Plot is also used for the Rabi signal with MW
        self.ODMR_Plot,=self.ui.mplPlotODMR.axes.plot([2.75,2.80,2.85,2.90,2.95,3.0],[0,0,0,0,0,0])
        self.Rabi_Plot_WithOutMW,=self.ui.mplPlotODMR.axes.plot([2.75,2.80,2.85,2.90,2.95,3.0],[1,1,1,1,1,1])
        self.ui.mplPlotODMR.axes.set_xlabel('Frequency (GHz)')
        self.ui.mplPlotODMR.figure.subplots_adjust(top=0.95,bottom=0.2,right=0.99)
        self.ui.mplPlotODMR.draw()

        self.ui.mplTb=NavigationToolbar(self.ui.mplPlotODMR,self.ui.tbwidget_odmr)
        self.ui.mplTb.setParent(self.ui.tbwidget_odmr)
        self.ui.mplTb.setGeometry(QtCore.QRect(QtCore.QPoint(0,0),self.ui.tbwidget_odmr.size()))


        
        self.ui.pushButton_live.clicked.connect(self.pushButton_live_clicked)  # This is for the 'Live' button in camera panel
        self.ui.pushButton_stop.clicked.connect(self.pushButton_stop_clicked)
        self.ui.pushButton_snapshot.clicked.connect(self.pushButton_snapshot_clicked)
        self.ui.pushButton_clear_roi.clicked.connect(self.pushButton_clear_roi_clicked)
        self.ui.pushButton_select_image_save_path.clicked.connect(self.pushButton_select_image_save_path_clicked) # This is for the 'save path' button in camera panel
        self.ui.pushButton_save_image.clicked.connect(self.pushButton_save_image_clicked) # This is for the 'save' button in camera panel
        self.ui.pushButton_turn_off_camera.clicked.connect(self.pushButton_turn_off_camera_clicked)
        self.ui.pushButton_andor_cooler_on.clicked.connect(self.pushButton_andor_cooler_on_clicked)
        self.ui.pushButton_andor_temperature_check.clicked.connect(self.pushButton_andor_temperature_check_clicked)
        self.ui.pushButton_andor_cooler_off.clicked.connect(self.pushButton_andor_cooler_off_clicked)
        # self.ui.pushButton_turn_off_camera.clicked.connect(self.pushButton_Turn_Off_Camera_Clicked)
        # self.ui.lineEdit_ExposureTime.textChanged.connect(self.lineEdit_ExposureTime_textChanged)
        # self.ui.pushButton_pulsed_start.clicked.connect(self.pushButton_pulsed_start_clicked)
        # self.ui.pushButton_laser_on.clicked.connect(self.pushButton_laser_on_clicked)
        # self.ui.pushButton_laser_off.clicked.connect(self.pushButton_laser_off_clicked)
        # self.ui.pushButton_MW_set.clicked.connect(self.pushButton_MW_set_Clicked)
        # self.ui.pushButton_MW_on.clicked.connect(self.pushButton_MW_on_Clicked)
        # self.ui.pushButton_MW_off.clicked.connect(self.pushButton_MW_off_Clicked)

        self.ui.pushButton_select_quantum_measurement_save_path.clicked.connect(self.pushButton_select_quantum_measurement_save_path_clicked)
        self.ui.pushButton_start_quantum_measurement.clicked.connect(self.pushButton_start_quantum_measurement_clicked)
        self.ui.pushButton_stop_quantum_measurement.clicked.connect(self.pushButton_stop_quantum_measurement_clicked)

        
        # self.ui.pushButton_Pulsed_Stop.clicked.connect(self.pushButton_Pulsed_Stop_clicked)

        self.ui.radioButton_cw_odmr.clicked.connect(self.radioButton_cw_odmr_clicked)
        self.ui.radioButton_rabi.clicked.connect(self.radioButton_rabi_clicked)
        self.ui.radioButton_t1.clicked.connect(self.radioButton_t1_clicked)

        # self.ui.pushButton_select_experiment_schemes.clicked.connect(self.pushButton_select_experiment_schemes_clicked)

        # Initialize all of the hardwares
        self.Init = []
        try:
            self.pb = PulseGenerator()
            self.Init.append(self.pb) # 0
        except:
            self.Init.append('')
            QMessageBox.warning(self,"Warning","Pulse generator is not initialzed! Please initialize mannually!",QMessageBox.Yes | QMessageBox.No)
        
        try:
            self.smiq = SMIQ('')
            self.Init.append(self.smiq) # 1
        except:
            self.Init.append('')
            QMessageBox.warning(self,"Warning","Microwave source is not initialzed! Please initialize mannually!",QMessageBox.Yes | QMessageBox.No)
        try:
            self.ccd = CCD()
            self.Init.append(self.ccd) # 2
        except:
            self.Init.append('')
            QMessageBox.warning(self,"Warning","Camera is not initialzed! Please initialize mannually!",QMessageBox.Yes | QMessageBox.No)


        # Preset the experiment parameters
        self.ui.lineEdit_loops.setText('5')

        # Set the button state
        self.ui.pushButton_stop.setEnabled(False)

       

        #Camera display
        def paint(event):
            QtWidgets.QLabel.paintEvent(self.ui.label_CCD,event)
            painter = QtGui.QPainter()
            painter.begin(self.ui.label_CCD)
            try:
                self._draw_on_image(painter)
            except AttributeError:
                self._draw_on_image = lambda painter: None
            painter.end()
        self.ui.label_CCD.paintEvent = paint

        Current_path = os.path.split(os.path.realpath(__file__))[0]
        png=QtGui.QPixmap(Current_path+'\\GUI\\CCD_Init.jpg')
        self.ui.label_CCD.setPixmap(png)
        #self.ui.label_CCD.setScaledContents (True)

    def pushButton_live_clicked(self):
        self.reset_mouse_events()
        self.ui.label_31.setText('Live mode.')
        self.ui.pushButton_live.setEnabled(False)
        self.ui.pushButton_snapshot.setEnabled(False)
        self.ui.pushButton_stop.setEnabled(True)
        self.exposure_time = int(self.ui.lineEdit_ExposureTime.text())

        self.camera_timed_thread = CameraThread(self.exposure_time, self.Init)
        self.camera_timed_thread.camera.connect(self.picture_back)
        self.camera_timed_thread.start()  

        try:
            del self.normFrame, self.frame  
        except:
            pass  

    def pushButton_stop_clicked(self):
        self.camera_timed_thread.running = False
        self.ui.pushButton_live.setEnabled(True)
        self.ui.pushButton_snapshot.setEnabled(True)
        self.ui.label_31.setText('Live mode ended.')
        self.setup_mouse_events()
        self.frame = []

    def pushButton_snapshot_clicked(self):
        self.ui.label_31.setText('Single mode.')
        self.exposure_time = float(self.ui.lineEdit_ExposureTime.text())
        # self.picture_back(self.sThread.single_shot())
        self.ccd.set_trigger_mode('Internal')
        self.ccd.set_exposure(self.exposure_time)
        self.frame = self.ccd.snapshot()
        self.picture_back(self.frame)
        self.max_value = numpy.amax(self.frame)
        self.median_value = numpy.median(self.frame)
        self.mean_value = round(numpy.average(self.frame),2)
        self.ui.lcd_max.display(self.max_value)
        self.setup_mouse_events()
        self.normFrame = (self.frame-numpy.min(self.frame))* int(65535/(numpy.max(self.frame)-numpy.min(self.frame)))

    def pushButton_clear_roi_clicked(self):
        self._draw_on_image = lambda painter: None
        self.update()
        self.ui.radioButton_ALL.setChecked(True)
        self.ui.lineEdit_left_up_x.setText('')
        self.ui.lineEdit_left_up_y.setText('')
        self.ui.lineEdit_right_down_x.setText('')
        self.ui.lineEdit_right_down_y.setText('')
        self.ROI = numpy.ones((512,512), dtype = numpy.uint16)

    def pushButton_select_image_save_path_clicked(self):
        self.ui.label_31.setText('Select the save path.')
        save_path = QFileDialog.getExistingDirectory(self, "选择文件夹", 'G:\\1-Experimental Data\\')
        self.ui.lineEdit_Camera_SavePath.setText(save_path)
        print(save_path)
        save_path_segment = save_path.split("/")
        self.image_save_path = '\\'.join(save_path_segment)

    def pushButton_save_image_clicked(self):
        file_name = self.ui.lineEdit_FileName.text()
        if self.image_save_path == []:
            QMessageBox.warning(self,"Warning","Please select the save path!",QMessageBox.Yes | QMessageBox.No)
        elif file_name == '':
            QMessageBox.warning(self,"Warning","Please input the file name!",QMessageBox.Yes | QMessageBox.No)
        elif self.frame == []:
            QMessageBox.warning(self,"Warning","No valid data to be saved!",QMessageBox.Yes | QMessageBox.No)
        else:
            Image.fromarray(self.normFrame).save(self.image_save_path+'\\Contrast_adjusted_'+file_name+'.tif')
            Image.fromarray(self.frame).save(self.image_save_path+'\\'+file_name+'.tif')
            self.ui.label_31.setText('Image is saved.')



    # ----------------------------------------------------------------------------------------------------
    def radioButton_cw_odmr_clicked(self):
        self.Info = []
        dialog = GUI_Wrapper_CW_ODMR(self.Info, parent=self)  
        if dialog.exec_() == 1:
            self.ui.listWidget_sequence.clear()
            self.ui.listWidget_sequence.addItem('MW Power (dBm): '+str(self.Info[0]))
            self.ui.listWidget_sequence.addItem('MW Frequency (Hz): '+str(self.Info[1]))
            self.ui.listWidget_sequence.addItem('Exposure time (ms): '+str(self.Info[2]))
            self.ui.listWidget_sequence.addItem('AOM Voltage (V): '+self.Info[3])  # self.Info[3] is a string.
            self.ui.listWidget_sequence.addItem('AOM Current (A): '+self.Info[4])  # self.Info[4] is a string.

    def radioButton_rabi_clicked(self):
        self.Info = []
        dialog = GUI_Wrapper_Rabi(self.Info, parent=self)  
        if dialog.exec_() == 1:
            self.ui.listWidget_sequence.clear()
            self.ui.listWidget_sequence.addItem('MW Power (dBm): '+str(self.Info[0]))
            self.ui.listWidget_sequence.addItem('MW Frequency (Hz): '+str(self.Info[1]))
            self.ui.listWidget_sequence.addItem('Laser Duration (ns): '+str(self.Info[2]))
            self.ui.listWidget_sequence.addItem('MW Start: '+str(self.Info[3]))
            self.ui.listWidget_sequence.addItem('MW_duration_sweeping: '+str(self.Info[4]))
            self.ui.listWidget_sequence.addItem('Repetitions: '+str(self.Info[5]))
            self.ui.listWidget_sequence.addItem('Gap between laser and MW: '+str(self.Info[6]))
            self.ui.listWidget_sequence.addItem('AOM power (dBm): '+self.Info[7])  # self.Info[7] is a string.

    def radioButton_t1_clicked(self):
        self.Info = []
        dialog = GUI_Wrapper_T1(self.Info, parent=self)  
        if dialog.exec_() == 1:
            self.ui.listWidget_sequence.clear()
            self.ui.listWidget_sequence.addItem('MW Power (dBm): '+str(self.Info[0])) # self.Info[0] is a int.
            self.ui.listWidget_sequence.addItem('MW Frequency (Hz): '+str(self.Info[1]))
            self.ui.listWidget_sequence.addItem('Laser Duration (ns): '+str(self.Info[2]))
            self.ui.listWidget_sequence.addItem('MW Duration (ns): '+str(self.Info[3]))
            self.ui.listWidget_sequence.addItem('gap_1: '+str(self.Info[4]))
            self.ui.listWidget_sequence.addItem('gap_2: '+str(self.Info[5]))
            self.ui.listWidget_sequence.addItem('delay_duration_sweeping: '+str(self.Info[6]))
            self.ui.listWidget_sequence.addItem('repetitions: '+str(self.Info[7]))
            self.ui.listWidget_sequence.addItem('AOM power (dBm): '+self.Info[8]) # self.Info[8] is a string.

    def pushButton_select_quantum_measurement_save_path_clicked(self):
        try:
            if self.last_path:
                self.folder_path = QFileDialog.getExistingDirectory(self, "选择文件夹", self.last_path)
            else:
                self.folder_path = QFileDialog.getExistingDirectory(self, "选择文件夹", 'G:\\1-Experimental Data\\')
            if self.folder_path:
                self.last_path = self.folder_path
                self.ui.lineEdit_SavePathPulsed.setText(self.folder_path)
            else:
                self.folder_path = self.last_path
                self.ui.lineEdit_SavePathPulsed.setText(self.folder_path)
            print(self.folder_path)
            save_path = self.folder_path.split("/")
            path = '\\'.join(save_path)
            Check_Existing = os.path.exists(path+'\\Processed')
            if Check_Existing:
                pass
            else:
                os.mkdir(path+'\\Processed')
            self.folder_path = path
        
            print(save_path)
            print(path)
        except:
            pass

    def pushButton_start_quantum_measurement_clicked(self):
        if self.ui.radioButton_cw_odmr.isChecked() == True:
            self.cw_odmr_measurement()
        elif self.ui.radioButton_rabi.isChecked() == True:
            self.rabi_measurement()
        elif self.ui.radioButton_t1.isChecked() == True:
            self.t1_measurement()
        else:
            QMessageBox.warning(self,"Warning","You must select one ration button from CW ODMR, Pulsed ODMR, Rabi!",QMessageBox.Yes | QMessageBox.No)
    
    def pushButton_stop_quantum_measurement_clicked(self):
        if self.ui.radioButton_cw_odmr.isChecked() == True:
            self.cw_odmr_thread.running = False
        elif self.ui.radioButton_rabi.isChecked() == True:
            self.rabi_thread.running = False
        elif self.ui.radioButton_t1.isChecked() == True:
            self.t1_thread.running = False
        else:
            QMessageBox.warning(self,"Warning","No thread is running!",QMessageBox.Yes | QMessageBox.No)

    def cw_odmr_measurement(self, ROI = []):
        self.ODMR_X = []
        self.ODMR_Y = []
        self.loop = 0
        self.yBot_2 = 0
        self.yTop_2 = 0
        self.ui.lcd_loops.display(self.loop+1)
        self.ui.mplPlotODMR.axes.set_xlabel('Frequency (GHz)')
        loops = int(self.ui.lineEdit_loops.text())
        Freq_start = self.Info[1][0]
        Freq_stop = self.Info[1][-1]
        self.display_mark = 'cw_odmr'
        self.ui.mplPlotODMR.axes.set_xlim(left=int(Freq_start)/1000000000,right=int(Freq_stop)/1000000000)

        # Voltage = self.Info[3]
        # Current = self.Info[4]
        # if float(Voltage) <= self.aom_max_voltage:
        #     self.keithley_powersupply.Set(Voltage, Current)
        #     self.keithley_powersupply.ON()
        #     self.pushButton_Keithley_check_clicked()
        #     self.ui.label_keithley_state.setText('CW ODMR ON')
        # else:
        #     QMessageBox.warning(self,"Warning","The voltage must not be bigger than 0.9 V!",QMessageBox.Yes | QMessageBox.No)

        self.cw_odmr_thread = CW_Thread(self.Info, loops, self.folder_path, self.ROI, self.Init)
        self.cw_odmr_thread.cw.connect(self.animate_ODMR)
        self.cw_odmr_thread.start()

    def rabi_measurement(self):
        self.ODMR_X = []
        self.ODMR_Y = []
        self.Rabi_X_WithOutMW = []
        self.Rabi_Y_WithOutMW = []
        self.loop = -1
        self.yBot_0 = 65536
        self.yTop_0 = 0
        self.yBot_1 = 65536
        self.yTop_1 = 0
        self.min_time = self.Info[4][0]
        self.max_time = self.Info[4][-1]
        self.ui.mplPlotODMR.axes.set_xlim(left=self.min_time,right=self.max_time)
        self.ui.mplPlotODMR.axes.set_xlabel('Time (ns)')
        self.display_mark = 'rabi'
        print('Rabi start')
        loops = int(self.ui.lineEdit_loops.text())

        # Voltage = self.Info[7]
        # Current = self.Info[8]
        # if float(Voltage) <= self.aom_max_voltage:
        #     self.keithley_powersupply.Set(Voltage, Current)
        #     self.keithley_powersupply.ON()
        #     self.pushButton_Keithley_check_clicked()
        #     self.ui.label_keithley_state.setText('Rabi ON')
        # else:
        #     QMessageBox.warning(self,"Warning","The voltage must not be bigger than 1V!",QMessageBox.Yes | QMessageBox.No)

        self.rabi_thread = rabi_thread(self.Info, loops, self.folder_path, self.ROI, self.Init)
        self.rabi_thread.Rabi.connect(self.animate_Rabi)
        self.rabi_thread.start()

    def t1_measurement(self):
        self.ODMR_X = []
        self.ODMR_Y = []
        self.Rabi_X_WithOutMW = []
        self.Rabi_Y_WithOutMW = []
        self.loop = -1
        self.yBot_0 = 65536
        self.yTop_0 = 0
        self.yBot_1 = 65536
        self.yTop_1 = 0
        self.min_time = self.Info[6][10]
        self.max_time = self.Info[6][-6]
        self.ui.mplPlotODMR.axes.set_xlim(left=self.min_time,right=self.max_time)
        self.ui.mplPlotODMR.axes.set_xlabel('Time (ns)')
        self.display_mark = 't1'
        print('T1 start')
        loops = int(self.ui.lineEdit_loops.text())
        # Voltage = self.Info[8]
        # Current = self.Info[9]
        # if float(Voltage) <= self.aom_max_voltage:
        #     self.keithley_powersupply.Set(Voltage, Current)
        #     self.keithley_powersupply.ON()
        #     self.pushButton_Keithley_check_clicked()
        #     self.ui.label_keithley_state.setText('T1 ON')
        # else:
        #     QMessageBox.warning(self,"Warning","The voltage must not be bigger than 1V!",QMessageBox.Yes | QMessageBox.No)

        self.t1_thread = T1_thread(self.Info, loops, self.folder_path, self.ROI, self.Init)
        self.t1_thread.T1.connect(self.animate_Rabi)
        self.t1_thread.start()


    # -----------------------------------------------------------------------------------------------------
    def pushButton_turn_off_camera_clicked(self):
        print('camera close')
        self.ccd.close()

    def pushButton_andor_cooler_on_clicked(self):
        print('cooler on')
        self.ccd.set_temperature(-70)
        self.ccd.cooler_on()

    def pushButton_andor_cooler_off_clicked(self):
        print('cooler off')
        self.ccd.cooler_off()

    def pushButton_andor_temperature_check_clicked(self):
        self.camera_temperature_monitoring_thread = CameraTemperatureMonitoringThread(self.Init)
        self.camera_temperature_monitoring_thread.temperature.connect(self.camera_temperature_showing)
        self.camera_temperature_monitoring_thread.start()

    def camera_temperature_showing(self, temperature):
        self.ui.label_andor_temperature.setText(str(temperature))


    # -----------------------------------------------------------------------------------------------------
    def picture_back(self, frame):
        maxi = numpy.max(frame)
        if maxi == 65535:
            QMessageBox.warning(self,"Warning","The camera is over-exposured!",QMessageBox.Yes | QMessageBox.No)
            self.ui.pushButton_Submit.setEnabled(True)
            self.ui.pushButton_Single.setEnabled(True)
            self.ui.label_31.setText('Live mode ended.')
            self.pushButton_laser_off_clicked()
        self.ui.lcd_max.display(maxi)

        normImage = (frame-numpy.min(frame)) * (256/(maxi-numpy.min(frame)))
        image8Bit = Image.fromarray(numpy.array(normImage, dtype=numpy.uint8), mode='L')
        pix = QtGui.QPixmap.fromImage(ImageQt.ImageQt(image8Bit))
        self.ui.label_CCD.setPixmap(pix)
        try:
            self.camera_timed_thread.pause = False
        except:
            pass

    def ROI_filter(self, frame, ROI):
        ROI_frame = frame * ROI
        ROI_frame_NoZero = ROI_frame.ravel()[numpy.flatnonzero(ROI_frame)]
        return ROI_frame_NoZero

    # Format of data: [freq, frame, loop]; freq is the data in x axis.  Single line
    def animate_ODMR(self, data): 
        freq = data[0]
        frame = data[1]
        loop = data[2]
        frame_roi = self.ROI_filter(frame, self.ROI)
        max_frame = numpy.max(frame)
        # median_frame = numpy.median(frame_roi)
        median_frame = numpy.mean(frame_roi)

        if max_frame == 65535:  # display the 
            self.Over_exposure = self.Over_exposure +1
            self.ui.lcd_over_exposure.display(self.Over_exposure)

        if loop != self.loop:
            self.ODMR_X = []
            self.ODMR_Y = []
            self.loop = loop
            self.ui.lcd_loops.display(self.loop+1)

        #  This segment is for drawing the curve
        self.ODMR_X.append(freq/1000000000)
        self.ODMR_Y.append(median_frame)
        a=numpy.array(self.ODMR_Y)
        yBot=a.min()*0.99
        yTop=a.max()*1.01
        self.ODMR_Plot.set_xdata(self.ODMR_X)
        self.ODMR_Plot.set_ydata(self.ODMR_Y)
        self.ui.mplPlotODMR.axes.set_ylim(bottom=yBot,top=yTop)
        self.ui.mplPlotODMR.draw()

        if freq == self.Info[1][-1]: # self.Info[1][-1] is the last frequence of ODMR freq sequence.
            try:
                x_fit, y_fit = self.Lorentzian(self.ODMR_X, self.ODMR_Y)
                self.Rabi_Plot_WithOutMW.set_xdata(x_fit)
                self.Rabi_Plot_WithOutMW.set_ydata(y_fit)
            except:
                pass

        self.ui.lcd_max.display(max_frame)
        self.picture_back(frame)
        if self.display_mark == 'cw_odmr':
            self.cw_odmr_thread.pause = False
        elif self.display_mark == 'pulsed_odmr':
            self.pulsed_odmr_thread.pause = False
        else:
            pass

    # Format of Data: [t, frame, MWon/off, loop]; t is the data in x axis.   Two lines, 0 means MWoff, 1 means MWon
    def animate_Rabi(self, Data): 
        frame = Data[1]
        frame_roi = self.ROI_filter(frame, self.ROI)
        median_frame = numpy.median(frame_roi)
        max_frame = numpy.max(frame)

        if Data[3] != self.loop:
            self.ODMR_X = []
            self.ODMR_Y = []
            self.Rabi_X_WithOutMW = []
            self.Rabi_Y_WithOutMW = []
            self.loop = Data[3]
            self.ui.lcd_loops.display(self.loop+1)

        if Data[3] == self.loop:    
            if Data[2]==0:
                self.ODMR_X.append(Data[0])
                self.ODMR_Y.append(median_frame)
                a=numpy.array(self.ODMR_Y)
                self.yBot_0=a.min()*0.99
                self.yTop_0=a.max()*1.01
                yBot = min(self.yBot_0, self.yBot_1)
                yTop = max(self.yTop_0, self.yTop_1)
                self.ODMR_Plot.set_xdata(self.ODMR_X)
                self.ODMR_Plot.set_ydata(self.ODMR_Y)
                self.ui.mplPlotODMR.axes.set_ylim(bottom=yBot, top=yTop)
                self.ui.mplPlotODMR.draw() 
            elif Data[2]==1:
                self.Rabi_X_WithOutMW.append(Data[0])
                self.Rabi_Y_WithOutMW.append(median_frame)
                a=numpy.array(self.Rabi_Y_WithOutMW)
                self.yBot_1=a.min()*0.99
                self.yTop_1=a.max()*1.01
                yBot = min(self.yBot_0, self.yBot_1)
                yTop = max(self.yTop_0, self.yTop_1)
                self.Rabi_Plot_WithOutMW.set_xdata(self.Rabi_X_WithOutMW)
                self.Rabi_Plot_WithOutMW.set_ydata(self.Rabi_Y_WithOutMW)
                self.ui.mplPlotODMR.axes.set_ylim(bottom=yBot, top=yTop)
                self.ui.mplPlotODMR.draw() 
       
        self.ui.lcd_max.display(max_frame)

        if max_frame == 65535:
            self.Over_exposure = self.Over_exposure +1
            self.ui.lcd_over_exposure.display(self.Over_exposure)
        
        self.picture_back(frame)

        if self.display_mark == 'rabi':
            self.rabi_thread.pause = False
        elif self.display_mark == 't1':
            self.t1_thread.pause = False
        elif self.display_mark == 'pulsed_odmr_mw_none':
            self.pulsed_odmr_mw_none_thread.pause = False
        elif self.display_mark == 'sim_pulsed_odmr_mw_none':
            self.sim_pulsed_odmr_mw_none_thread.pause = False 
        else:
            pass

    def setup_mouse_events(self):
        # Press down
        print('1111111111')
        def mouse_press(event):
            x = event.x()
            y = event.y()
            self.mousePressXY = (x,y)
            self.mousePressButton = event.button()
            if self.mousePressButton == 1:
                # self.ui.label_26.setText('Center')
                # self.ui.label_27.setText('Radium')
                # self.ui.label_28.setText('X')
                # self.ui.label_29.setText('Y')
                # self.ui.label_30.setText('Circle')
                pass
            elif self.mousePressButton == 2:
                # self.ui.label_26.setText('Left Up')
                # self.ui.label_27.setText('Right Down')
                # self.ui.label_28.setText('X')
                # self.ui.label_29.setText('Y')
                # self.ui.label_30.setText('Rectangle')
                pass
            else:
                pass
            def draw_point(painter):
                painter.setPen(QtGui.QPen(QtCore.Qt.red,1))
                painter.drawPoint(x,y)
            self._draw_on_image = draw_point
            self.update()
        self.ui.label_CCD.mousePressEvent = mouse_press
        # Drag (left button: circle. right button: rectangle. center button: ellipse)
        def mouse_drag(event):
            x = event.x()
            y = event.y()
            x0,y0 = self.mousePressXY
            self.mouseReleaseXY = (x,y)
            if self.mousePressButton == 1: # Left Clicked
                xc = (x + x0) / 2
                yc = (y + y0) / 2
                r = numpy.sqrt((x-x0)**2 + (y-y0)**2) / 2
                def draw_circle(painter):
                    painter.setPen(QtGui.QPen(QtCore.Qt.red,1))
                    painter.drawEllipse(QtCore.QPointF(xc,yc),r,r)
                self._draw_on_image = draw_circle
                
                # self.ui.radioButton_Customized.setChecked(True)
                
                # self.ui.lineEdit_left_up_x.setText(str(int(xc)))
                # self.ui.lineEdit_left_up_y.setText(str(int(yc)))
                # self.ui.lineEdit_right_down_x.setText(str(int(r)))
                # self.ui.lineEdit_right_down_y.setText('')
            elif self.mousePressButton == 2:
                def draw_rect(painter):
                    painter.setPen(QtGui.QPen(QtCore.Qt.red,1))
                    painter.drawRect(QtCore.QRect(QtCore.QPoint(x0,y0), QtCore.QPoint(x,y)))
                # self.ui.radioButton_Customized.setChecked(True)
                # self.ui.lineEdit_left_up_x.setText(str(x0))
                # self.ui.lineEdit_left_up_y.setText(str(y0))
                # self.ui.lineEdit_right_down_x.setText(str(x))
                # self.ui.lineEdit_right_down_y.setText(str(y))
                self._draw_on_image = draw_rect
            else:
                def draw_ellipse(painter):
                    painter.setPen(QtGui.QPen(QtCore.Qt.red,1))
                    painter.drawEllipse(QtCore.QRect(QtCore.QPoint(x0,y0), QtCore.QPoint(x,y)))
                self._draw_on_image = draw_ellipse
            self.update()
        self.ui.label_CCD.mouseMoveEvent = mouse_drag
        # Release (setup region of interest)
        def mouse_release(event):
            try: 
                x1, y1 = self.mousePressXY
                x2, y2 = self.mouseReleaseXY
                self.roi = numpy.zeros((512, 512),dtype=numpy.uint16)
                if self.mousePressButton == 1:
                    xc = (x1 + x2) / 2
                    yc = (y1 + y2) / 2
                    for x in range(self.roi.shape[1]):
                        for y in range(self.roi.shape[0]):
                            if (x-xc)**2 + (y-yc)**2 < ((x1-x2)**2 + (y1-y2)**2) / 4:
                                self.roi[y,x] = 1
                elif self.mousePressButton == 2:
                    self.roi[min(y1, y2):max(y1, y2), min(x1, x2):max(x1, x2)] = 1
                    print('dfs')
                    self.zoom_in_x_left = min(x1, x2)
                    self.zoom_in_x_right = max(x1, x2)
                    self.zoom_in_y_up = min(y1, y2)
                    self.zoom_in_y_down = max(y1, y2)
                    print(self.zoom_in_x_left)
                    print(self.zoom_in_x_right)
                    print(self.zoom_in_y_up)
                    print(self.zoom_in_y_down)
                else:
                    xc = (x1 + x2) / 2
                    yc = (y1 + y2) / 2
                    a = (x1 - x2) / 2
                    b = (y1 - y2) / 2
                    for x in range(self.roi.shape[1]):
                        for y in range(self.roi.shape[0]):
                            if ((x-xc)/a)**2 + ((y-yc)/b)**2 < 1:
                                self.roi[y,x] = 1
                if numpy.max(self.roi) == 0:
                    self.roi[x1, y1] = 1
                self.ROI = self.roi
                print('ROI DOWN')
            except:
                pass
        self.ui.label_CCD.mouseReleaseEvent = mouse_release

    def reset_mouse_events(self):
        #self._draw_on_image = lambda painter : None
        #self.ui.label_CCD.update()
        self.ui.label_CCD.mousePressEvent = lambda event : None
        self.ui.label_CCD.mouseMoveEvent = lambda event : None
        self.ui.label_CCD.mouseReleaseEvent = lambda event : None
        try:
            del self.mousePressXY, self.mouseReleaseXY, self.mousePressButton
        except AttributeError:
            pass

    
if __name__ == '__main__':
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_DisableHighDpiScaling,True)
    app=QtWidgets.QApplication(sys.argv)
    myWindow=mainGUI()
    myWindow.show()
    sys.exit(app.exec_())
