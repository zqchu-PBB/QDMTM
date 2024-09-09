from PyQt5 import QtCore
import time

class PiStageThread(QtCore.QThread):
    '''
    This thread is for display the position in the mainwindow.
    '''

    def __init__(self, Init = [], UI = []):
        super().__init__()
        self.pi_stage = Init[3]
        self.ui = UI
        # self.ui.pushButton_PiStage_Check.setEnabled(False)
    
    def run(self):
        while True:
            pos = self.pi_stage.check_position()
            self.ui.label_PiStage_X.setText(str(pos[0]))
            self.ui.label_PiStage_Y.setText(str(pos[1]))
            self.ui.label_PiStage_Z.setText(str(pos[2]))
            time.sleep(0.1)

