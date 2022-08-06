# -*- coding: utf-8 -*-
"""
Created on Mon Jul 11 16:57:09 2022

@author: iamiv
"""
import sys, time, threading, cv2
import numpy as np

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt 
from PyQt5.QtGui import QImage, QPixmap
#from PyQt5 import QtWidgets, QtCore
#from PyQt5.QtCore import QTimer, QPoint, pyqtSignal
#from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QLabel
#from PyQt5.QtWidgets import QWidget, QAction, QVBoxLayout, QHBoxLayout

from UI import Ui_MainWindow

class Camera(QtCore.QThread):  # 繼承 QtCore.QThread 來建立 Camera 類別
    rawdata = QtCore.pyqtSignal(np.ndarray)  # 建立傳遞信號，需設定傳遞型態為 np.ndarray

    def __init__(self, parent=None):
        """ 初始化
            - 執行 QtCore.QThread 的初始化
            - 建立 cv2 的 VideoCapture 物件
            - 設定屬性來確認狀態
              - self.connect：連接狀態
              - self.running：讀取狀態
        """
        # 將父類初始化
        super().__init__(parent)
        # 建立 cv2 的攝影機物件
        self.cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        # 判斷攝影機是否正常連接
        if self.cam is None or not self.cam.isOpened():
            self.connect = False
            self.running = False
        else:
            self.connect = True
            self.running = False

    def run(self):
        """ 執行多執行緒 - 讀取影像 - 發送影像 - 簡易異常處理 """
        # 當正常連接攝影機才能進入迴圈
        while self.running and self.connect:
            ret, img = self.cam.read()    # 讀取影像
            if ret:
                self.rawdata.emit(img)    # 發送影像
            else:    # 例外處理
                print("Warning!!!")
                self.connect = False

    def open(self):
        """ 開啟攝影機影像讀取功能 """
        if self.connect:
            self.running = True    # 啟動讀取狀態

    def stop(self):
        """ 暫停攝影機影像讀取功能 """
        if self.connect:
            self.running = False    # 關閉讀取狀態

    def close(self):
        """ 關閉攝影機功能 """
        if self.connect:
            self.running = False    # 關閉讀取狀態
            time.sleep(1)
            self.cam.release()      # 釋放攝影機

class SystemTime(QtCore.QThread):  # 繼承 QtCore.QThread 來建立 SystemTime 類別
    systime = QtCore.pyqtSignal(str)  # 建立傳遞信號，設定傳遞型態為 str
    def run(self):
        while 1 :
            gettime = QtCore.QDateTime.currentDateTime() # 抓取現在時間
            times = gettime.toString(Qt.DefaultLocaleLongDate) # 轉換成 str 型態
            self.systime.emit(times) # 發送時間資料
            time.sleep(0.3) # 暫停一小段時間 不然會卡死

class rollCall(QtCore.QThread):  # 繼承 QtCore.QThread 來建立 rollCall 類別
    
    stdname = QtCore.pyqtSignal(str)
    def run(self):
        while 1 :
            gettime = QtCore.QTime.currentTime() # 抓取現在時間
            getmin = gettime.minute() 
            getsec = gettime.second() 
            
            student_name = '姓名' + str(getsec)
            
            self.stdname.emit(student_name)
            
            if getsec == 0 :
                print(getmin,getsec)
                with open('test.csv', 'a', newline='') as f:
                    print('{},{}'.format(getmin,student_name),file=f) #儲存資料在csv內
                           
            time.sleep(1) # 暫停一小段時間 不然會卡死
                    
