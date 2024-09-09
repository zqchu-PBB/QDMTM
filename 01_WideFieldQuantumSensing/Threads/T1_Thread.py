from PyQt5 import QtCore
import numpy
from PIL import Image
import os
import pandas as pd

class T1_thread(QtCore.QThread):
    Signal_pulsed = QtCore.pyqtSignal(numpy.ndarray,name='T1')

    def __init__(self, Info = [], loops = 1, save_path = [], ROI = [], Init = []):
        super().__init__()
        self.MW_power = Info[0]
        self.MW_freq = Info[1]
        self.aom_duration = Info[2]
        self.MW_duration = Info[3]
        self.gap_1 = Info[4]
        self.gap_2 = Info[5]
        self.delay_duration_sweeping = Info[6]
        self.repetitions = Info[7]
        self.aom_power = Info[8]
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

        self.pb.high([])
        self.running = True

        Check_Existing = os.path.exists(self.save_path+'\\T1_Images')
        if Check_Existing:
            pass
        else:
            os.mkdir(self.save_path+'\\T1_Images')
        f = open(self.save_path+'\\Processed\\T1_Information.txt','w')
        f.write('MW_power:'+str(self.MW_power)+'dBm')
        f.write("\n")
        f.write('MW_freq:'+str(self.MW_freq)+'Hz')
        f.write("\n")
        f.write('aom_duration:'+str(self.aom_duration)+'ns')
        f.write("\n")
        f.write('MW_duration:'+str(self.MW_duration)+'ns')
        f.write("\n")
        f.write('gap_1:'+str(self.gap_1)+'ns')
        f.write("\n")
        f.write('gap_2:'+str(self.gap_2)+'ns')
        f.write("\n")
        f.write('delay_duration_sweeping:')
        for item in self.delay_duration_sweeping:
            f.write(str(item)+' ')
        f.write("\n")
        f.write('repetitions:'+str(self.repetitions))
        f.write("\n")
        f.write('loops:'+str(self.loops))
        f.write("\n")
        f.write('aom power:'+str(self.aom_power)+'V')
        f.write("\n")
        f.close()
        Image.fromarray(self.ROI*65535).save(self.save_path+'\\Processed\\ROI.tif')
        dataFrame = pd.DataFrame(self.ROI*65535) # data must cannot exceed two one dimensions, two dimensions are acceptable
        # with pd.ExcelWriter(self.save_path+'\\Processed\\ROI.xlsx') as writer: # 一个excel写入多页数据
        #     dataFrame.to_excel(writer, sheet_name='page1', float_format='%.6f')


    def run(self):
        self.smiq.SetPower(str(self.MW_power))
        self.smiq.SetFrequence(str(self.MW_freq))
        self.smiq.on()
        self.ccd.live_start()
        try:
            for loop in range(0, self.loops):
                for t in self.delay_duration_sweeping: # t is the delay time
                    for i in range(2):
                        self.msleep(200)
                        self.pause = True
                        if i == 0: # from the ms = 0 state, without MW
                            laser_seq = [(self.aom_duration, 1),(self.gap_1 + self.MW_duration + self.gap_2 + t, 0)]
                            MW_seq = [(self.aom_duration + self.gap_1 + self.MW_duration + self.gap_2 + t, 0)]
                            # print('without mw')
                        else:
                            laser_seq = [(self.aom_duration, 1),(self.gap_1 + self.MW_duration + self.gap_2 + t, 0)]
                            MW_seq = [(self.aom_duration + self.gap_1, 0),(self.MW_duration, 1), (self.gap_2 + t, 0)]
                            # print('with mw')
                        self.sequences = [[0, laser_seq], [1, MW_seq]]
                        self.pb.Sequence(self.sequences, self.repetitions)
                        
                        self.pb.run()

                        frame = self.ccd.live_readout()  
                        if not self.running or numpy.max(frame) == 65535:
                            raise BaseException

                        
                        if i == 0:
                            Point_Data = [t, frame, 0, loop]
                            self.T1.emit(Point_Data) 
                            if t>0:
                                Image.fromarray(frame).save(self.save_path+'\\T1_Images\\loop'+str(loop)+'_None'+str(t)+'.tif')
                            self.msleep(30)
                        else:
                            Point_Data = [t, frame, 1, loop]
                            self.T1.emit(Point_Data)
                            if t>0: 
                                Image.fromarray(frame).save(self.save_path+'\\T1_Images\\loop'+str(loop)+'_MW'+str(t)+'.tif')
                            self.msleep(30)
                        while self.pause == True:
                            print('')
                        
        except:
            pass
        self.running = True
        self.smiq.off()
        f = open(self.save_path+'\\Processed\\T1_Information.txt','a')
        f.write('Measurement loops:'+str(loop))
        f.write("\n")
        f.close()
        self.ccd.live_stop()
        self.ccd.set_trigger_mode('Internal')
        print('WORK DOWN')
        
