from PyQt5 import QtCore
import numpy
from PIL import Image
import os

class rabi_thread(QtCore.QThread):
    Signal_pulsed = QtCore.pyqtSignal(numpy.ndarray,name='Rabi')

    def __init__(self, Info = [], loops = 1, save_path = [], ROI = [], Init = []):
        super().__init__()
        self.MW_power = Info[0]
        self.MW_freq = Info[1]
        self.AOM_duration = Info[2]
        self.MW_start = Info[3]
        self.MW_duration_sweeping = Info[4]
        self.repetitions = Info[5]
        self.gap = Info[6]
        self.AOM_Voltage = Info[7]

        self.loops = loops
        self.save_path = save_path
        self.ROI = ROI
        self.sequences = []
        self.frames_MW = []
        self.frames_None = []    

        self.smiq = Init[1]
        self.pb = Init[0]
        self.ccd = Init[2]
        self.ccd.set_trigger_mode('Bulb')

        self.running = True

        Check_Existing = os.path.exists(self.save_path+'\\Rabi_Images')
        if Check_Existing:
            pass
        else:
            os.mkdir(self.save_path+'\\Rabi_Images')
        f = open(self.save_path+'\\Processed\\Rabi_Information.txt','w')
        f.write('MW_power:'+str(self.MW_power)+' dBm')
        f.write("\n")
        f.write('MW_freq:'+str(self.MW_freq)+' Hz')
        f.write("\n")
        f.write('AOM_duration:'+str(self.AOM_duration)+' ns')
        f.write("\n")
        f.write('MW_start:'+str(self.MW_start)+' ns')
        f.write("\n")
        f.write('MW_duration_sweeping:'+str(self.MW_duration_sweeping)+' ns')
        f.write("\n")
        f.write('repetitions:'+str(self.repetitions))
        f.write("\n")
        f.write('gap:'+str(self.gap)+' ns')
        f.write("\n")
        f.write('loops:'+str(self.loops))
        f.write("\n")
        f.write('AOM power:'+str(self.AOM_Voltage)+' dBm')
        f.write("\n")
        f.close()
        Image.fromarray(self.ROI*65535).save(self.save_path+'\\Processed\\ROI.tif')

    def run(self):
        self.smiq.SetPower(str(self.MW_power))
        self.smiq.SetFrequence(str(self.MW_freq))
        self.smiq.on()
        self.ccd.live_start()
        try:
            for loop in range(0, self.loops):
                for t in self.MW_duration_sweeping:
                    for i in range(2):
                        print(1)
                        self.pause = True
                        if i == 0: # Don't apply microwave to the nv centers.
                            MW_seq = [(self.MW_start + t, 0)]
                            laser_seq = [(self.MW_start + t + self.gap, 0), (self.AOM_duration, 1)]

                        else: # Apply microwave to the nv centers.
                            MW_seq = [(self.MW_start, 0), (t, 1)]
                            laser_seq = [(self.MW_start + t + self.gap, 0), (self.AOM_duration, 1)]

                        self.sequences = [[0, laser_seq], [1, MW_seq]]
                        self.pb.Sequence(self.sequences, self.repetitions)
                        self.pb.run()
                        frame = self.ccd.live_readout()  
                        if i == 0:
                            Point_Data = [t, frame, 0, loop]
                            self.Rabi.emit(Point_Data) 
                            Image.fromarray(frame).save(self.save_path+'\\Rabi_Images\\loop'+str(loop)+'_None'+str(t)+'.tif')
                        else:
                            Point_Data = [t, frame, 1, loop]
                            self.Rabi.emit(Point_Data) 
                            Image.fromarray(frame).save(self.save_path+'\\Rabi_Images\\loop'+str(loop)+'_MW'+str(t)+'.tif')
                        if not self.running or numpy.max(frame) == 65535:
                            raise BaseException
                        # self.msleep(40)  
                        while self.pause == True:
                            print('')                     
        except:
            pass
        self.running = True
        self.smiq.off()
        f = open(self.save_path+'\\Processed\\Rabi_Information.txt','a')
        f.write('Measurement loops:'+str(loop))
        f.write("\n")
        f.close()
        self.ccd.live_stop()
        self.ccd.set_trigger_mode('Internal')
        print('WORK DOWN')
        
