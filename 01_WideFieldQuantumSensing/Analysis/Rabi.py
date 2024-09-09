from PIL import Image
import numpy as np
import matplotlib.pyplot as plt # plt 用于显示图片
from skimage import io 
from scipy.optimize import curve_fit
import numpy
import math
loadpath = 'E:\\OneDrive - connect.hku.hk\\1-Experimental Data\\29-ND_ODMR(20201021)\\11-LED_excitation'
Counts = 0
i =0
for loop in range(1,5):
    ODMR_X = []
    ODMR_Y = []
    i = i+1
    for freq in range(2790, 2950, 2):
        imagepath = loadpath + '\\loop' + str(loop) + '_freq'+str(freq/1000) + 'GHz_power' + '0dBm.tif'
        image = Image.open(imagepath)
        image1 = np.array(image)
        mean_value = np.mean(image1)
        ODMR_Y.append(mean_value)
        ODMR_X.append(freq/1000)
        ''' 
        #Show the image 
        plt.figure("dog")
        plt.imshow(image1,'gray')
        plt.show()
        '''
    Counts = Counts + np.array(ODMR_Y)
    print(loop)
Counts_mean = Counts/i