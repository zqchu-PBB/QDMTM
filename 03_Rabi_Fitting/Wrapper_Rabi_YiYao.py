import sys
import os
import io
from GUI.GUI import Ui_MainWindow
from PyQt5 import QtWidgets,QtCore
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib.widgets import Cursor
from PIL import Image
from PyQt5.QtWidgets import QFileDialog
import numpy as np
from scipy.optimize import curve_fit
import pickle
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QFileDialog

class mainGUI(QtWidgets.QMainWindow):
    def __init__(self,parent=None):
        QtWidgets.QWidget.__init__(self,parent)
        self.ui=Ui_MainWindow()
        self.ui.setupUi(self)
        self.last_path = None
        
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
        self.ui.dataMap_row.figure.subplots_adjust(top=0.95,bottom=0.15,right=0.95,left=0.10)
        # self.ui.dataMap_row.figure.subplots_adjust(top=1,bottom=0,right=1,left=0)

        self.ui.mplTb=NavigationToolbar(self.ui.dataMap_row,self.ui.tbwidget_row)
        self.ui.mplTb.setParent(self.ui.tbwidget_row)
        self.ui.mplTb.setGeometry(QtCore.QRect(QtCore.QPoint(0,0),self.ui.tbwidget_row.size()))
        self.cursor=None
        self._cid=[]

        self.ui.pushButton_open.clicked.connect(self.open)
        self.ui.pushButton_fit.clicked.connect(self.fit)
        # self.ui.pushButton_export.clicked.connect(self.export)
        self.ui.pushButton_reset.clicked.connect(self.reset_roi)
        self.ui.pushButton_show_rabi_in_roi.clicked.connect(self.show_rabi_in_roi)

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

        self.roi = np.ones((512,512),dtype=int)
        
        self.setup_mouse_events()

    # The format of the np.ndarray is [row, col]
    def open(self):
        if self.last_path:
            open_path, _ = QFileDialog.getOpenFileName(self, "Select Data File", self.last_path, "All Files (*);;Text Files (*.txt)")
        else:
            open_path, _ = QFileDialog.getOpenFileName(self, "Select Data File", "", "All Files (*);;Text Files (*.txt)")
        if open_path:
            self.last_path = open_path
            # self.ui.lineEdit_Open_Path.setText(open_path)
            with open(open_path,'rb') as dataFile:
                loaded_data = pickle.load(dataFile)

            self.loops = loaded_data['Loops']
            self.all_images = loaded_data['Y']
            self.x_time = loaded_data['X']
            self.first_frame_show = np.array(self.all_images[0,0,:,:]) # turn the first image into np array
            self.ui.mplMap.axes.imshow(self.first_frame_show)
            self.ui.mplMap.axes.set_xlabel('Pixels')
            self.ui.mplMap.axes.set_ylabel('Pixels')
            
            self.cursor=None
            self.ui.mplMap.draw()
            print(self.first_frame_show.shape)

            frame = self.first_frame_show
            normImage = (frame-np.min(frame)) * (256/(np.max(frame)-np.min(frame)))
            image8Bit = Image.fromarray(np.array(normImage, dtype=np.uint8), mode='L')
            # pix = QtGui.QPixmap.fromImage(ImageQt.ImageQt(image8Bit))
            
            def pil_image_to_pixmap(pil_image):
                """Convert a PIL Image to QPixmap."""
                buffer = io.BytesIO()
                pil_image.save(buffer, format="PNG")
                buffer.seek(0)
                pixmap = QtGui.QPixmap()
                pixmap.loadFromData(buffer.read())
                return pixmap
            pix = pil_image_to_pixmap(image8Bit)
            
            self.ui.labelCCD.setPixmap(pix)
        else:
            print("No file selected.")

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
            self.ui.lineEdit_counts.setText(str(self.first_frame_show[int(self.row),int(self.col)]))
            self.cursor.disconnect_events()
            self.profile_one_row(self.row, self.col)
    
    def profile_one_row(self, row, col):
        try:
            # self.spectrum # NOTE ??
            self.ui.dataMap_row.figure.clear()
            self.ui.dataMap_row.axes=self.ui.dataMap_row.figure.add_subplot(111)
        except:
            pass
        self.spectrum=self.ui.dataMap_row.axes.plot(self.x_time, self.all_images[:, int(row), int(col)])
        self.ui.dataMap_row.axes.set_xlabel('Time (nm)')
        self.ui.dataMap_row.axes.set_ylabel('Contrast')
        self.ui.dataMap_row.draw()


    @QtCore.pyqtSlot()
    # The format of the np.ndarray is [row, col]
    def fit(self):
        def rabi_curve(x, amplitude, omega_rabi, phi, t2_star, constant):
            """
            The function for rabi curve.
            :param x: time
            :param amplitude: Rabi oscillation Amplitude
            :param omega_rabi: Rabi Frequency
            :param phi: phase offsite (-pi/2 for ideal Rabi oscillation)
            :param t2_star: Driven coherence time
            :param constant: offset
            :return: rabi curve based on the given x
            """
            return amplitude * np.cos(2*np.pi*omega_rabi*x + phi) * np.exp(- np.power(x / t2_star, 2)) + constant
        period = None
        try:
            period = float(self.ui.lineEdit_input_period.text())
        except:
            pass
        max_value = max(self.y_data)
        min_value = min(self.y_data)
        min_index, = np.where(self.y_data == min_value)[0]
        magnitude_guess = max_value - min_value
        x_min = self.x_data[min_index]

        if period:
            omega_guess = 1/(2*period)
        else:
            omega_guess = 1/(2*x_min)
            print(x_min)

        phi_guess = 0.0
        t2_star_guess = 1000
        constant_guess = self.y_data[-1]
        init_vals = [magnitude_guess, omega_guess, phi_guess, t2_star_guess, constant_guess]
        popt, pcov = curve_fit(rabi_curve, self.x_data, self.y_data, p0 = init_vals, sigma = self.y_err)
        magnitude = popt[0]
        omega = popt[1] 
        omega_in_mhz = omega * 1e3 # convert to MHz
        phi = popt[2]
        t2_star = popt[3]
        constant = popt[4]
        x_fit = np.array(range(self.x_data[0], self.x_data[-1], 1))
        y_fit = rabi_curve(x_fit, magnitude, omega, phi, t2_star, constant)
        Contrast = round((max(y_fit)-min(y_fit))/max(y_fit)*100, 2)
        pi_pulse = 1.0 / omega / 2

        try:
            self.ui.dataMap_row.figure.clear()
            self.ui.dataMap_row.axes = self.ui.dataMap_row.figure.add_subplot(111)
        except Exception as e:
            print(f"Error clearing and setting up the plot: {e}")

        # plot the data and the fitted curve
        try:
            self.ui.dataMap_row.axes.errorbar(self.x_data, self.y_data, yerr=self.y_err, fmt='.', label='Data')
            self.ui.dataMap_row.axes.plot(x_fit, y_fit, label='Fit')
            self.ui.dataMap_row.axes.set_xlabel('Time (ns)')
            self.ui.dataMap_row.axes.set_ylabel('Contrast')
            self.ui.dataMap_row.axes.legend()
            self.ui.dataMap_row.draw()
        except Exception as e:
            print(f"Error plotting data: {e}")

        # update the fitting results list
        try:
            self.ui.listWidget_fitting_results.clear()
            fitting_results = (f'Contrast: {Contrast}%\n'
                            f'Rabi Frequency: {round(omega_in_mhz, 6)} MHz\n'
                            f'T2_star: {round(t2_star, 3)} ns\n'
                            f'Pi Pulse: {round(pi_pulse, 3)} ns')
            self.ui.listWidget_fitting_results.addItem(fitting_results)
        except Exception as e:
            print(f"Error updating fitting results list: {e}")

        # save the fitting results to a text file
        try:
            fit_data_save_path = os.path.dirname(self.last_path)

            with open(os.path.join(fit_data_save_path, 'Rabi_Fit_Results.txt'), 'w', encoding='utf-8') as f:
                f.write(fitting_results) # save the fitting results to the same folder as the data
            self.ui.listWidget_fitting_results.addItem(f'Fitting results have been saved to {fit_data_save_path}') 
        except IOError as e:
            print(f"An error occurred while saving fitting results: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")


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
        self.ui.mplMap.axes.imshow(self.first_frame_show)
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
            # print('ssssss')
            print(int(self.select_x0_onerow))
            print(int(self.select_x1_onerow))
            self.ui.dataMap_row.axes.plot(np.arange(int(self.select_x0_onerow),int(self.select_x1_onerow)),self.first_frame_show[int(self.row),int(self.select_x0_onerow):int(self.select_x1_onerow)])  #这里的onerow对应着图片onerow
        except:
            self.ui.dataMap_row.axes.plot(self.first_frame_show[int(self.row),:])
        self.cursor=None
        self.ui.dataMap_row.axes.set_xlabel('Pixels')
        self.ui.dataMap_row.axes.set_ylabel('Intensity (a.u.)')
        self.ui.dataMap_row.draw()
    

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
                r = np.sqrt((x-x0)**2 + (y-y0)**2) / 2
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
            self.roi = np.zeros((512,512),dtype=np.uint16)
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
            if np.max(self.roi) == 0:
                self.roi[x1, y1] = 1
        self.ui.labelCCD.mouseReleaseEvent = mouse_release
    @QtCore.pyqtSlot()
    def reset_roi(self):
        self.roi = np.ones((512,512),dtype=int)
        self._draw_on_image = lambda painter: None
        self.update()

    def show_rabi_in_roi(self):
        try:
            # self.spectrum
            self.ui.dataMap_row.figure.clear()
            self.ui.dataMap_row.axes=self.ui.dataMap_row.figure.add_subplot(111)
        except:
            pass
        data_size = self.all_images.shape
        roi = np.tile(self.roi, (data_size[0],data_size[1], 1, 1))
        roi_bool = np.array(roi, dtype = bool)
        data_rabi_roi_y_all_loops = np.ma.masked_array(self.all_images, mask=~roi_bool)
        data_rabi_y_mean_all_loops = np.mean(data_rabi_roi_y_all_loops, axis=(2, 3))
        data_rabi_y_mean = np.mean(data_rabi_y_mean_all_loops, axis=0)
        sample_size = data_rabi_y_mean_all_loops.shape[0]
        std_dev = np.std(data_rabi_y_mean_all_loops, axis=0)
        standard_error = std_dev / np.sqrt(sample_size)

        self.x_data = self.x_time
        self.y_data = data_rabi_y_mean
        self.y_err = standard_error

        self.ui.dataMap_row.axes.plot(self.x_data, self.y_data)
        self.ui.dataMap_row.axes.set_xlabel('Time (ns)')
        self.ui.dataMap_row.axes.set_ylabel('Contrast')
        self.ui.dataMap_row.draw()


if __name__ == '__main__':
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling,True)
    app=QtWidgets.QApplication(sys.argv)
    myWindow=mainGUI()
    myWindow.setWindowTitle('Rabi_Analysis')# set the title of the window
    myWindow.show()
    sys.exit(app.exec_())