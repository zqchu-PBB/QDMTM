from PIL import Image
import numpy as np
import matplotlib.pyplot as plt # plt 用于显示图片
from skimage import io 
from scipy.optimize import curve_fit
import numpy
import math
from Lorentzian_Fitting import Lorentzian
loadpath = 'E:\\OneDrive - connect.hku.hk\\1-Experimental Data\\34-ODMR_Versus_MW\\7'
save_path = 'E:\\OneDrive - connect.hku.hk\\1-Experimental Data\\34-ODMR_Versus_MW\\7'
power = 3
Counts = 0
Final_Y = []
for loop in range(1,11):
    ODMR_X = []
    ODMR_Y = []
    for freq in range(2790000000, 2950000000, 1000000):
        imagepath = loadpath + '\\loop' + str(loop) + '_freq'+str(freq/1000000000) + 'GHz_power' + '3dBm.tif'
        image = Image.open(imagepath)
        image1 = np.array(image)
        median_value = np.median(image1)
        ODMR_Y.append(median_value)
        ODMR_X.append(freq)
    Final_Y.append(ODMR_Y)

    print(loop)
Final_Y_mean = numpy.round(numpy.mean(Final_Y, axis = 0), 2)
Final_Y_std = numpy.round(numpy.std(Final_Y, axis = 0, ddof =1), 2)
Final_Y_error = Final_Y_std/numpy.sqrt(len(Final_Y))
x_data = numpy.array(ODMR_X)
y_data = Final_Y_mean.tolist()
Fitting, Contrast = Lorentzian.Lorentzian_fitting(x_data, y_data, Final_Y_error, 1, False, save_path, power)

