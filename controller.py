# -*- coding: utf-8 -*-
"""
Created on Mon Jul 11 16:57:09 2022

@author: iamiv
"""
import sys, time, threading, cv2
import numpy as np
import adafruit_dht
from board import *
import csv
#from string import replace

from tflite_runtime.interpreter import Interpreter

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt 
from PyQt5.QtGui import QImage, QPixmap ,QFont
#from PyQt5 import QtWidgets, QtCore
#from PyQt5.QtCore import QTimer, QPoint, pyqtSignal
#from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QLabel
#from PyQt5.QtWidgets import QWidget, QAction, QVBoxLayout, QHBoxLayout

from UI import Ui_MainWindow

data_folder = "ssd_mobilenet/"
EfficientDetLite = 'ef1' #修改EfficientDetLite的版本

model_path = data_folder + "model_" + EfficientDetLite + ".tflite"
label_path = data_folder + "labelmap.txt"
min_conf_threshold = 0.5

GPIO_PIN= D4 # 定義DHT資料輸入的gpio接腳
dht_device = adafruit_dht.DHT11(GPIO_PIN, use_pulseio = False)

with open(label_path, "r") as f:
    labels=[line.strip() for line in f.readlines()]
    
interpreter = Interpreter(model_path=model_path)
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()
_,height, width, _ = interpreter.get_input_details()[0]["shape"]


