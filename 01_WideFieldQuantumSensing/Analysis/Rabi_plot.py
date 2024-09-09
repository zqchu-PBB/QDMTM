from PIL import Image
import numpy as np
import matplotlib.pyplot as plt # plt 用于显示图片
from skimage import io 
from scipy.optimize import curve_fit
import numpy
import math
from Rabi_Fitting import Rabi_fitting

# Below is the part needed to be revised.
loadpath = 'G:\\1-Experimental Data\\72-Laser polarization time(20210113)\\2-Rabi'
#-------------------------------------------------------------------------
ROI = Image.open(loadpath+'\\processed\\ROI.tif')
ROI = numpy.array(ROI)/65535
f = open(loadpath+'\\processed\\Rabi_Information.txt','r')
Info = f.readlines()
for item in Info:
    item1 = item.replace('\n','')
    parameter = item1.split(':')
    if parameter[0] == 'MW_power':
        MW_power = parameter[1]
        print(MW_power)
        power = MW_power  
    if parameter[0] == 'MW_duration_sweeping':
        delay_time_range = eval(parameter[1])
    if parameter[0] == 'loops':
        loops = int(parameter[1])
        print(loops) 
def ROI_(frame, ROI):
    ROI_frame = frame * ROI
    ROI_frame_NoZero = ROI_frame.ravel()[numpy.flatnonzero(ROI_frame)]
    return ROI_frame_NoZero

loops = 5
# Above is the part needed to be revised.
Final_Y_MW = []
Final_Y_WithoutMW = []
Final_Y_Normalized = []
for loop in range(1,loops):
    Data_X = []
    Data_Y_MW = []
    Data_Y_WithoutMW = []
    Data_Y_Normalized = []
    for tau in delay_time_range:
        imagepath_MW = loadpath + '\\Rabi_Images\\loop' + str(loop) + '_MW'+str(tau) + '.tif'
        imagepath_WithoutMW = loadpath + '\\Rabi_Images\\loop' + str(loop) + '_None'+str(tau) + '.tif'
        image_MW = Image.open(imagepath_MW)
        image_WithoutMW = Image.open(imagepath_WithoutMW)
        image_MW = np.array(image_MW)
        image_WithoutMW = np.array(image_WithoutMW)
        image_ROI_MW = ROI_(image_MW, ROI)
        image_ROI_WithoutMW = ROI_(image_WithoutMW, ROI)
        median_MW = np.median(image_ROI_MW)
        median_WithoutMW = np.median(image_ROI_WithoutMW)
        Data_Y_Normalized.append(round(median_MW.astype(numpy.float64)/median_WithoutMW.astype(numpy.float64),6))
        #print(type(median_MW))
        #print(round(median_MW.astype(numpy.float64)/median_WithoutMW.astype(numpy.float64),6))
        Data_Y_MW.append(median_MW)
        Data_Y_WithoutMW.append(median_WithoutMW)
        Data_X.append(tau)
    Final_Y_MW.append(Data_Y_MW)
    Final_Y_WithoutMW.append(Data_Y_WithoutMW)
    Final_Y_Normalized.append(Data_Y_Normalized)
    print(loop)
#Final_Y_MW = numpy.array(Final_Y_MW).astype(numpy.float64)
#Final_Y_WithoutMW = numpy.array(Final_Y_WithoutMW).astype(numpy.float64)
#Final_Y_Normalized = Final_Y_MW/Final_Y_WithoutMW
Final_Y_MW_mean = numpy.round(numpy.mean(Final_Y_MW, axis = 0), 2)
Final_Y_WithoutMW_mean = numpy.round(numpy.mean(Final_Y_WithoutMW, axis = 0), 2)
Final_Y_Normalized_mean = numpy.round(numpy.mean(Final_Y_Normalized, axis = 0), 6)
Final_Y_MW_std = numpy.round(numpy.std(Final_Y_MW, axis = 0, ddof =1), 2)
Final_Y_WithoutMW_std = numpy.round(numpy.std(Final_Y_WithoutMW, axis = 0, ddof =1), 2)
Final_Y_Normalized_std = numpy.round(numpy.std(Final_Y_Normalized, axis = 0, ddof =1), 6)
Final_Y_MW_error = Final_Y_MW_std/numpy.sqrt(75)
Final_Y_WithoutMW_error = Final_Y_WithoutMW_std/numpy.sqrt(75)
Final_Y_Normalized_error = Final_Y_Normalized_std/numpy.sqrt(75)
print('Final_Y_Normalized_error')
print(Final_Y_Normalized_error[0:10])
'''
Final_Y_MW_error = Final_Y_MW_std/numpy.sqrt(int(loops)-1)
Final_Y_WithoutMW_error = Final_Y_WithoutMW_std/numpy.sqrt(int(loops)-1)
Final_Y_Normalized_error = Final_Y_Normalized_std/numpy.sqrt(int(loops)-1)
'''
plt.errorbar(Data_X, numpy.array(Final_Y_MW_mean), fmt = "b.", yerr = Final_Y_MW_error, label = 'MW')
plt.errorbar(Data_X, numpy.array(Final_Y_WithoutMW_mean), fmt = "r.", yerr = Final_Y_WithoutMW_error, label = 'WithoutMW')
plt.xlabel("Time (ns)")
plt.ylabel("Intensity (a.u.)")
plt.legend(loc = "lower left")
plt.legend(frameon=False) 
plt.savefig(loadpath+'\\Processed\\Rabi.tif',dpi=240)#保存图片
plt.close()

plt.errorbar(Data_X, numpy.array(Final_Y_Normalized_mean), fmt = "b.", yerr = Final_Y_Normalized_error)
plt.gcf().subplots_adjust(left=0.55,bottom=0.15)
plt.xlabel("Time (ns)")
plt.ylabel("Normalized Intensity (a.u.)")

plt.savefig(loadpath+'\\Processed\\Rabi_normalized.tif',dpi=240)#保存图片
plt.close()

Final_Y_Normalized_mean = Final_Y_Normalized_mean.tolist()
Rabi_fitting.fitting(Data_X, numpy.array(Final_Y_Normalized_mean), Final_Y_Normalized_error, loadpath, power)

