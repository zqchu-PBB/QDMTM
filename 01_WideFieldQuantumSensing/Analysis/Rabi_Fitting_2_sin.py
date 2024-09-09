import numpy as np
import matplotlib.pyplot as plt # plt 用于显示图片
from scipy.optimize import curve_fit
import numpy
import math

class Rabi_fitting():
    def __init__(self): #NOP means number of peaks
        self.x = []
        self.y = []
        self.nop = []
        self.x_fit = []
        self.y_fit = []
        self.Normalization = []
        self.save_path = []

    @staticmethod
    def fitting(X = [], Y = [], yerr = [], save_path = [], power = []): # Variable X is a list and Y is a numpy.array.
        x_fit = []
        y_fit = []

        def func(x,magnitude,omega,t2_star,constant):
            return magnitude1*np.cos(2*math.pi*omega1*x)*np.exp(-(x/t2_star1)**2)+magnitude2*np.cos(2*math.pi*omega2*x)*np.exp(-(x/t2_star2)**2)+constant
        x_data = numpy.array(X)
        y_data = numpy.array(Y)
        mean_value = numpy.mean(y_data)
        max_value = max(y_data)
        min_value = min(y_data)
        min_index, = numpy.where(y_data == min_value)[0]
        magnitude = max_value - min_value
        x_min = x_data[min_index]
        omega = 1/(2*x_min)
        t2_star = 1000
        constant = y_data[-1]

        init_vals = [magnitude, omega, t2_star,magnitude, omega, t2_star, constant]
        print(init_vals)

        popt, pcov = curve_fit(func, x_data, y_data, p0 = numpy.array(init_vals), sigma = yerr)
        print('FITTING')

        magnitude1 = popt[0] # popt里面是拟合系数，读者可以自己help其用法  
        omega1 = popt[1]
        t2_star1 = popt[2]
        magnitude2 = popt[0] # popt里面是拟合系数，读者可以自己help其用法  
        omega2 = popt[1]
        t2_star2 = popt[2]
        constant = popt[3]
        x_fit = numpy.array(range(x_data[0], x_data[-1], 1))
        y_fit = func(x_fit, magnitude, omega, t2_star, constant)
        Contrast = round((max(y_fit)-min(y_fit))/max(y_fit)*100, 2)

        f = open(save_path+'\\Processed\\Rabi_fitting_power_'+str(power)+'dBm_2sin.txt','w')
        #f.write('Amplitude 1:           '+str(popt[0])+'  Counts')
        #f.write("\n")
        f.write('Contrast:                   '+str(Contrast)+'%')
        f.write("\n")
        f.write('Omega:        '+str(round(omega,6)*1000000000)+'  Hz')
        f.write("\n")
        f.write('T2_star:        '+str(round(t2_star,3))+'  ns')
        f.write("\n")
        f.close()

        ''' 画以秒为单位的counts图
        plt.plot(ODMR_X, np.array(Counts_mean) * 1000/15, '.', label='data')
        plt.plot(x_fit, yvals* 1000/15, 'r', label='fitting')
        '''

        plt.errorbar(x_data, numpy.array(Y), fmt = "b.", yerr = yerr, label = 'data')
        plt.plot(x_fit, y_fit, 'r', label='fitting')

        plt.xlabel("Time (ns)")
        plt.ylabel("Intensity (a.u.)")
        plt.legend(loc = "lower left")
        plt.legend(frameon=False) 
        
        print('9999999999999999999999')
        print(save_path)
        print(type(save_path))
        print(power)
        print(type(power))
        plt.savefig(save_path+'\\Processed\\Rabi_fitting_mean_power_'+str(power)+'dBm_2sin.tif',dpi=240)
        plt.close()

        return omega, t2_star, Contrast
