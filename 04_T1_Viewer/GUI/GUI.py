# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'E:\01-RawData\Y2021_ExperimentData_Cell\138-20210602(ZSX_Gd+fixed_cell_with_ph7.4_PBS)\4-t1\NP_T1_Viewer_V3_20240731\GUI\GUI.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1079, 628)
        MainWindow.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.mplwidget = QtWidgets.QWidget(self.centralwidget)
        self.mplwidget.setGeometry(QtCore.QRect(10, 10, 491, 491))
        self.mplwidget.setCursor(QtGui.QCursor(QtCore.Qt.CrossCursor))
        self.mplwidget.setMouseTracking(True)
        self.mplwidget.setObjectName("mplwidget")
        self.tbwidget = QtWidgets.QWidget(self.centralwidget)
        self.tbwidget.setGeometry(QtCore.QRect(10, 510, 491, 51))
        self.tbwidget.setObjectName("tbwidget")
        self.widget_row = QtWidgets.QWidget(self.centralwidget)
        self.widget_row.setGeometry(QtCore.QRect(510, 10, 541, 261))
        self.widget_row.setObjectName("widget_row")
        self.pushButton_open = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_open.setGeometry(QtCore.QRect(970, 445, 75, 41))
        self.pushButton_open.setObjectName("pushButton_open")
        self.tbwidget_row = QtWidgets.QWidget(self.centralwidget)
        self.tbwidget_row.setGeometry(QtCore.QRect(510, 270, 541, 51))
        self.tbwidget_row.setObjectName("tbwidget_row")
        self.tbwidget_row_2 = QtWidgets.QWidget(self.tbwidget_row)
        self.tbwidget_row_2.setGeometry(QtCore.QRect(0, -50, 501, 51))
        self.tbwidget_row_2.setObjectName("tbwidget_row_2")
        self.pushButton_select_pixel = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_select_pixel.setGeometry(QtCore.QRect(510, 510, 121, 51))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.pushButton_select_pixel.setFont(font)
        self.pushButton_select_pixel.setObjectName("pushButton_select_pixel")
        self.pushButton_fit = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_fit.setGeometry(QtCore.QRect(640, 510, 121, 51))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.pushButton_fit.setFont(font)
        self.pushButton_fit.setObjectName("pushButton_fit")
        self.listWidget_fitting_results = QtWidgets.QListWidget(self.centralwidget)
        self.listWidget_fitting_results.setGeometry(QtCore.QRect(770, 510, 281, 51))
        self.listWidget_fitting_results.setObjectName("listWidget_fitting_results")
        self.checkBox_set_x_to_log = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBox_set_x_to_log.setGeometry(QtCore.QRect(510, 450, 161, 31))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(16)
        self.checkBox_set_x_to_log.setFont(font)
        self.checkBox_set_x_to_log.setObjectName("checkBox_set_x_to_log")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1079, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Matplotlib Canvas"))
        self.pushButton_open.setText(_translate("MainWindow", "Open"))
        self.pushButton_select_pixel.setText(_translate("MainWindow", "Select Pixel"))
        self.pushButton_fit.setText(_translate("MainWindow", "Fit"))
        self.checkBox_set_x_to_log.setText(_translate("MainWindow", "logarithmic axis"))

