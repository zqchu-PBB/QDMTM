from PyQt5 import QtCore
import numpy

class CameraThread(QtCore.QThread):
    '''
    Camera module as a thread, based on PyQt5.QtCore.QThread parameters:
    @hardware: python object of hardware control
    '''
    SIGNAL_camera=QtCore.pyqtSignal(numpy.ndarray,name='camera')

    def __init__(self, exposure_time = [], Init = []):
        super().__init__()
        self.running = True
        self.exposure_time = exposure_time
        self.pb = Init[0]
        self.ccd = Init[2]
        self.ccd.set_trigger_mode('Internal')
    def run(self):
        print('run')
        self.ccd.set_exposure(self.exposure_time)
        self.ccd.live_start()
        try:
            self.ccd.live_start()
            while self.running:
                self.pause = True
                frame = self.ccd.live_readout()
                self.camera.emit(frame)
                if numpy.max(frame) == 65535:
                    raise BaseException
                while self.pause == True:
                    print('')    
        except:
            pass
        self.ccd.live_stop()
        self.pb.high([])

