# -*- coding: utf-8 -*-
"""
Created on Mon Jul 11 19:24:05 2022

@author: iamiv
"""

from PyQt5 import QtWidgets

from controller import MainWindow_controller

if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow_controller()
    window.setWindowTitle("影像辨識點名系統")
    window.show()
    sys.exit(app.exec_())
