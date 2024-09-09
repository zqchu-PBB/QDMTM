from PyQt5 import QtCore
import numpy
import time
class CameraTemperatureMonitoringThread(QtCore.QThread):
    '''
    Camera module as a thread, based on PyQt5.QtCore.QThread parameters:
    @hardware: python object of hardware control
    '''

    SIGNAL_camera=QtCore.pyqtSignal(numpy.ndarray,name='temperature')

    def __init__(self, Init = []):
        super().__init__()
        self.ccd = Init[2]

    def run(self):
        while True:
            temp = self.ccd.get_temperature()
            self.temperature.emit(temp.value)
            time.sleep(0.05)