class MainWindow_controller(QtWidgets.QMainWindow):
    
    

    def __init__(self, parent=None):
        super().__init__() # in python3, super(Class, self).xxx = super().xxx
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setup_control()
        
        # 設定 Frame Rate 的參數
        self.frame_num = 0
        

        # 設定相機功能
        self.ProcessCam = Camera()  # 建立相機物件
        if self.ProcessCam.connect:
            # 連接影像訊號 (rawdata) 至 getRaw()
            self.ProcessCam.rawdata.connect(self.getRaw)  # 槽功能：取得並顯示影像
            # 攝影機啟動按鈕的狀態：ON
            self.ui.camBtn_open.setEnabled(True)
        else:
            # 攝影機啟動按鈕的狀態：OFF
            self.ui.camBtn_open.setEnabled(False)
        # 攝影機的其他功能狀態：OFF
        self.ui.camBtn_stop.setEnabled(False)
        
        # 連接按鍵
        self.ui.camBtn_open.clicked.connect(self.openCam)  # 槽功能：開啟攝影機
        self.ui.camBtn_stop.clicked.connect(self.stopCam)  # 槽功能：暫停讀取影像
        

        
    def getRaw(self, data):  # data 為接收到的影像
        """ 取得影像 """
        self.showData(data)  # 將影像傳入至 showData()

    def openCam(self):
        """ 啟動攝影機的影像讀取 """
        if self.ProcessCam.connect:  # 判斷攝影機是否可用
            self.ProcessCam.open()   # 影像讀取功能開啟
            self.ProcessCam.start()  # 在子緒啟動影像讀取
            # 按鈕的狀態：啟動 OFF、暫停 ON、視窗大小 ON
            self.ui.camBtn_open.setEnabled(False)
            self.ui.camBtn_stop.setEnabled(True)

    def stopCam(self):
        """ 凍結攝影機的影像 """
        if self.ProcessCam.connect:  # 判斷攝影機是否可用
            self.ProcessCam.stop()   # 影像讀取功能關閉
            # 按鈕的狀態：啟動 ON、暫停 OFF、視窗大小 OFF
            self.ui.camBtn_open.setEnabled(True)
            self.ui.camBtn_stop.setEnabled(False)

    def showData(self, img):
        """ 顯示攝影機的影像 """
        self.Ny, self.Nx, _ = img.shape  # 取得影像尺寸

        # 建立 Qimage 物件 (灰階格式)
        # qimg = QtGui.QImage(img[:,:,0].copy().data, self.Nx, self.Ny, QtGui.QImage.Format_Indexed8)

        # 建立 Qimage 物件 (RGB格式)
        qimg = QtGui.QImage(img.data, self.Nx, self.Ny, QtGui.QImage.Format_RGB888)

        # viewData 的顯示設定
        self.ui.label_pic.setScaledContents(True)  # 尺度可變
        ### 將 Qimage 物件設置到 viewData 上
        self.ui.label_pic.setPixmap(QtGui.QPixmap.fromImage(qimg))

        # Frame Rate 計算並顯示到狀態欄上
        if self.frame_num == 0:
            self.time_start = time.time()
        if self.frame_num >= 0:
            self.frame_num += 1
            self.t_total = time.time() - self.time_start
            if self.frame_num % 100 == 0:
                self.frame_rate = float(self.frame_num) / self.t_total

    def getTime(self, times):
        self.ui.label_time.setText(times) # 修改現在時間
 
    def getRollCall(self, student_name):
        self.ui.label_name.setText(student_name) # 修改名稱   
        
    def setup_control(self):
       # TODO        
        #self.ui.label_name.setText(self.student_name)
        self.ui.label_temp.setText('溫度')
        self.img_path = 'IMG_0485.png'
        self.display_img()
        
        # 取得現在時間
        self.SystemTime = SystemTime() 
        self.SystemTime.systime.connect(self.getTime) # 槽功能：取得時間資料
        self.SystemTime.start()
        
        # 點名系統
        self.rollCall = rollCall()
        self.rollCall.stdname.connect(self.getRollCall) # 槽功能：取得姓名資料
        self.rollCall.start()
        
    def display_img(self):
        self.img = cv2.imread(self.img_path)
        height, width, channel = self.img.shape
        bytesPerline = 3 * width
        self.qimg = QImage(self.img, width, height, bytesPerline, QImage.Format_RGB888).rgbSwapped()
        self.ui.label_pic.setPixmap(QPixmap.fromImage(self.qimg))
        
    def closeEvent(self, event):
        """ 視窗應用程式關閉事件 """
        if self.ProcessCam.running:
            self.ProcessCam.close()      # 關閉攝影機
            time.sleep(1)
            self.ProcessCam.terminate()  # 關閉子緒
        QtWidgets.QApplication.closeAllWindows()  # 關閉所有視窗