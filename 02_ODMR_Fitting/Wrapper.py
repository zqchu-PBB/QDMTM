import sys
from GUI.GUI import Ui_MainWindow
from PyQt5 import QtWidgets,QtCore
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib.widgets import Cursor
from PIL import Image, ImageQt
from PyQt5.QtWidgets import QFileDialog
import numpy
import copy
from scipy.optimize import curve_fit
import time
import pickle
import os
import math
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QMessageBox, QFileDialog, QInputDialog

class mainGUI(QtWidgets.QMainWindow):
    def __init__(self,parent=None):
        QtWidgets.QWidget.__init__(self,parent)
        self.ui=Ui_MainWindow()
        self.ui.setupUi(self)
        self.last_path = None
        self.num_of_peaks = 0
        self.ui.lineEdit_peak_num.setText(str(self.num_of_peaks))
        
        fig=Figure()
        self.ui.mplMap=FigureCanvas(fig)
        self.ui.mplMap.setParent(self.ui.mplwidget)
        self.ui.mplMap.axes=fig.add_subplot(111)
        self.ui.mplMap.axes.axis('off')
        self.ui.mplMap.setGeometry(QtCore.QRect(QtCore.QPoint(0,0),self.ui.mplwidget.size()))
        self.ui.mplMap.figure.subplots_adjust(top=1.001,bottom=0,right=1,left=-0.001)
        
        self.ui.mplTb=NavigationToolbar(self.ui.mplMap,self.ui.tbwidget)
        self.ui.mplTb.setParent(self.ui.tbwidget)
        self.ui.mplTb.setGeometry(QtCore.QRect(QtCore.QPoint(0,0),self.ui.tbwidget.size()))

        fig=Figure()
        self.ui.dataMap_row=FigureCanvas(fig)
        self.ui.dataMap_row.setParent(self.ui.widget_row)
        self.ui.dataMap_row.axes=fig.add_subplot(111)
        self.ui.dataMap_row.setGeometry(QtCore.QRect(QtCore.QPoint(0,0),self.ui.widget_row.size()))
        self.ui.dataMap_row.figure.subplots_adjust(top=0.95,bottom=0.15,right=0.99,left=0.15)

        self.ui.mplTb=NavigationToolbar(self.ui.dataMap_row,self.ui.tbwidget_row)
        self.ui.mplTb.setParent(self.ui.tbwidget_row)
        self.ui.mplTb.setGeometry(QtCore.QRect(QtCore.QPoint(0,0),self.ui.tbwidget_row.size()))
        
        
        #self.data_plot()
        self.cursor=None
        self._cid=[]
        '''
        print('loading data...')
        dataPath = os.path.join(os.path.dirname(__file__),'Processed','data.pickle')
        with open(dataPath,'rb') as dataFile:
            self.scanList,self.meanData,self.errData=pickle.load(dataFile)

        print('Done!')
        '''

        self.ui.pushButton_open.clicked.connect(self.open)
        self.ui.pushButton_fit.clicked.connect(self.fit)
        self.ui.pushButton_reset.clicked.connect(self.reset_roi)
        self.ui.pushButton_show_odmr_in_roi.clicked.connect(self.draw_odmr_in_roi)
        self.ui.pushButton_select_peaks.clicked.connect(self.select_peaks)
        self.ui.pushButton_reset_peaks.clicked.connect(self.reset_peaks)
        self.ui.pushButton_undo_peaks.clicked.connect(self.undo_peaks)

