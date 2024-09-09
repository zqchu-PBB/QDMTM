import numpy as np
import matplotlib.pyplot as plt # plt 用于显示图片
from scipy.optimize import curve_fit
import numpy
import math

class Lorentzian_multipeak():
    def __init__(self): #NOP means number of peaks
        self.x = []
        self.y = []
        self.nop = []
        self.x_fit = []
        self.y_fit = []
        self.Normalization = []
        self.save_path = []

    @staticmethod
    def Lorentzian_fitting(X = [], Y = [], yerr = [], NOP = [], Normalization = [], save_path = [], power = []):
        x_fit = []
        y_fit = []

        if NOP == 1:
            def func(x,a1,b1,c1,constant):
                return a1/math.pi*b1/(pow((x-c1),2)+pow(b1,2)) + constant
            x_data = X/1000000000
            y_data = Y
            print('1111111111111111111111111111111111111111111111111111111111111111111111111111111111')
            print(type(y_data))
            print(y_data)
            max_value = max(y_data)
            min_value = min(y_data)
            min_index = y_data.index(min(y_data))
            magnitude = max_value - min_value   

            x_data_array = numpy.array(x_data)
            y_data_array = numpy.array(y_data)
            
            #print(x_data[min_index])
            init_vals = [-magnitude, 0.005, x_data[min_index],max_value]
            popt, pcov = curve_fit(func, numpy.array(x_data), numpy.array(y_data), p0 = init_vals)
            print('FITTING')
            print(init_vals)
            print(x_data)
            print(y_data)
            a1=popt[0] # popt里面是拟合系数，读者可以自己help其用法  
            b1=popt[1]
            c1=popt[2]
            constant=popt[3]
            x_fit = numpy.array(range(27900,29481,1))/10000
            y_fit = func(x_fit,a1,b1,c1,constant)
            Contrast = round((max(y_fit)-min(y_fit))/max(y_fit)*100, 2)

            f = open(save_path+'\\Processed\\ODMR_information_power_'+str(power)+'dBm.txt','w')
            #f.write('Amplitude 1:           '+str(popt[0])+'  Counts')
            #f.write("\n")
            f.write('Contrast:                   '+str(Contrast)+'%')
            f.write("\n")
            f.write('FWHM 1:                     '+str(round(popt[1],4)*1000)+'  MHz')
            f.write("\n")
            f.write('Center wavelength 1:        '+str(round(popt[2],3))+'  GHz')
            f.write("\n")
            f.close()


        elif NOP == 4:
            x_fit = []
            y_fit = []

        
            def func(x,a1,b1,c1,a2,b2,c2,a3,b3,c3,a4,b4,c4,constant):
                return a1/math.pi*b1/(pow((x-c1),2)+pow(b1,2)) + a2/math.pi*b2/(pow((x-c2),2)+pow(b2,2)) + a3/math.pi*b3/(pow((x-c3),2)+pow(b3,2)) + a4/math.pi*b4/(pow((x-c4),2)+pow(b4,2)) + constant
            x_data = X/1000000000
            y_data = Y
            print('1111111111111111111111111111111111111111111111111111111111111111111111111111111111')
            print(type(y_data))
            print(y_data)
            max_value = max(y_data)
            min_value = min(y_data)
            min_index = y_data.index(min(y_data))
            magnitude = max_value - min_value   

            x_data_array = numpy.array(x_data)
            y_data_array = numpy.array(y_data)
            
            #print(x_data[min_index])
            #init_vals = [-magnitude, 0.005, x_data[min_index],max_value]
            init_vals = [-1000, 0.002, 2.44,-1000, 0.002,2.81, -1000, 0.002, 3.1, -1500, 0.001, 3.3 , 24500]
            popt, pcov = curve_fit(func, numpy.array(x_data), numpy.array(y_data), p0 = init_vals)
            print('FITTING')
            print(init_vals)
            print(x_data)
            print(y_data)
            a1=popt[0] # popt里面是拟合系数，读者可以自己help其用法  
            b1=popt[1]
            c1=popt[2]
            a2=popt[3] # popt里面是拟合系数，读者可以自己help其用法  
            b2=popt[4]
            c2=popt[5]
            a3=popt[6] # popt里面是拟合系数，读者可以自己help其用法  
            b3=popt[7]
            c3=popt[8]
            a4=popt[9] # popt里面是拟合系数，读者可以自己help其用法  
            b4=popt[10]
            c4=popt[11]
            constant=popt[12]
            x_fit = numpy.array(range(23000, 35000, 1))/10000
            y_fit = func(x_fit,a1,b1,c1,a2,b2,c2,a3,b3,c3,a4,b4,c4,constant)
            Contrast = round((max(y_fit)-min(y_fit))/max(y_fit)*100, 2)

            f = open(save_path+'\\ODMR_information_power_'+str(power)+'dBm.txt','w')
            #f.write('Amplitude 1:           '+str(popt[0])+'  Counts')
            #f.write("\n")
            f.write('Contrast:                   '+str(Contrast)+'%')
            f.write("\n")
            f.write('FWHM 1:                     '+str(round(popt[1],4)*1000)+'  MHz')
            f.write("\n")
            f.write('Center wavelength 1:        '+str(round(popt[2],3))+'  GHz')
            f.write("\n")
            f.close()



        elif NOP ==2:

            def func(x,a1,b1,c1,a2,b2,c2,constant):
                return a1/math.pi*b1/(pow((x-c1),2)+pow(b1,2)) + a2/math.pi*b2/(pow((x-c2),2)+pow(b2,2)) + constant

            init_vals = [1000000,0.001,2.860,1000000,0.001,2.88,0]
            popt, pcov = curve_fit(func, numpy.array(ODMR_X), np.array(Counts_mean), p0 = init_vals)
            a1=popt[0] # popt里面是拟合系数，读者可以自己help其用法  
            b1=popt[1]
            c1=popt[2]
            a2=popt[3] # popt里面是拟合系数，读者可以自己help其用法    
            b2=popt[4]
            c2=popt[5]
            constant=popt[6]
            x_fit = np.array(range(27900,29481,1))/10000
            yvals=func(x_fit,a1,b1,c1,a2,b2,c2,constant)

            f = open(save_path+'\\Processed\\ODMR_information_power_'+str(power)+'dBm.txt','w')
            #f.write('Amplitude 1:           '+str(popt[0])+'  Counts')
            #f.write("\n")
            f.write('FWHM 1:                     '+str(round(popt[1],4)*1000)+'  MHz')
            f.write("\n")
            f.write('Center wavelength 1:   '+str(round(popt[2],3))+'  GHz')
            f.write("\n")
            f.close()


        ''' 画以秒为单位的counts图
        plt.plot(ODMR_X, np.array(Counts_mean) * 1000/15, '.', label='data')
        plt.plot(x_fit, yvals* 1000/15, 'r', label='fitting')
        '''
        # Plot the figure of normalized intensity
        if Normalization == True:
            plt.errorbar(x_data, np.array(Y)/max(y_fit), fmt = "b.", yerr = yerr/max(y_fit), label = 'data')
            plt.plot(x_fit, y_fit/max(y_fit), 'r', label='fitting')
            plt.xlabel("Frequency (GHz)")
            plt.ylabel("Normalized Intensity (a.u.)")
            plt.legend(loc = 'lower right')
            plt.legend(frameon=False) 

        elif Normalization == False:
            #plt.plot(x_data, numpy.array(Y), '.', label='data')
            plt.errorbar(x_data, numpy.array(Y), fmt = "b.", yerr = yerr, label = 'data')
            plt.plot(x_fit, y_fit, 'r', label='fitting')

            plt.xlabel("Frequency (GHz)")
            plt.ylabel("Intensity (a.u.)")
            plt.legend(loc = "lower left")
            plt.legend(frameon=False) 
        
        print('9999999999999999999999')
        print(save_path)
        print(type(save_path))
        print(power)
        print(type(power))
        plt.savefig(save_path+'\\ODMR_mean_power_'+str(power)+'dBm.tif',dpi=240)
        plt.close()


        return popt, Contrast