class Camera(QtCore.QThread):  # 繼承 QtCore.QThread 來建立 Camera 類別
    rawdata = QtCore.pyqtSignal(np.ndarray)  # 建立傳遞信號，需設定傳遞型態為 np.ndarray
    getstdname = QtCore.pyqtSignal(str)
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
        self.cam = cv2.VideoCapture(0)
        self.fps = 0 
        # 判斷攝影機是否正常連接
        if self.cam is None or not self.cam.isOpened():
            self.connect = False
            self.running = False
        else:
            self.connect = True
            self.running = False

    def run(self):
        """ 執行多執行緒 - 讀取影像 - 發送影像 - 簡易異常處理 """
        imHeight=480
        imWidth=640
        # 當正常連接攝影機才能進入迴圈
        while self.running and self.connect:
            ret, img = self.cam.read()    # 讀取影像
            frame_rgb=cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
            frame_resized=cv2.resize(frame_rgb,(width,height))
            input_data = np.expand_dims(frame_resized,axis=0)
            
            interpreter.set_tensor(input_details[0]["index"],input_data)
            interpreter.invoke()

            boxes=interpreter.get_tensor(output_details[1]["index"])[0]
            classes=interpreter.get_tensor(output_details[3]["index"])[0]
            scores=interpreter.get_tensor(output_details[0]["index"])[0]
            
            for i in range(len(scores)):
                if ((scores[i] > min_conf_threshold) and (scores[i] <= 1.0)):
                    min_y = int(max(1, (boxes[i][0] * imHeight)))
                    min_x = int(max(1, (boxes[i][1] * imWidth)))
                    max_y = int(min(imHeight, (boxes[i][2] * imHeight)))
                    max_x = int(min(imWidth, (boxes[i][3] * imWidth)))
                    cv2.rectangle(img, (min_x, min_y), (max_x ,max_y), (10, 255, 0), 2)
                    object_name = labels[int(classes[i])]
                    label = "%s: %d%%" %(object_name, int(scores[i] * 100))                    
                    labelSize, baseLine = cv2.getTextSize(label,
                                                       cv2.FONT_HERSHEY_SIMPLEX, 0.7,2)
                    label_min_y = max(min_x ,labelSize[1] + 10)
                    cv2.rectangle(img, (min_x , min_y- labelSize[1] - 10),
                                  (min_x + labelSize[0], min_y + baseLine - 10),
                                  (255, 255, 255), cv2.FILLED)
                    cv2.putText(img, label, (min_x, min_y - 7),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
                    
                    if self.fps == 1:
                        self.getstdname.emit(object_name) # control speed
                        
            if ret:
                self.rawdata.emit(img)    # 發送影像
            else:    # 例外處理
                print("Warning!!!")
                self.connect = False
                
            self.fps = self.fps + 1
            if self.fps == 3:
                self.fps = 0

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
    """ 顯示系統時間 """
    systime = QtCore.pyqtSignal(str)  # 建立傳遞信號，設定傳遞型態為 str
    def run(self):
        while MainWindow_controller.stop_flag == True :
            gettime = QtCore.QDateTime.currentDateTime() # 抓取現在時間
            times = gettime.toString(Qt.DefaultLocaleLongDate) # 轉換成 str 型態
            characters = "[CST]" #刪除後面多餘的[CST]
            for x in range(len(characters)):
                times= times.replace(characters[x],"")
            split_times = times.split()    
            split_times.insert(2,"\n")
            times=' '.join(split_times)
            self.systime.emit(times) # 發送時間資料
            time.sleep(0.3) # 暫停一小段時間 不然會卡死        
        
class rollCall(QtCore.QThread):  # 繼承 QtCore.QThread 來建立 rollCall 類別
    """ 修改姓名欄位，並新增時間跟姓名到CSV檔案 """
    stdname = QtCore.pyqtSignal(str)
    
    def __init__(self, object_name):
        super().__init__()
        self.name = object_name # 修改名稱
        self.current = True
        
    def run(self):        
        while self.current == True :
            gettime = QtCore.QDateTime.currentDateTime() # 抓取現在時間
            times = gettime.toString(Qt.DefaultLocaleLongDate) # 轉換成 str 型態
            characters = "[CST]" #刪除後面多餘的[CST]
            for x in range(len(characters)):
                times= times.replace(characters[x],"")
                
            if MainWindow_controller.deplicate_name != self.name :
                MainWindow_controller.deplicate_name = self.name
                
                student_name = '姓名：' + str(MainWindow_controller.student_name_list[self.name])            
                self.stdname.emit(student_name)
            
                if self.current == True:
                    with open('student_record.csv', 'a', newline='') as f: # 儲存資料在csv內
                        print('{},{}'.format(times, MainWindow_controller.student_name_list[self.name]),file=f)
                        self.current = False
                time.sleep(10)
                
                student_name = '姓名'
                self.stdname.emit(student_name)
                
                #MainWindow_controller.deplicate_name = ''
                          
            time.sleep(2) # 暫停一小段時間 不然會卡死                    

class GetTemperature(QtCore.QThread):  # 繼承 QtCore.QThread 來建立 GetTemperature 類別
    """ 取得溫溼度資訊，並修改溫溼度的欄位 """
    temperature = QtCore.pyqtSignal(int)  # 建立傳遞信號，設定傳遞型態為 int
    humidity = QtCore.pyqtSignal(int)
    gettemp=-1 # 先宣告一個值，以免未取得值就需要把它印出
    gethumi=-1
    def run(self):
        while MainWindow_controller.stop_flag == True:
            try:
                self.gettemp=dht_device.temperature # 抓取溫溼度
                self.gethumi=dht_device.humidity    # 抓取溫溼度
            except RuntimeError:
                pass           
            self.temperature.emit(self.gettemp)
            self.humidity.emit(self.gethumi)
            
            time.sleep(10) # 暫停一小段時間，不必實時更新，節省資源
            
                    
class MainWindow_controller(QtWidgets.QMainWindow):
    stop_flag = True
    deplicate_name = ''
    student_name_list = {}

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
            self.ProcessCam.getstdname.connect(self.getStdName)
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
        
        # 建立 Qimage 物件 (RGB格式)
        qimg = QtGui.QImage(img.data, self.Nx, self.Ny, QtGui.QImage.Format_RGB888).rgbSwapped()
        # viewData 的顯示設定
        self.ui.label_pic.setScaledContents(True)  # 尺度可變
        ### 將 Qimage 物件設置到 viewData 上
        self.ui.label_pic.setPixmap(QtGui.QPixmap.fromImage(qimg))

        # Frame Rate 計算並顯示到狀態欄上
 """       if self.frame_num == 0:
            self.time_start = time.time()
        if self.frame_num >= 0:
            self.frame_num += 1
            self.t_total = time.time() - self.time_start
            if self.frame_num % 100 == 0:
                self.frame_rate = float(self.frame_num) / self.t_total"""

    def getTime(self, times):
        self.ui.label_time.setText(times) # 修改現在時間
 
    def getStdName(self, object_name):
        self.rollCall = rollCall(object_name)
        self.rollCall.start()
        self.rollCall.stdname.connect(self.getRollCall) # 槽功能：取得姓名資料
        
    def getRollCall(self, student_name):
        self.ui.label_name.setText(student_name) # 修改名稱   
        
    def getTemperature(self, temperature):
        self.ui.label_temp.setText('溫度：{0:0.1f} 度'.format(temperature)) # 修改名稱 

    def getHumidity(self, humidity):
        self.ui.label_humi.setText('濕度：{0:0.1f} ％'.format(humidity)) # 修改名稱 
        
    def setup_control(self):
        """主視窗事件"""      
        self.display_texts() #顯示所有顯示文字
        self.load_student_name_from_csv() # 從CSV讀取學生姓名
        
        # 取得現在時間
        self.SystemTime = SystemTime() 
        self.SystemTime.systime.connect(self.getTime) # 槽功能：取得時間資料
        self.SystemTime.start()
               
        # 溫溼度系統
        self.GetTemperature = GetTemperature()
        self.GetTemperature.temperature.connect(self.getTemperature) # 槽功能：取得資料
        self.GetTemperature.humidity.connect(self.getHumidity) # 槽功能：取得資料
        self.GetTemperature.start()
    
    def display_texts(self): # 顯示所有顯示文字      
        self.ui.label_name.setText('姓名')
        self.ui.label_temp.setText('溫度')
        self.ui.label_pic.setText('影像辨識\n點名系統')
        self.ui.label_pic.setFont(QFont("Arial",35))
        
    def display_img(self): # 顯示圖片
        self.img = cv2.imread(self.img_path)
        height, width, channel = self.img.shape
        bytesPerline = 3 * width
        self.qimg = QImage(self.img, width, height, bytesPerline, QImage.Format_RGB888).rgbSwapped()
        self.ui.label_pic.setPixmap(QPixmap.fromImage(self.qimg))
        
    def load_student_name_from_csv(self): # 從CSV讀取學生姓名
        """ 讀取CSV資料，並轉換成字典 """
        with open('student_name.csv', mode='r', encoding='utf-8') as inp:
            self.reader = csv.reader(inp)
            MainWindow_controller.student_name_list = {rows[0]:rows[1] for rows in self.reader}
        
    def closeEvent(self, event):
        """ 視窗應用程式關閉事件 """
        MainWindow_controller.stop_flag = False
        if self.ProcessCam.running:
            self.ProcessCam.close()      # 關閉攝影機
            time.sleep(1)        
        time.sleep(0.5)
        self.ProcessCam.exit()  # 關閉子緒
        self.SystemTime.exit()  # 關閉子緒
        #self.rollCall.exit()  # 關閉子緒
        self.GetTemperature.exit()  # 關閉子緒
        QtWidgets.QApplication.closeAllWindows()  # 關閉所有視窗
        