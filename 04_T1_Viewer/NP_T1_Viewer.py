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
import tifffile as tif
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
        
        fig=Figure()
        self.ui.mplMap=FigureCanvas(fig)
        self.ui.mplMap.setParent(self.ui.mplwidget)
        self.ui.mplMap.axes=fig.add_subplot(111)
        self.ui.mplMap.axes.axis('off')
        self.ui.mplMap.setGeometry(QtCore.QRect(QtCore.QPoint(0,0),self.ui.mplwidget.size()))
        self.ui.mplMap.figure.subplots_adjust(top=1.001,bottom=0,right=1.001,left=-0.001)
        self.ui.mplMap.figure.subplots_adjust(top=1.001,bottom=0,right=1.001,left=-0.001)
        
        self.ui.mplTb=NavigationToolbar(self.ui.mplMap,self.ui.tbwidget)
        self.ui.mplTb.setParent(self.ui.tbwidget)
        self.ui.mplTb.setGeometry(QtCore.QRect(QtCore.QPoint(0,0),self.ui.tbwidget.size()))

        fig=Figure()
        self.ui.dataMap_1=FigureCanvas(fig)
        self.ui.dataMap_1.setParent(self.ui.widget_row)
        self.ui.dataMap_1.axes=fig.add_subplot(111)
        self.ui.dataMap_1.axes.axis('off')
        self.ui.dataMap_1.setGeometry(QtCore.QRect(QtCore.QPoint(0,0),self.ui.widget_row.size()))
        self.ui.dataMap_1.figure.subplots_adjust(top=0.95,bottom=0.2,right=0.95,left=0.15)

        self.ui.mplTb=NavigationToolbar(self.ui.dataMap_1,self.ui.tbwidget_row)
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
        # self.ui.pushButton.clicked.connect(self.mark)
        self.ui.pushButton_fit.clicked.connect(self.fit)
        self.ui.checkBox_set_x_to_log.stateChanged.connect(self.set_x_axis_log)
        self.ui.pushButton_select_pixel.clicked.connect(self.select_pixel)



    # The format of the numpy.ndarray is [row, col]

    def open(self):
        # try:
        if self.last_path:
            file_path, file_type = QFileDialog.getOpenFileName(self, "选择文件", self.last_path, "All Files (*);;Text Files (*.txt)")
        else:
            file_path, file_type = QFileDialog.getOpenFileName(self, "选择文件", os.path.join('D:','OneDrive - connect.hku.hk','1-Experimental Data'), "All Files (*);;Text Files (*.txt)")
        if file_type:
            self.last_path = file_path
        print('file_path:', file_path)
        rootpath = os.path.split(file_path)[0]
        print('rootpath:', rootpath)
        
        with open(file_path,'rb') as dataFile:
            self.tau_sequence, self.all_raw_data = pickle.load(dataFile)
        print('all_raw_data:', self.all_raw_data.shape)
        file_path_all_t1_mapping = os.path.join(rootpath, 'all_t1_mapping.pickle')
        with open(file_path_all_t1_mapping,'rb') as dataFile:
            self.all_t1_mapping = pickle.load(dataFile)
        
        self.loop = 4
        print(self.tau_sequence)
        print(self.all_raw_data.shape)
        print(self.all_t1_mapping[self.loop-1])

        self.image_ndarray = numpy.array(self.all_t1_mapping[self.loop-1])

        self.ui.mplMap.axes.imshow(self.image_ndarray)
        self.ui.mplMap.axes.set_xlabel('Pixels')
        self.ui.mplMap.axes.set_ylabel('Pixels')
        
        self.cursor=None
        self.ui.mplMap.draw()
        print(self.image_ndarray.shape)


    @QtCore.pyqtSlot()
    def select_pixel(self):
        self.cursor=Cursor(self.ui.mplMap.axes, useblit=True, color='red', linewidth=0.5)
        self.cursor.connect_event('button_press_event',self.mark_end)
        self.ui.mplMap.draw()

    @QtCore.pyqtSlot()
    def mark_end(self,event):
        if event.inaxes:
            self.col=round(event.xdata)
            self.row=round(event.ydata)
            self.cursor.disconnect_events()
            self.profile_one_row(self.row, self.col)
    
    def profile_one_row(self, row, col):
        try:
            self.spectrum
            self.ui.dataMap_1.figure.clear()
            self.ui.dataMap_1.axes=self.ui.dataMap_1.figure.add_subplot(111)
        except:
            pass
        self.spectrum=self.ui.dataMap_1.axes.plot(self.tau_sequence, self.all_raw_data[:, self.loop, int(row), int(col)])
        self.ui.dataMap_1.axes.set_xlabel('Delay time (ns)')
        self.ui.dataMap_1.axes.set_ylabel('Intensity (a.u.)')
        self.ui.dataMap_1.axes.axis('on')
        if self.ui.checkBox_set_x_to_log.isChecked() == True:
            self.ui.dataMap_1.axes.set_xscale('log')
        elif self.ui.checkBox_set_x_to_log.isChecked() == False:
            self.ui.dataMap_1.axes.set_xscale('linear')
        self.ui.dataMap_1.draw()

        self.data_t1 = self.all_raw_data[:, self.loop, int(row), int(col)]

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
        # try:
        self.t1_fitting()
        # except:
        #     QMessageBox.warning(self,"Warning","Fit failed!",QMessageBox.Yes | QMessageBox.No)

    def t1_fitting(self):
        def func(x,a,T,c,constant):
            return a*numpy.exp(-(x/T)**c) + constant
        
        def func_with_background(x, a,T,c,k,constant):
            return a*numpy.exp(-(x/T)**c) + k*x+ constant
        
        x_data = self.tau_sequence
        y_data = self.data_t1

        k = (y_data[-1] - y_data[0])/(x_data[-1] - x_data[0])
        constant = numpy.min(y_data)
        magnitude = numpy.max(y_data) - numpy.min(y_data)
        init_vals = [magnitude, 20000, 1, constant]
        #param_bounds = ([0, 0, 0.95, 0.95],[0.1, 2000000, 1.05, 1.05])
        #try:
        popt, pcov = curve_fit(func, numpy.array(x_data), numpy.array(y_data), p0 = init_vals, maxfev = 50000)   
        t1 = round(popt[1]/1000,2)
        t1_pcov = numpy.sqrt(pcov[1,1])

        #except:
            #pass

        self.ui.listWidget_fitting_results.clear()
        self.ui.listWidget_fitting_results.addItem('T1: '+str(t1)+'us')


        print('popt:', popt)
        x_fit = numpy.arange(x_data[0], x_data[-1], 100)
        y_fit = func(x_fit, *popt)
 


        self.spectrum_1=self.ui.dataMap_1.axes.plot(self.tau_sequence, y_data, 'b.')
        self.spectrum_1=self.ui.dataMap_1.axes.plot(x_fit, y_fit, 'r')
        self.ui.dataMap_1.axes.set_xlabel('Deley Time (ns)')
        self.ui.dataMap_1.axes.set_ylabel('Intensity (Counts)')

        if self.ui.checkBox_set_x_to_log.isChecked() == True:
            self.ui.dataMap_1.axes.set_xscale('log')
        elif self.ui.checkBox_set_x_to_log.isChecked() == False:
            self.ui.dataMap_1.axes.set_xscale('linear')
        self.ui.dataMap_1.draw()



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
        

        cid=self.ui.dataMap_1.mpl_connect('axes_enter_event',lambda event:self.ui.dataMap_1.setCursor(QtCore.Qt.CrossCursor))
        self._cid.append(cid)
        cid=self.ui.dataMap_1.mpl_connect('axes_leave_event',lambda event:self.ui.dataMap_1.setCursor(QtCore.Qt.ArrowCursor))
        self._cid.append(cid)
        cid=self.ui.dataMap_1.mpl_connect('button_press_event',self.select_drag_start_onerow)
        self._cid.append(cid)

    def select_drag_start_onerow(self,event):
        if event.inaxes:
            self.select_x0_onerow=event.xdata
            self.ui.lineEdit.setText(str(round(self.select_x0_onerow,3)))
            self.select_y0_onerow=event.ydata
            self.ui.lineEdit_2.setText(str(round(self.select_y0_onerow,3)))
            self._x0=event.x
            self._y0=event.y
            cid=self.ui.dataMap_1.mpl_connect('button_release_event',self.select_drag_end_onerow)
            self._cid.append(cid)
            cid=self.ui.dataMap_1.mpl_connect('motion_notify_event',self.select_dragging_onerow)
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
            height = self.ui.dataMap_1.figure.bbox.height
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
            self.ui.dataMap_1.drawRectangle(rect)

    def select_drag_end_onerow(self,event):
        
        self.ui.dataMap_1.setCursor(QtCore.Qt.ArrowCursor)
        for cid in self._cid:
            self.ui.dataMap_1.mpl_disconnect(cid)
        self.ui.dataMap_1.axes.clear()
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
            self.ui.dataMap_1.axes.plot(numpy.arange(int(self.select_x0_onerow),int(self.select_x1_onerow)),self.image_ndarray[int(self.row),int(self.select_x0_onerow):int(self.select_x1_onerow)])  #这里的onerow对应着图片onerow
        except:
            self.ui.dataMap_1.axes.plot(self.image_ndarray[int(self.row),:])
        self.cursor=None
        self.ui.dataMap_1.axes.set_xlabel('Pixels')
        self.ui.dataMap_1.axes.set_ylabel('Intensity (a.u.)')
        self.ui.dataMap_1.draw()
    
    def export(self):
        print(self.last_path)
        prefix = self.ui.lineEdit_export_prefix.text()
        path = os.path.split(self.last_path)
        f = open(os.path.join(path[0],prefix+'_row'+str(int(self.row))+'_col'+str(int(self.col))+'.txt'),'w')
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

    
    def set_x_axis_log(self):
        try:
            self.spectrum
            self.ui.dataMap_1.figure.clear()
            self.ui.dataMap_1.axes=self.ui.dataMap_1.figure.add_subplot(111)
            self.spectrum_2
            self.ui.dataMap_2.figure.clear()
            self.ui.dataMap_2.axes=self.ui.dataMap_2.figure.add_subplot(111)

        except:
            pass
        try:
            if self.ui.checkBox_set_x_to_log.isChecked() == True:
                self.data_t1 = numpy.array(self.data_t1)
                self.data_background = numpy.array(self.data_background)
                self.spectrum=self.ui.dataMap_1.axes.plot(self.tau_sequence, self.data_t1, 'b')
                self.spectrum=self.ui.dataMap_1.axes.plot(self.tau_sequence, self.data_background, 'r')
                self.ui.dataMap_1.axes.set_xscale('log') 
                self.ui.dataMap_1.axes.set_xlabel('Deley Time (ns)')
                self.ui.dataMap_1.axes.set_ylabel('Intensity (Counts)')
                self.ui.dataMap_1.draw()

                # Draw subtract curve in right panel
                self.spectrum=self.ui.dataMap_2.axes.plot(self.tau_sequence, self.subtract_t1_background, 'b')
                self.ui.dataMap_2.axes.set_xlabel('Deley Time (ns)')
                self.ui.dataMap_2.axes.set_xscale('log') 
                self.ui.dataMap_2.axes.set_ylabel('Intensity (Counts)')
                self.ui.dataMap_2.draw()
            else:
                self.data_t1 = numpy.array(self.data_t1)
                self.data_background = numpy.array(self.data_background)
                self.spectrum=self.ui.dataMap_1.axes.plot(self.tau_sequence, self.data_t1, 'b')
                self.spectrum=self.ui.dataMap_1.axes.plot(self.tau_sequence, self.data_background, 'r')
                self.ui.dataMap_1.axes.set_xscale('linear') 
                self.ui.dataMap_1.axes.set_xlabel('Deley Time (ns)')
                self.ui.dataMap_1.axes.set_ylabel('Intensity (Counts)')
                self.ui.dataMap_1.draw()

                # Draw subtract curve in right panel
                self.spectrum=self.ui.dataMap_2.axes.plot(self.tau_sequence, self.subtract_t1_background, 'b')
                self.ui.dataMap_2.axes.set_xscale('linear') 
                self.ui.dataMap_2.axes.set_xlabel('Deley Time (ns)')
                self.ui.dataMap_2.axes.set_ylabel('Intensity (Counts)')
                self.ui.dataMap_2.draw()
        except:
            pass

        

if __name__ == '__main__':
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling,True)
    app=QtWidgets.QApplication(sys.argv)
    myWindow=mainGUI()
    myWindow.setWindowTitle(u'T1 Version 2021')#设置窗体标题，本行可有可无。
    #myWindow.setWindowIcon(QIcon('ico.ico'))#调用QIcon构造函数时，我们需要提供要显示的图标的路径(相对或绝对路径)。同时注意：使用QIcon类型必须导入此模块from PyQt5.QtGui import QIcon
    myWindow.show()
    sys.exit(app.exec_())