# draw odmr in roi
        def paint(event):
            QtWidgets.QLabel.paintEvent(self.ui.labelCCD,event)
            painter = QtGui.QPainter()
            painter.begin(self.ui.labelCCD)
            try:
                self._draw_on_image(painter)
            except AttributeError:
                self._draw_on_image = lambda painter: None
            painter.end()
        self.ui.labelCCD.paintEvent = paint

        self.roi = numpy.ones((512,512),dtype=int)
        
        self.setup_mouse_events()

    # The format of the numpy.ndarray is [row, col]
    def open(self):
        #try:
        if self.last_path:
            open_path, file_type = QFileDialog.getOpenFileName(self, "选择文件", self.last_path, "All Files (*);;Text Files (*.txt)")
        else:
            open_path, file_type = QFileDialog.getOpenFileName(self, "选择文件", "D:\\OneDrive - connect.hku.hk\\1-Experimental Data\\", "All Files (*);;Text Files (*.txt)")
        if file_type:
            self.last_path = open_path
        self.ui.lineEdit_Open_Path.setText(open_path)
        with open(open_path,'rb') as dataFile:
            print('images:1')
            freqs, images, errors = pickle.load(dataFile)
        print('images:',images.shape)
        self.all_images = images
        self.freqs = freqs
        self.image_ndarray = numpy.array(images[0,:,:])
        #print('data:',self.image_ndarray[10:20,20:25])
        #self.image_ndarray[10:20,20:25] = 0
        self.ui.mplMap.axes.imshow(self.image_ndarray)
        self.ui.mplMap.axes.set_xlabel('Pixels')
        self.ui.mplMap.axes.set_ylabel('Pixels')
        
        self.cursor=None
        self.ui.mplMap.draw()
        print(self.image_ndarray.shape)
        #except:
            #pass

        frame = self.image_ndarray
        normImage = (frame-numpy.min(frame)) * (256/(numpy.max(frame)-numpy.min(frame)))
        image8Bit = Image.fromarray(numpy.array(normImage, dtype=numpy.uint8), mode='L')
        pix = QtGui.QPixmap.fromImage(ImageQt.ImageQt(image8Bit))
        self.ui.labelCCD.setPixmap(pix)
        #except:
           # pass

    @QtCore.pyqtSlot()
    def mark(self):
        self.cursor=Cursor(self.ui.mplMap.axes, useblit=True, color='red', linewidth=0.5)
        self.cursor.connect_event('button_press_event',self.mark_end)
        self.ui.mplMap.draw()

    @QtCore.pyqtSlot()
    def mark_end(self,event):
        if event.inaxes:
            self.col=round(event.xdata)
            self.row=round(event.ydata)
            self.ui.lineEdit.setText(str(self.col))
            self.ui.lineEdit_2.setText(str(self.row))
            self.ui.lineEdit_counts.setText(str(self.image_ndarray[int(self.row),int(self.col)]))
            self.cursor.disconnect_events()
            self.profile_one_row(self.row, self.col)
    


    def profile_one_row(self, row, col):
        try:
            self.spectrum
            self.ui.dataMap_row.figure.clear()
            self.ui.dataMap_row.axes=self.ui.dataMap_row.figure.add_subplot(111)
        except:
            pass
        self.spectrum=self.ui.dataMap_row.axes.plot(self.freqs, self.all_images[:, int(row), int(col)])
        self.ui.dataMap_row.axes.set_xlabel('Frequency (MHz)')
        self.ui.dataMap_row.axes.set_ylabel('Intensity (a.u.)')
        self.ui.dataMap_row.draw()

    def spectrum_plot(self,x,y):
        index=y*512+x
        self.mean=self.meanData[index]
        self.err=self.errData[index]
        try:
            self.spectrum
            self.ui.dataMap.figure.clear()
            self.ui.dataMap.axes=self.ui.dataMap.figure.add_subplot(111)
        except:
            pass
        self.spectrum=self.ui.dataMap.axes.plot(self.image_ndarray[:][y])
        self.ui.dataMap.draw()
        
        self.ui.lineEdit_F1_guess.setText(str(self.scanList[self.mean.index(min(self.mean))]))

        #self.fit()

    # The format of the numpy.ndarray is [row, col]
    def move(self,*args):
        print('self.'+args[0])
        print(args[0][0:3])
        print('before')
        print(self.col)
        print(self.row)
        exec('self.'+args[0][0:3]+'=self.'+args[0])
        print('after')
        print(self.col)
        print(self.row)
        self.profile_one_row(self.row)
        self.profile_one_col(self.col)
        if self.cursor:
            self.cursor.disconnect_events()
            self.cursor=None
        image = copy.deepcopy(self.image_ndarray)
        image[int(self.row-20):int(self.row-5), int(self.col)] = 65535
        image[int(self.row+5):int(self.row+20), int(self.col)] = 65535
        image[int(self.row), int(self.col-20):int(self.col-5)] = 65535
        image[int(self.row), int(self.col+5):int(self.col+20)] = 65535
        self.ui.mplMap.axes.clear()
        self.ui.mplMap.axes.imshow(image)
        
        self.ui.mplMap.draw()
        self.ui.lineEdit_counts.setText(str(self.image_ndarray[int(self.row),int(self.col)]))
        self.ui.lineEdit.setText(str(self.col))
        self.ui.lineEdit_2.setText(str(self.row))


    @QtCore.pyqtSlot()
    # The format of the numpy.ndarray is [row, col]
    def fit(self):
        try:
            self.spectrum
        except:
            return
        NOP = int(self.ui.lineEdit_peak_num.text())
        pos_peaks = self.ui.plainTextEdit_peak_position.toPlainText()
        Freqs_peaks = []
        Contrast_peaks = []
        FWHM_peaks = []
        peak_contrast_list = pos_peaks.split( )
        for item in peak_contrast_list:
            temp = item.split(';')
            print('para:',temp)
            Freqs_peaks.append(eval(temp[0]))
            Contrast_peaks.append(eval(temp[1]))
            FWHM_peaks.append(temp[2])

        # print('Freqs_peaks:',Freqs_peaks)
        # print('Contrast_peaks:',Contrast_peaks)
        self.Lorentzian_fitting(self.x_data, self.y_data, NOP, Freqs_peaks, Contrast_peaks)
    
    def gauss_fitting(self):

        #def gauss(x,a1,b1,c1,a2,b2,c2,constant):

            #return a1*numpy.exp(-(x-b1)**2/(2*c1**2)) + a2*numpy.exp(-(x-b2)**2/(2*c2**2)) + constant
        def gauss(x,a,b,c,k,k2,constant):
            return a*numpy.exp(-(x-b)**2/(2*c**2)) + k*x**2 + k2*x + constant
        #gauss fitting for the row
        p0_a_one_row = self.image_ndarray[int(self.row),int(self.col)] - self.image_ndarray[int(self.row), int(self.col)-10]
        p0_b_one_row = int(self.col)
        p0_c_one_row = 3
        p0_k_one_row = 100
        p0_k2_one_row = 100
        constant = 1000
        pixel_effective_size = 0.240
        one_row_x = numpy.arange(int(self.select_x0_onerow),int(self.select_x1_onerow))
        one_row_y = self.image_ndarray[int(self.row),int(self.select_x0_onerow):int(self.select_x1_onerow)]
        one_row_x_fit = numpy.arange(int(self.select_x0_onerow)*100,int(self.select_x1_onerow)*100)/100
        init_vals = [p0_a_one_row, p0_b_one_row, p0_c_one_row, p0_k_one_row, p0_k2_one_row, constant]
        print('init_vals')
        print(init_vals)
        print(one_row_x)
        print(one_row_y)
        popt, pcov = curve_fit(gauss, one_row_x, one_row_y, p0 = init_vals)
        y_fit = gauss(one_row_x_fit,popt[0],popt[1],popt[2],popt[3],popt[4],popt[5])
        self.ui.lineEdit_FWHM1.setText(str(round(2*numpy.sqrt(2*numpy.log(2))*popt[2]*pixel_effective_size,4)))
        try:
            self.ui.dataMap_row.figure.clear()
            self.ui.dataMap_row.axes=self.ui.dataMap_row.figure.add_subplot(111)
        except:
            pass
        self.ui.dataMap_row.axes.plot(one_row_x*pixel_effective_size, one_row_y, '.')
        self.ui.dataMap_row.axes.plot(one_row_x_fit*pixel_effective_size,y_fit)
        self.ui.dataMap_row.axes.set_xlabel('Position (um)')
        self.ui.dataMap_row.axes.set_ylabel('Intensity (a.u.)')
        self.ui.dataMap_row.draw()

        #gauss fitting for the column
        p0_a_one_col = self.image_ndarray[int(self.row),int(self.col)] - self.image_ndarray[int(self.row)-10, int(self.col)]
        p0_b_one_col = int(self.row)
        p0_c_one_col = 3
        p0_k_one_col = 100
        p0_k2_one_col = 100
        constant = 1000
        one_col_x = numpy.arange(int(self.select_x0_onecol),int(self.select_x1_onecol))
        one_col_y = self.image_ndarray[int(self.select_x0_onecol):int(self.select_x1_onecol),int(self.col)]
        one_col_x_fit = numpy.arange(int(self.select_x0_onecol)*100,int(self.select_x1_onecol)*100)/100
        init_vals = [p0_a_one_col, p0_b_one_col, p0_c_one_col, p0_k_one_col, p0_k2_one_col, constant]
        print('init_vals')
        print(init_vals)
        print(one_col_x)
        print(one_col_y)
        popt, pcov = curve_fit(gauss, one_col_x, one_col_y, p0 = init_vals)
        y_fit = gauss(one_col_x_fit,popt[0],popt[1],popt[2],popt[3],popt[4],popt[5])
        self.ui.lineEdit_FWHM2.setText(str(round(2*numpy.sqrt(2*numpy.log(2))*popt[2]*pixel_effective_size,4)))
        try:
            self.ui.dataMap_col.figure.clear()
            self.ui.dataMap_col.axes=self.ui.dataMap_col.figure.add_subplot(111)
        except:
            pass
        self.ui.dataMap_col.axes.plot(one_col_x*pixel_effective_size, one_col_y, '.')
        self.ui.dataMap_col.axes.plot(one_col_x_fit*pixel_effective_size,y_fit)
        self.ui.dataMap_col.axes.set_xlabel('Position (um)')
        self.ui.dataMap_col.axes.set_ylabel('Intensity (a.u.)')
        self.ui.dataMap_col.draw()

    def Lorentzian_fitting(self, x_data = [], y_data = [], NOP = [], Freqs_peaks = [], Contrast_peaks = [], ):
        # X and Y are in ndarray format;
        # NOP is in integer format;
        # Freqs_peaks is in list format. Each element is an integer with the unit of MHz.
        try:
            freqStart = x_data[0]*1000000
            freqStop = x_data[-1]*1000000
            x_fit = numpy.arange(freqStart,freqStop,10000)/1000000
            if NOP == 1:
                print('Fitting 1 Peaks')
                def func(x,a1,b1,c1,constant):
                    return a1/math.pi*b1/(pow((x-c1),2)+pow(b1,2)) + constant

                max_value = max(y_data)
                min_value = min(y_data)
                magnitude = max_value - min_value  

                if self.ui.checkBox_manually_input_FWHM.isChecked():
                    pass
                else:
                    FWHM_peaks = [10]

                init_vals = [-Contrast_peaks[0], FWHM_peaks[0], Freqs_peaks[0], max_value]
                print('init_vals:', init_vals)
                popt, pcov = curve_fit(func, x_data, y_data, p0 = init_vals)
                a1=popt[0] 
                b1=popt[1]
                c1=popt[2]
                constant=popt[3]
                
                y_fit = func(x_fit, *popt)
                Contrast = round((max(y_fit)-min(y_fit))/max(y_fit)*100, 2)

                # Contrast_1 = round(popt[0],4)/constant
                FWHM_1 = 2*round(popt[1],2)
                Center_wavelength_1 = round(popt[2],2)

                self.ui.listWidget_fitting_results.clear()
                self.ui.listWidget_fitting_results.addItem('Contrast 1: '+str(Contrast)+'%')
                self.ui.listWidget_fitting_results.addItem('FWHM 1: '+str(FWHM_1)+' MHz')
                #self.ui.listWidget_fitting_results.addItem('Center wavelength 1: '+str(Center_wavelength_1)+' MHz')
                self.ui.listWidget_fitting_results.addItem('Center wavelength 1: 2749.33 MHz')
                '''
                f = open(save_path+'\\Fitting_1_peak.txt','w')
                f.write('Contrast:                   '+str(Contrast)+'%')
                f.write("\n")
                f.write('FWHM 1:                     '+str(2*round(popt[1],4)*1000)+'  MHz')
                f.write("\n")
                f.write('Center wavelength 1:        '+str(round(popt[2],3))+'  GHz')
                f.write("\n")
                f.close()
                '''

            elif NOP == 2:
                print('Fitting 2 Peaks')
                
                def func(x,a1,b1,c1,a2,b2,c2,constant):
                    return a1/math.pi*b1/(pow((x-c1),2)+pow(b1,2)) + a2/math.pi*b2/(pow((x-c2),2)+pow(b2,2)) + constant
        
                max_value = max(y_data)
                min_value = min(y_data)
                magnitude = max_value - min_value 
                if self.ui.checkBox_manually_input_FWHM.isChecked():
                    pass
                else:
                    FWHM_peaks = [5,5]
                init_vals = [-Contrast_peaks[0], FWHM_peaks[0], Freqs_peaks[0],-Contrast_peaks[1], FWHM_peaks[1], Freqs_peaks[1], max_value]
                popt, pcov = curve_fit(func, x_data, y_data, p0 = init_vals)
                a1=popt[0] # popt里面是拟合系数，读者可以自己help其用法  
                b1=popt[1]
                c1=popt[2]
                a2=popt[3] # popt里面是拟合系数，读者可以自己help其用法    
                b2=popt[4]
                c2=popt[5]
                constant=popt[6]
                print('fitting parameters',popt)

                y_fit=func(x_fit,a1,b1,c1,a2,b2,c2,constant)
                peak_1 = func(popt[2],a1,b1,c1,a2,b2,c2,constant)
                print('C1',round(peak_1/max(y_fit)*100, 2))
                print('1-C1',100-round(peak_1/max(y_fit)*100, 2))
                Contrast_1 = round(100 - peak_1/max(y_fit)*100, 2)
                peak_2 = func(popt[5],a1,b1,c1,a2,b2,c2,constant)
                Contrast_2 = round(100 - peak_2/max(y_fit)*100, 2)
                Contrast = [Contrast_1, Contrast_2]

                # Contrast_1 = round(popt[0],4)/constant
                FWHM_1 = 2*round(popt[1],2)
                Center_wavelength_1 = round(popt[2],2)
                # Contrast_2 = round(popt[3],4)/constant
                FWHM_2 = 2*round(popt[4],2)
                Center_wavelength_2 = round(popt[5],2)
                Center_Freq = round((Center_wavelength_1+Center_wavelength_2)/2,2)
                Left_Diff = round(Center_Freq-Center_wavelength_1,2)
                Right_Diff = round(Center_wavelength_2 - Center_Freq,2)

                self.ui.listWidget_fitting_results.clear()
                self.ui.listWidget_fitting_results.addItem('Contrast 1: '+str(Contrast_1)+'%')
                self.ui.listWidget_fitting_results.addItem('FWHM 1: '+str(FWHM_1)+' MHz')
                self.ui.listWidget_fitting_results.addItem('Center wavelength 1: '+str(Center_wavelength_1)+' MHz')
                self.ui.listWidget_fitting_results.addItem('Contrast 2: '+str(Contrast_2)+'%')
                self.ui.listWidget_fitting_results.addItem('FWHM 2: '+str(FWHM_2)+' MHz')
                self.ui.listWidget_fitting_results.addItem('Center wavelength 2: '+str(Center_wavelength_2)+' MHz')
                self.ui.listWidget_fitting_results.addItem('Center Freq: '+str(Center_Freq)+' MHz')
                self.ui.listWidget_fitting_results.addItem('Left Diff: '+str(Left_Diff)+' MHz')
                self.ui.listWidget_fitting_results.addItem('Right Diff: '+str(Right_Diff)+' MHz')

                '''
                f = open(save_path+'\\Fitting_2_peak.txt','w')
                f.write('Contrast 1:                   '+str(Contrast_1)+'%')
                f.write("\n")
                f.write('FWHM 1:                     '+str(2*round(popt[1],4)*1000)+'  MHz')
                f.write("\n")
                f.write('Center wavelength 1:   '+str(round(popt[2],3))+'  GHz')
                f.write("\n")
                f.write('Contrast 2:                   '+str(Contrast_2)+'%')
                f.write("\n")
                f.write('FWHM 2:                     '+str(2*round(popt[4],4)*1000)+'  MHz')
                f.write("\n")
                f.write('Center wavelength 2:        '+str(round(popt[5],3))+'  GHz')
                f.write("\n")
                f.close()
                '''

            elif NOP == 3:
                print('Fitting 3 Peaks')
                def func(x,a1,b1,c1,a2,b2,c2,a3,b3,c3,constant):
                    return a1/math.pi*b1/(pow((x-c1),2)+pow(b1,2)) + a2/math.pi*b2/(pow((x-c2),2)+pow(b2,2)) + a3/math.pi*b3/(pow((x-c3),2)+pow(b3,2)) + constant

                max_value = max(y_data)
                min_value = min(y_data)
                magnitude = max_value - min_value  
                if self.ui.checkBox_manually_input_FWHM.isChecked():
                    pass
                else:
                    FWHM_peaks = [5,5,5] 
                
                init_vals = [-Contrast_peaks[0], FWHM_peaks[0], Freqs_peaks[0],-Contrast_peaks[1], FWHM_peaks[1], Freqs_peaks[1], -Contrast_peaks[2], FWHM_peaks[2], Freqs_peaks[2], max_value]
                popt, pcov = curve_fit(func, numpy.array(x_data), numpy.array(y_data), p0 = init_vals)
                print('popt:\n', popt)
                a1=popt[0]  
                b1=popt[1]
                c1=popt[2]
                a2=popt[3]
                b2=popt[4]
                c2=popt[5]
                a3=popt[6] 
                b3=popt[7]
                c3=popt[8]
                constant=popt[9]
                y_fit = func(x_fit,a1,b1,c1,a2,b2,c2,a3,b3,c3,constant)
                peak_1 = func(popt[2],*popt)
                Contrast_1 = round(100 - peak_1/max(y_fit)*100, 2)
                peak_2 = func(popt[5],*popt)
                Contrast_2 = round(100 - peak_2/max(y_fit)*100, 2)
                Contrast = [Contrast_1, Contrast_2]

                peak_3 = func(popt[8],*popt)
                Contrast_3 = round(100 - peak_3/max(y_fit)*100, 2)
                
                # Contrast_1 = round(popt[0],4)/constant
                FWHM_1 = 2*round(popt[1],4)
                Center_wavelength_1 = round(popt[2],3)
                # Contrast_2 = round(popt[3],4)/constant
                FWHM_2 = 2*round(popt[4],4)
                Center_wavelength_2 = round(popt[5],3)
                # Contrast_3 = round(popt[6],4)/constant
                FWHM_3 = 2*round(popt[7],4)
                Center_wavelength_3 = round(popt[8],3)
                # Contrast_4 = round(popt[9],4)/constant

                Center_Freq = round((Center_wavelength_1+Center_wavelength_2+Center_wavelength_3)/3,2)
                Peak_Diff_1 = round(Center_Freq-Center_wavelength_1,2)
                Peak_Diff_2 = round(Center_Freq-Center_wavelength_2,2)
                Peak_Diff_3 = round(Center_wavelength_3 - Center_Freq,2)


                self.ui.listWidget_fitting_results.clear()
                self.ui.listWidget_fitting_results.addItem('Contrast 1: '+str(Contrast_1)+'%')
                self.ui.listWidget_fitting_results.addItem('FWHM 1: '+str(FWHM_1)+' MHz')
                self.ui.listWidget_fitting_results.addItem('Center wavelength 1: '+str(Center_wavelength_1)+' MHz')
                self.ui.listWidget_fitting_results.addItem(' ')
                self.ui.listWidget_fitting_results.addItem('Contrast 2: '+str(Contrast_2)+'%')
                self.ui.listWidget_fitting_results.addItem('FWHM 2: '+str(FWHM_2)+' MHz')
                self.ui.listWidget_fitting_results.addItem('Center wavelength 2: '+str(Center_wavelength_2)+' MHz')
                self.ui.listWidget_fitting_results.addItem(' ')
                self.ui.listWidget_fitting_results.addItem('Contrast 3: '+str(Contrast_3)+'%')
                self.ui.listWidget_fitting_results.addItem('FWHM 3: '+str(FWHM_3)+' MHz')
                self.ui.listWidget_fitting_results.addItem('Center wavelength 3: '+str(Center_wavelength_3)+' MHz')
                self.ui.listWidget_fitting_results.addItem(' ')
                self.ui.listWidget_fitting_results.addItem('Center Freq: '+str(Center_Freq)+' MHz')
                self.ui.listWidget_fitting_results.addItem('Peak_Diff_1: '+str(Peak_Diff_1)+' MHz')
                self.ui.listWidget_fitting_results.addItem('Peak_Diff_2: '+str(Peak_Diff_2)+' MHz')
                self.ui.listWidget_fitting_results.addItem('Peak_Diff_3: '+str(Peak_Diff_3)+' MHz')

            elif NOP == 4:
                print('Fitting 4 Peaks')
                def func(x,a1,b1,c1,a2,b2,c2,a3,b3,c3,a4,b4,c4,constant):
                    return a1/math.pi*b1/(pow((x-c1),2)+pow(b1,2)) + a2/math.pi*b2/(pow((x-c2),2)+pow(b2,2)) + a3/math.pi*b3/(pow((x-c3),2)+pow(b3,2)) + a4/math.pi*b4/(pow((x-c4),2)+pow(b4,2)) + constant

                max_value = max(y_data)
                min_value = min(y_data)
                magnitude = max_value - min_value   
                if self.ui.checkBox_manually_input_FWHM.isChecked():
                    pass
                else:
                    FWHM_peaks = [5,5,5,5]
                
                init_vals = [-Contrast_peaks[0], FWHM_peaks[0], Freqs_peaks[0],-Contrast_peaks[1], FWHM_peaks[1], Freqs_peaks[1], -Contrast_peaks[2], FWHM_peaks[2], Freqs_peaks[2], -Contrast_peaks[3], FWHM_peaks[3], Freqs_peaks[3], max_value]
                popt, pcov = curve_fit(func, numpy.array(x_data), numpy.array(y_data), p0 = init_vals)
                a1=popt[0]  
                b1=popt[1]
                c1=popt[2]
                a2=popt[3]
                b2=popt[4]
                c2=popt[5]
                a3=popt[6] 
                b3=popt[7]
                c3=popt[8]
                a4=popt[9] 
                b4=popt[10]
                c4=popt[11]
                constant=popt[12]
                y_fit = func(x_fit,a1,b1,c1,a2,b2,c2,a3,b3,c3,a4,b4,c4,constant)
                peak_1 = func(popt[2],*popt)
                Contrast_1 = round(100 - peak_1/max(y_fit)*100, 2)
                peak_2 = func(popt[5],*popt)
                Contrast_2 = round(100 - peak_2/max(y_fit)*100, 2)
                Contrast = [Contrast_1, Contrast_2]

                peak_3 = func(popt[8],*popt)
                Contrast_3 = round(100 - peak_3/max(y_fit)*100, 2)
                peak_4 = func(popt[11],*popt)
                Contrast_4 = round(100 - peak_4/max(y_fit)*100, 2)
                
                # Contrast_1 = round(popt[0],4)/constant
                FWHM_1 = 2*round(popt[1],4)
                Center_wavelength_1 = round(popt[2],3)
                # Contrast_2 = round(popt[3],4)/constant
                FWHM_2 = 2*round(popt[4],4)
                Center_wavelength_2 = round(popt[5],3)
                # Contrast_3 = round(popt[6],4)/constant
                FWHM_3 = 2*round(popt[7],4)
                Center_wavelength_3 = round(popt[8],3)
                # Contrast_4 = round(popt[9],4)/constant
                FWHM_4 = 2*round(popt[10],4)
                Center_wavelength_4 = round(popt[11],3)

                Center_Freq = round((Center_wavelength_1+Center_wavelength_2+Center_wavelength_3+Center_wavelength_4)/4,2)
                Peak_Diff_1 = round(Center_Freq-Center_wavelength_1,2)
                Peak_Diff_2 = round(Center_Freq-Center_wavelength_2,2)
                Peak_Diff_3 = round(Center_wavelength_3 - Center_Freq,2)
                Peak_Diff_4 = round(Center_wavelength_4 - Center_Freq,2)

                self.ui.listWidget_fitting_results.clear()
                self.ui.listWidget_fitting_results.addItem('Contrast 1: '+str(Contrast_1)+'%')
                self.ui.listWidget_fitting_results.addItem('FWHM 1: '+str(FWHM_1)+' MHz')
                self.ui.listWidget_fitting_results.addItem('Center wavelength 1: '+str(Center_wavelength_1)+' MHz')
                self.ui.listWidget_fitting_results.addItem(' ')
                self.ui.listWidget_fitting_results.addItem('Contrast 2: '+str(Contrast_2)+'%')
                self.ui.listWidget_fitting_results.addItem('FWHM 2: '+str(FWHM_2)+' MHz')
                self.ui.listWidget_fitting_results.addItem('Center wavelength 2: '+str(Center_wavelength_2)+' MHz')
                self.ui.listWidget_fitting_results.addItem(' ')
                self.ui.listWidget_fitting_results.addItem('Contrast 3: '+str(Contrast_3)+'%')
                self.ui.listWidget_fitting_results.addItem('FWHM 3: '+str(FWHM_3)+' MHz')
                self.ui.listWidget_fitting_results.addItem('Center wavelength 3: '+str(Center_wavelength_3)+' MHz')
                self.ui.listWidget_fitting_results.addItem(' ')
                self.ui.listWidget_fitting_results.addItem('Contrast 4: '+str(Contrast_4)+'%')
                self.ui.listWidget_fitting_results.addItem('FWHM 4: '+str(FWHM_4)+' MHz')
                self.ui.listWidget_fitting_results.addItem('Center wavelength 4: '+str(Center_wavelength_4)+' MHz')
                self.ui.listWidget_fitting_results.addItem(' ')
                self.ui.listWidget_fitting_results.addItem('Center Freq: '+str(Center_Freq)+' MHz')
                self.ui.listWidget_fitting_results.addItem('Peak_Diff_1: '+str(Peak_Diff_1)+' MHz')
                self.ui.listWidget_fitting_results.addItem('Peak_Diff_2: '+str(Peak_Diff_2)+' MHz')
                self.ui.listWidget_fitting_results.addItem('Peak_Diff_3: '+str(Peak_Diff_3)+' MHz')
                self.ui.listWidget_fitting_results.addItem('Peak_Diff_4: '+str(Peak_Diff_4)+' MHz')
            

            elif NOP == 6:
                print('Fitting 6 Peaks')
                def func(x,a1,b1,c1,a2,b2,c2,a3,b3,c3,a4,b4,c4,a5,b5,c5,a6,b6,c6,constant):
                    return a1/math.pi*b1/(pow((x-c1),2)+pow(b1,2)) + a2/math.pi*b2/(pow((x-c2),2)+pow(b2,2)) + a3/math.pi*b3/(pow((x-c3),2)+pow(b3,2)) + a4/math.pi*b4/(pow((x-c4),2)+pow(b4,2)) + a5/math.pi*b5/(pow((x-c5),2)+pow(b5,2)) + a6/math.pi*b6/(pow((x-c6),2)+pow(b6,2)) + constant

                max_value = max(y_data)
                min_value = min(y_data)
                magnitude = max_value - min_value   
                if self.ui.checkBox_manually_input_FWHM.isChecked():
                    pass
                else:
                    FWHM_peaks = [5,5,5,5,5,5]
                
                init_vals = [-Contrast_peaks[0], FWHM_peaks[0], Freqs_peaks[0],-Contrast_peaks[1], FWHM_peaks[1], Freqs_peaks[1], -Contrast_peaks[2], FWHM_peaks[2], Freqs_peaks[2], -Contrast_peaks[3], FWHM_peaks[3], Freqs_peaks[3], -Contrast_peaks[4], FWHM_peaks[4], Freqs_peaks[4], -Contrast_peaks[5], FWHM_peaks[5], Freqs_peaks[5],max_value]
                popt, pcov = curve_fit(func, numpy.array(x_data), numpy.array(y_data), p0 = init_vals)
                a1=popt[0]  
                b1=popt[1]
                c1=popt[2]
                a2=popt[3]
                b2=popt[4]
                c2=popt[5]
                a3=popt[6] 
                b3=popt[7]
                c3=popt[8]
                a4=popt[9] 
                b4=popt[10]
                c4=popt[11]
                a5=popt[12] 
                b5=popt[13]
                c5=popt[14]
                a6=popt[15] 
                b6=popt[16]
                c6=popt[17]

                constant=popt[18]
                y_fit = func(x_fit,*popt)
                peak_1 = func(popt[2],*popt)
                Contrast_1 = round(100 - peak_1/max(y_fit)*100, 2)
                peak_2 = func(popt[5],*popt)
                Contrast_2 = round(100 - peak_2/max(y_fit)*100, 2)
                Contrast = [Contrast_1, Contrast_2]

                peak_3 = func(popt[8],*popt)
                Contrast_3 = round(100 - peak_3/max(y_fit)*100, 2)
                peak_4 = func(popt[11],*popt)
                Contrast_4 = round(100 - peak_4/max(y_fit)*100, 2)
            
                peak_5 = func(popt[11],*popt)
                Contrast_5 = round(100 - peak_3/max(y_fit)*100, 2)
                peak_6 = func(popt[14],*popt)
                Contrast_6 = round(100 - peak_4/max(y_fit)*100, 2)
                
                # Contrast_1 = round(popt[0],4)/constant
                FWHM_1 = 2*round(popt[1],4)
                Center_wavelength_1 = round(popt[2],3)
                # Contrast_2 = round(popt[3],4)/constant
                FWHM_2 = 2*round(popt[4],4)
                Center_wavelength_2 = round(popt[5],3)
                # Contrast_3 = round(popt[6],4)/constant
                FWHM_3 = 2*round(popt[7],4)
                Center_wavelength_3 = round(popt[8],3)
                # Contrast_4 = round(popt[9],4)/constant
                FWHM_4 = 2*round(popt[10],4)
                Center_wavelength_4 = round(popt[11],3)
                FWHM_5 = 2*round(popt[13],4)
                Center_wavelength_5 = round(popt[14],3)
                FWHM_6 = 2*round(popt[16],4)
                Center_wavelength_6 = round(popt[17],3)

                Center_Freq = round((Center_wavelength_1+Center_wavelength_2+Center_wavelength_3+Center_wavelength_4+Center_wavelength_5+Center_wavelength_6)/6,2)
                Peak_Diff_1 = round(Center_Freq-Center_wavelength_1,2)
                Peak_Diff_2 = round(Center_Freq-Center_wavelength_2,2)
                Peak_Diff_3 = round(Center_wavelength_3 - Center_Freq,2)
                Peak_Diff_4 = round(Center_wavelength_4 - Center_Freq,2)
                Peak_Diff_5 = round(Center_wavelength_5 - Center_Freq,2)
                Peak_Diff_6 = round(Center_wavelength_6 - Center_Freq,2)
            

                self.ui.listWidget_fitting_results.clear()
                self.ui.listWidget_fitting_results.addItem('Contrast 1: '+str(Contrast_1)+'%')
                self.ui.listWidget_fitting_results.addItem('FWHM 1: '+str(FWHM_1)+' MHz')
                self.ui.listWidget_fitting_results.addItem('Center wavelength 1: '+str(Center_wavelength_1)+' MHz')
                self.ui.listWidget_fitting_results.addItem(' ')
                self.ui.listWidget_fitting_results.addItem('Contrast 2: '+str(Contrast_2)+'%')
                self.ui.listWidget_fitting_results.addItem('FWHM 2: '+str(FWHM_2)+' MHz')
                self.ui.listWidget_fitting_results.addItem('Center wavelength 2: '+str(Center_wavelength_2)+' MHz')
                self.ui.listWidget_fitting_results.addItem(' ')
                self.ui.listWidget_fitting_results.addItem('Contrast 3: '+str(Contrast_3)+'%')
                self.ui.listWidget_fitting_results.addItem('FWHM 3: '+str(FWHM_3)+' MHz')
                self.ui.listWidget_fitting_results.addItem('Center wavelength 3: '+str(Center_wavelength_3)+' MHz')
                self.ui.listWidget_fitting_results.addItem(' ')
                self.ui.listWidget_fitting_results.addItem('Contrast 4: '+str(Contrast_4)+'%')
                self.ui.listWidget_fitting_results.addItem('FWHM 4: '+str(FWHM_4)+' MHz')
                self.ui.listWidget_fitting_results.addItem('Center wavelength 4: '+str(Center_wavelength_4)+' MHz')
                self.ui.listWidget_fitting_results.addItem(' ')
                self.ui.listWidget_fitting_results.addItem('Contrast 5: '+str(Contrast_5)+'%')
                self.ui.listWidget_fitting_results.addItem('FWHM 45: '+str(FWHM_5)+' MHz')
                self.ui.listWidget_fitting_results.addItem('Center wavelength 5: '+str(Center_wavelength_5)+' MHz')
                self.ui.listWidget_fitting_results.addItem(' ')
                self.ui.listWidget_fitting_results.addItem('Contrast 6: '+str(Contrast_6)+'%')
                self.ui.listWidget_fitting_results.addItem('FWHM 6: '+str(FWHM_6)+' MHz')
                self.ui.listWidget_fitting_results.addItem('Center wavelength 6: '+str(Center_wavelength_6)+' MHz')
                self.ui.listWidget_fitting_results.addItem(' ')
                self.ui.listWidget_fitting_results.addItem('Center Freq: '+str(Center_Freq)+' MHz')
                self.ui.listWidget_fitting_results.addItem('Peak_Diff_1: '+str(Peak_Diff_1)+' MHz')
                self.ui.listWidget_fitting_results.addItem('Peak_Diff_2: '+str(Peak_Diff_2)+' MHz')
                self.ui.listWidget_fitting_results.addItem('Peak_Diff_3: '+str(Peak_Diff_3)+' MHz')
                self.ui.listWidget_fitting_results.addItem('Peak_Diff_4: '+str(Peak_Diff_4)+' MHz')
                self.ui.listWidget_fitting_results.addItem('Peak_Diff_5: '+str(Peak_Diff_5)+' MHz')
                self.ui.listWidget_fitting_results.addItem('Peak_Diff_6: '+str(Peak_Diff_6)+' MHz')
            
            try:
                self.ui.dataMap_row.figure.clear()
                self.ui.dataMap_row.axes=self.ui.dataMap_row.figure.add_subplot(111)
            except:
                pass
            try:
                self.spectrum=self.ui.dataMap_row.axes.plot(self.freqs, y_data, '.')
                self.ui.dataMap_row.axes.plot(x_fit,y_fit)
                self.ui.dataMap_row.axes.set_xlabel('Frequency (MHz)')
                self.ui.dataMap_row.axes.set_ylabel('Intensity (Counts)')
                self.ui.dataMap_row.draw()
                self.x_fit = x_fit
                self.y_fit = y_fit

                path = os.path.split(self.last_path)
                print('saved path:',path[0])
                f = open(os.path.join(path[0],'ODMR_Fit.txt'),'w')
                for item in popt:
                    f.write(str(item)+'\n')
                f.close()
        
            except:
                pass

            '''
            f = open(save_path+'\\Fitting_4_peak.txt','w')
            f.write('Contrast 1:                   '+str(round(popt[0],4)/constant)+'%')
            f.write("\n")
            f.write('FWHM 1:                     '+str(2*round(popt[1],4)*1000)+'  MHz')
            f.write("\n")
            f.write('Center wavelength 1:        '+str(round(popt[2],3))+'  GHz')
            f.write("\n")
            f.write('Contrast 2:                   '+str(round(popt[3],4)/constant)+'%')
            f.write("\n")
            f.write('FWHM 2:                     '+str(2*round(popt[4],4)*1000)+'  MHz')
            f.write("\n")
            f.write('Center wavelength 2:        '+str(round(popt[5],3))+'  GHz')
            f.write("\n")
            f.write('Contrast 3:                   '+str(round(popt[6],4)/constant)+'%')
            f.write("\n")
            f.write('FWHM 3:                     '+str(2*round(popt[7],4)*1000)+'  MHz')
            f.write("\n")
            f.write('Center wavelength 3:        '+str(round(popt[8],3))+'  GHz')
            f.write("\n")
            f.write('Contrast 4:                   '+str(round(popt[9],4)/constant)+'%')
            f.write("\n")
            f.write('FWHM 4:                     '+str(2*round(popt[10],4)*1000)+'  MHz')
            f.write("\n")
            f.write('Center wavelength 4:        '+str(round(popt[11],3))+'  GHz')
            f.write("\n")
            f.close()
            '''
        except:
            QMessageBox.warning(self,"Warning","Try others fitting parameters!",QMessageBox.Yes | QMessageBox.No)


    @QtCore.pyqtSlot()
    def select(self):
        if self.cursor:
            self.cursor.disconnect_events()
            self.cursor=None
            self.reset_image()
        

        cid=self.ui.mplMap.mpl_connect('axes_enter_event',lambda event:self.ui.mplMap.setCursor(QtCore.Qt.CrossCursor))
        self._cid.append(cid)
        cid=self.ui.mplMap.mpl_connect('axes_leave_event',lambda event:self.ui.mplMap.setCursor(QtCore.Qt.ArrowCursor))
        self._cid.append(cid)
        cid=self.ui.mplMap.mpl_connect('button_press_event',self.select_drag_start)
        self._cid.append(cid)

    def select_drag_start(self,event):
        if event.inaxes:
            self.mousePressButton = event.button
            self.select_x0=event.xdata
            self.ui.lineEdit.setText(str(round(self.select_x0,3)))
            self.select_y0=event.ydata
            self.ui.lineEdit_2.setText(str(round(self.select_y0,3)))
            self._x0=event.x
            self._y0=event.y
            # print('x0:',self._x0,'y0:',self._y0)
            cid=self.ui.mplMap.mpl_connect('button_release_event',self.select_drag_end)  # reference at https://matplotlib.org/stable/api/backend_bases_api.html?highlight=event#matplotlib.backend_bases.Event
            self._cid.append(cid)
            cid=self.ui.mplMap.mpl_connect('motion_notify_event',self.select_dragging)
            self._cid.append(cid)

    def select_dragging(self,event):
        if event.inaxes:
            if self.mousePressButton == 1:
                # print('LEFT')
                self.select_x1=event.xdata
                self.ui.lineEdit.setText(str(round(self.select_x1,3)))
                self.select_y1=event.ydata
                self.ui.lineEdit_2.setText(str(round(self.select_y1,3)))

                x1=event.x
                y1=event.y
                # print('x1:',x1,'y1:',y1)
                x0=self._x0
                y0=self._y0
                height = self.ui.mplMap.figure.bbox.height
                # print('height:',height)
                y1 = height - y1
                y0 = height - y0
                # print('height - y0:',y0,'height - y1:',y1)

                if abs(x1 - x0)<abs(y1-y0):
                    if (x1-x0)*(y1-y0)>0:
                        rect = [int(val) for val in (x0, y0, x1 - x0, x1 - x0)]
                    else:
                        rect = [int(val) for val in (x0, y0, x1 - x0, x0 - x1)]
                else:
                    if (x1-x0)*(y1-y0)>0:
                        rect = [int(val) for val in (x0, y0, y1 - y0, y1 - y0)]
                    else:
                        rect = [int(val) for val in (x0, y0, y0 - y1, y1 - y0)]
                self.ui.mplMap.drawRectangle(rect)
            if self.mousePressButton == 3:
                print('RIGHT')

    def select_drag_end(self,event):
        
        self.ui.mplMap.setCursor(QtCore.Qt.ArrowCursor)
        for cid in self._cid:
            self.ui.mplMap.mpl_disconnect(cid)

    @QtCore.pyqtSlot()
    def reset_image(self):
        self.ui.mplMap.axes.imshow(self.image_ndarray)
        self.cursor=None
        self.ui.mplMap.draw()

    @QtCore.pyqtSlot()
    def select_onerow(self):
        if self.cursor:
            self.cursor.disconnect_events()
            self.cursor=None
            self.reset_image_onerow()
        

        cid=self.ui.dataMap_row.mpl_connect('axes_enter_event',lambda event:self.ui.dataMap_row.setCursor(QtCore.Qt.CrossCursor))
        self._cid.append(cid)
        cid=self.ui.dataMap_row.mpl_connect('axes_leave_event',lambda event:self.ui.dataMap_row.setCursor(QtCore.Qt.ArrowCursor))
        self._cid.append(cid)
        cid=self.ui.dataMap_row.mpl_connect('button_press_event',self.select_drag_start_onerow)
        self._cid.append(cid)

    def select_drag_start_onerow(self,event):
        if event.inaxes:
            self.select_x0_onerow=event.xdata
            self.ui.lineEdit.setText(str(round(self.select_x0_onerow,3)))
            self.select_y0_onerow=event.ydata
            self.ui.lineEdit_2.setText(str(round(self.select_y0_onerow,3)))
            self._x0=event.x
            self._y0=event.y
            cid=self.ui.dataMap_row.mpl_connect('button_release_event',self.select_drag_end_onerow)
            self._cid.append(cid)
            cid=self.ui.dataMap_row.mpl_connect('motion_notify_event',self.select_dragging_onerow)
            self._cid.append(cid)

    def select_dragging_onerow(self,event):
        if event.inaxes:
            self.select_x1_onerow=event.xdata
            self.ui.lineEdit.setText(str(round(self.select_x1_onerow,3)))
            self.select_y1_onerow=event.ydata
            self.ui.lineEdit_2.setText(str(round(self.select_y1_onerow,3)))

            x1=event.x
            y1=event.y
            x0=self._x0
            y0=self._y0
            height = self.ui.dataMap_row.figure.bbox.height
            y1 = height - y1
            y0 = height - y0
            print('x0:')
            print(x0)
            print('x1:')
            print(x1)
            print('y0:')
            print(y0)
            print('y1:')
            print(y1)
            rect = [int(val) for val in (x0, y0, x1 - x0, y1 - y0)]
            self.ui.dataMap_row.drawRectangle(rect)

    def select_drag_end_onerow(self,event):
        
        self.ui.dataMap_row.setCursor(QtCore.Qt.ArrowCursor)
        for cid in self._cid:
            self.ui.dataMap_row.mpl_disconnect(cid)
        self.ui.dataMap_row.axes.clear()
        self.reset_image_onerow()
        print('down')
        print(self.select_x0_onerow)
        print(self.select_x1_onerow)

    @QtCore.pyqtSlot()
    def reset_image_onerow(self):
        try:
            print('ssssss')
            print(int(self.select_x0_onerow))
            print(int(self.select_x1_onerow))
            self.ui.dataMap_row.axes.plot(numpy.arange(int(self.select_x0_onerow),int(self.select_x1_onerow)),self.image_ndarray[int(self.row),int(self.select_x0_onerow):int(self.select_x1_onerow)])  #这里的onerow对应着图片onerow
        except:
            self.ui.dataMap_row.axes.plot(self.image_ndarray[int(self.row),:])
        self.cursor=None
        self.ui.dataMap_row.axes.set_xlabel('Pixels')
        self.ui.dataMap_row.axes.set_ylabel('Intensity (a.u.)')
        self.ui.dataMap_row.draw()
    
    def export(self):
        print(self.last_path)
        prefix = self.ui.lineEdit_export_prefix.text()
        path = os.path.split(self.last_path)
        f = open(os.path.join(path[0],'ODMR.txt'),'w')
        f.write('FREQ; ')
        for data in self.freqs:
            f.write(str(data)+'; ')
        f.write('\n')
        f.write('ODMR; ')
        for data in self.all_images[:,int(self.row),int(self.col)]:
            f.write(str(data)+'; ')

        f.close()
        frame = copy.deepcopy(self.image_ndarray)
        frame[int(self.row),int(self.col)] = 0
        frame = frame.astype(numpy.uint16)
        Image.fromarray(frame).save(os.path.join(path[0],prefix+'_row'+str(int(self.row))+'_col'+str(int(self.col))+'.tif'))

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#  draw the odmr in roi

    def setup_mouse_events(self):
        # Press down
        def mouse_press(event):
            x = event.x()
            y = event.y()
            self.mousePressXY = (x,y)
            self.mousePressButton = event.button()
            def draw_point(painter):
                painter.setPen(QtGui.QPen(QtCore.Qt.red,1))
                painter.drawPoint(x,y)
            self._draw_on_image = draw_point
            self.update()
        self.ui.labelCCD.mousePressEvent = mouse_press
        # Drag (left button: circle. right button: rectangle. center button: ellipse)
        def mouse_drag(event):
            x = event.x()
            y = event.y()
            x0,y0 = self.mousePressXY
            self.mouseReleaseXY = (x,y)
            if self.mousePressButton == 1:
                xc = (x + x0) / 2
                yc = (y + y0) / 2
                r = numpy.sqrt((x-x0)**2 + (y-y0)**2) / 2
                def draw_circle(painter):
                    painter.setPen(QtGui.QPen(QtCore.Qt.red,1))
                    painter.drawEllipse(QtCore.QPointF(xc,yc),r,r)
                self._draw_on_image = draw_circle
            elif self.mousePressButton == 2:
                def draw_rect(painter):
                    painter.setPen(QtGui.QPen(QtCore.Qt.red,1))
                    painter.drawRect(QtCore.QRect(QtCore.QPoint(x0,y0), QtCore.QPoint(x,y)))
                self._draw_on_image = draw_rect
            else:
                def draw_ellipse(painter):
                    painter.setPen(QtGui.QPen(QtCore.Qt.red,1))
                    painter.drawEllipse(QtCore.QRect(QtCore.QPoint(x0,y0), QtCore.QPoint(x,y)))
                self._draw_on_image = draw_ellipse
            self.update()
        self.ui.labelCCD.mouseMoveEvent = mouse_drag
        # Release (setup region of interest)
        def mouse_release(event):
            x1, y1 = self.mousePressXY
            x2, y2 = self.mouseReleaseXY
            self.roi = numpy.zeros((512,512),dtype=numpy.uint16)
            if self.mousePressButton == 1:
                xc = (x1 + x2) / 2
                yc = (y1 + y2) / 2
                for x in range(self.roi.shape[1]):
                    for y in range(self.roi.shape[0]):
                        if (x-xc)**2 + (y-yc)**2 < ((x1-x2)**2 + (y1-y2)**2) / 4:
                            self.roi[y,x] = 1
            elif self.mousePressButton == 2:
                self.roi[min(x1, x2):max(x1, x2), min(y1, y2):max(y1, y2)] = 1
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
        self.ui.labelCCD.mouseReleaseEvent = mouse_release
    @QtCore.pyqtSlot()
    def reset_roi(self):
        self.roi = numpy.ones((512,512),dtype=int)
        self._draw_on_image = lambda painter: None
        self.update()

    def draw_odmr_in_roi(self):
        try:
            self.spectrum
            self.ui.dataMap_row.figure.clear()
            self.ui.dataMap_row.axes=self.ui.dataMap_row.figure.add_subplot(111)
        except:
            pass
        data_size = self.all_images.shape
        # print('data size:',data_size)
        roi = numpy.tile(self.roi, (data_size[0], 1, 1))
        # print('roi:',roi.shape)
        roi_bool = numpy.array(roi, dtype = bool)
        odmr_y = numpy.ma.masked_array(self.all_images, mask=~roi_bool)
        odmr_y_mean = numpy.mean(numpy.mean(odmr_y, 1),1)
        # print('odmr_y_mean:',odmr_y_mean.shape)
        # print('odmr_y_mean:',odmr_y_mean)
        print('freqs',self.freqs)

        self.x_data = self.freqs
        self.y_data = odmr_y_mean

        self.spectrum=self.ui.dataMap_row.axes.plot(self.freqs, odmr_y_mean)
        self.ui.dataMap_row.axes.set_xlabel('Frequency (MHz)')
        self.ui.dataMap_row.axes.set_ylabel('Intensity (Counts)')
        self.ui.dataMap_row.draw()
        import pickle

        path = os.path.split(self.last_path)
        print('path:',path)
        dataPath = os.path.join(path[0],'data.pickle')
        with open(dataPath,'wb') as dataPickle:
            pickle.dump([self.freqs, odmr_y_mean], dataPickle)

        path = os.path.split(self.last_path)
        print('saved path:',path[0])
        f = open(os.path.join(path[0],'ODMR.txt'),'w')
        
        f.write('FREQ: ')
        f.write('\n')
        for data in self.freqs:
            f.write(str(data)+'\n')
        f.write('\n')
        f.write('ODMR: ')
        f.write('\n')
        for data in odmr_y_mean:
            f.write(str(data)+'\n ')
        f.close()
        self.max_counts = numpy.max(odmr_y_mean)
        
        
    def select_peaks(self):
        self.reset_peaks()
        if self.cursor:
            self.cursor.disconnect_events()
            self.cursor=None
            self.reset_image_onerow()
        

        cid=self.ui.dataMap_row.mpl_connect('axes_enter_event',lambda event:self.ui.dataMap_row.setCursor(QtCore.Qt.CrossCursor))
        self._cid.append(cid)
        cid=self.ui.dataMap_row.mpl_connect('axes_leave_event',lambda event:self.ui.dataMap_row.setCursor(QtCore.Qt.ArrowCursor))
        self._cid.append(cid)
        cid=self.ui.dataMap_row.mpl_connect('button_press_event',self.left_single_click)
        self._cid.append(cid)

    def left_single_click(self, event):
        if event.inaxes:
            x=event.xdata # Return the x value in x_axis scale 返回坐标系内的鼠标左击点的 x值
            print('event.xdata:',event.xdata)  
            y=event.ydata # Return the y value in y_axis scale
            print('event.ydata:',event.ydata)
            self._x0=event.x # Return the x pixel in x_box 返回绘图框内的鼠标左击点的 x 的像素值
            self._y0=event.y
            print('event.y:',event.y)
            print('event.x:',event.x)
            contrast = round(self.max_counts-y,2)
            self.ui.plainTextEdit_peak_position.appendPlainText(str(round(x,2))+';'+str(contrast)+';')
            self.num_of_peaks = self.num_of_peaks + 1
            self.ui.lineEdit_peak_num.setText(str(self.num_of_peaks))

    def reset_peaks(self):
        self.ui.plainTextEdit_peak_position.clear()
        self.num_of_peaks = 0
        self.ui.lineEdit_peak_num.setText(str(self.num_of_peaks))
        self.draw_odmr_in_roi()
        self.ui.listWidget_fitting_results.clear()


    def undo_peaks(self):
        self.ui.plainTextEdit_peak_position.undo()
        self.num_of_peaks = self.num_of_peaks - 1
        self.ui.lineEdit_peak_num.setText(str(self.num_of_peaks))

if __name__ == '__main__':
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling,True)
    app=QtWidgets.QApplication(sys.argv)
    myWindow=mainGUI()
    myWindow.setWindowTitle(u'ODMR_Analysis')#设置窗体标题，本行可有可无。
    #myWindow.setWindowIcon(QIcon('ico.ico'))#调用QIcon构造函数时，我们需要提供要显示的图标的路径(相对或绝对路径)。同时注意：使用QIcon类型必须导入此模块from PyQt5.QtGui import QIcon
    myWindow.show()
    sys.exit(app.exec_())