from matplotlib import pyplot as plt
'''
1. NOL: the number of the line need to be ploted
2. X: X data
3. Y: Y data
4. line_shape: r, b, r. ,.
5. X_Label
6. Y_Label
7. Legends
8. Legends_loc: the location of the legends
'''

class plot_line():
    def __init__(self):
        pass

    @staticmethod
    def draw(Data = [], line_shape = [], X_Label = [], Y_Label = [], Legends = [], Legends_loc = []):
        
        for data in Data[0:-2]:
            plt.plot(data[0], data[1], data[2], label=data[3])
            
        X_Label = Data[-2]
        Y_Label = Data[-1]
        plt.xlabel(X_Label)
        plt.ylabel(Y_Label)
        
        if Legends_loc == '':
            plt.legend(loc = 'lower right')
        else:
            plt.legend(loc = Legends_loc)
        plt.legend(frameon=False) 
        plt.show()