# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'window0709.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1200, 600)
        self.centralwidget_main = QtWidgets.QWidget(MainWindow)
        self.centralwidget_main.setObjectName("centralwidget_main")
        self.label_time = QtWidgets.QLabel(self.centralwidget_main)
        self.label_time.setGeometry(QtCore.QRect(650, 250, 500, 150))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(20)
        self.label_time.setFont(font)
        self.label_time.setObjectName("label_time")
        self.label_temp = QtWidgets.QLabel(self.centralwidget_main)
        self.label_temp.setGeometry(QtCore.QRect(650, 400, 500, 150))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(20)
        self.label_temp.setFont(font)
        self.label_temp.setObjectName("label_temp")
        self.label_pic = QtWidgets.QLabel(self.centralwidget_main)
        self.label_pic.setGeometry(QtCore.QRect(0, 30, 640, 480))
        self.label_pic.setObjectName("label_pic")
        self.label_name = QtWidgets.QLabel(self.centralwidget_main)
        self.label_name.setGeometry(QtCore.QRect(650, 0, 500, 250))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(20)
        self.label_name.setFont(font)
        self.label_name.setObjectName("label_name")
        self.camBtn_open = QtWidgets.QPushButton(self.centralwidget_main)
        self.camBtn_open.setGeometry(QtCore.QRect(30, 570, 75, 23))
        self.camBtn_open.setObjectName("camBtn_open")
        self.camBtn_stop = QtWidgets.QPushButton(self.centralwidget_main)
        self.camBtn_stop.setGeometry(QtCore.QRect(140, 570, 75, 23))
        self.camBtn_stop.setObjectName("camBtn_stop")
        MainWindow.setCentralWidget(self.centralwidget_main)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.label_time.setText(_translate("MainWindow", "TextLabel_time"))
        self.label_temp.setText(_translate("MainWindow", "TextLabel_temp"))
        self.label_pic.setText(_translate("MainWindow", "TextLabel_picture"))
        self.label_name.setText(_translate("MainWindow", "TextLabel_name"))
        self.camBtn_open.setText(_translate("MainWindow", "Open"))
        self.camBtn_stop.setText(_translate("MainWindow", "Stop"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

