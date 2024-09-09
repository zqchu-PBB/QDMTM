from PyQt5 import QtCore
import numpy
from PIL import Image
import os

class CW_Thread(QtCore.QThread):
    Signal_pulsed = QtCore.pyqtSignal(numpy.ndarray,name='cw')
    SIGNAL_camera=QtCore.pyqtSignal(numpy.ndarray,name='camera')
    def __init__(self, Info = [], loops = 1, save_path = [], ROI = [], Init = []):
        super().__init__()
        self.MW_power = Info[0]
        self.MW_sequence = Info[1]
        self.exposure_time = Info[2]
        self.AOM_Voltage = Info[3]
        self.AOM_Current = Info[4]
        self.loops = loops
        self.ROI = ROI
        self.save_path = save_path
        self.pb = Init[0]
        self.smiq = Init[1]
        self.ccd = Init[2]
        self.ccd.set_exposure(self.exposure_time)
        self.running = True

        Check_Existing = os.path.exists(self.save_path+'\\CW_ODMR_Images')
        if Check_Existing:
            pass
        else:
            os.mkdir(self.save_path+'\\CW_ODMR_Images')

        f = open(self.save_path+'\\Processed\\Info.txt','w')  #If the file doesn't exist, it will be created automatically. 若文件不存在，系统自动创建。'a'表示可连续写入到文件，保留原内容，在原内容之后写入。可修改该模式（'w+','w','wb'等）
        f.write('MW_power:'+str(self.MW_power)+' dBm')
        f.write("\n")
        f.write('MW_sequence:'+str(self.MW_sequence))
        f.write("\n")
        f.write('exposure_time:'+str(self.exposure_time)+' ms')
        f.write("\n")
        f.write('loops:'+str(self.loops))
        f.write("\n")
        f.write('AOM Voltage:'+str(self.AOM_Voltage)+' V')
        f.write("\n")
        f.write('AOM Current:'+str(self.AOM_Current)+' A')
        f.write("\n")
        f.close()
        Image.fromarray(self.ROI*65535).save(self.save_path+'\\Processed\\ROI.tif')

    def run(self):
        self.smiq.SetPower(str(self.MW_power))
        print(self.MW_sequence)
        self.smiq.on()
        self.pb.high([0, 1])

        try:
            for loop in range(0, self.loops, 1):
                for freq in self.MW_sequence:
                    self.pause = True
                    self.smiq.SetFrequence(str(freq))
                    self.msleep(3)
                    frame = self.ccd.snapshot()
                    data = [freq, frame, loop]
                    self.cw.emit(data)      #emit the frame go back to MainGui
                    if not self.running or numpy.max(frame) == 65535:
                        raise BaseException
                    self.msleep(27)
                    Frequency_2 = freq/1000000000
                    Frequency_str = str('%.3f' % Frequency_2)
                    Image.fromarray(frame).save(self.save_path+'\\CW_ODMR_Images\\loop'+str(loop)+'_freq'+ Frequency_str +'GHz_power'+str(self.MW_power)+'dBm_MW.tif')
                    while self.pause == True:
                        print('')

        except:
            pass
        f = open(self.save_path+'\\Processed\\Info.txt','a')
        f.write('Measurement loops:'+str(loop))
        f.write("\n")
        f.close()
        self.running = True
        self.pb.high([])
        self.smiq.off()
        self.ccd.set_trigger_mode('Internal')
        print('CW ODMR DOWN')
        
