from PyQt5.QtCore import QElapsedTimer,QIODevice, pyqtSignal, QTimer, Qt, QThread, QObject, pyqtSignal, pyqtSlot
from PyQt5.QtSerialPort import QSerialPortInfo, QSerialPort
from PyQt5 import QtCore, QtGui, QtWidgets, QtOpenGL
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtGui import QImage, QPixmap  
from PyQt5.QtWidgets import *
from PyQt5 import QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import pyqtgraph as pg
from gui1 import *
from OpenGL import GL, GLU
from stl import mesh
import numpy as np
import folium
import time
import cv2
import csv
import sys
import io
import threading, wave, pyaudio,pickle,struct
import serial, serial.tools.list_ports
from threading import Thread, Event
import cv2, imutils, socket
import base64
import queue
import os
import sys
import asyncio
import websockets
import numpy as np
import cv2

PaketNumarası = 0
UyduStatusu = 0
HataKodu = "00000"
GöndermeSaati = "00/00/0000-00:00:00"
Basınç1 = 0.0
Basınç2 = 0.0
Yükseklik1 = 0.0
Yükseklik2 = 0.0
İrtifaFarkı = 0.0
İnişHızı = 0.0
Sıcaklık = 0.0
PilGerilimi = 0.0
GPS1Latitude = 0.0
GPS1Longitude = 0.0
GPS1Altitude = 0.0
Pitch = 0.0
Roll = 0.0
Yaw = 0.0
RHRH = "0000"
IoTData = 0.0
TakımNo = "000000"

TakımID = "000000"

veriPaketi = []
headerList = ["Paket Numarası","Uydu Statusu","Hata Kodu","Gönderme Saati","Basınç1","Basınç2","Yükseklik1","Yükseklik2","İrtifa Farkı","İnis Hızı","Sıcaklık","Pil Gerilimi","GPS1 Latitude","GPS1 Longitude","GPS1 Altitude","Pitch","Roll","Yaw","RHRH","IoT Data","Takım No"]
videoPath = ""


host = "localhost"
port = 5003
yerIstasyonuSocket =  socket.socket()
#yerIstasyonuSocket.connect((host,port))

q = queue.Queue(maxsize=10)
BUFF_SIZE = 65536


class Window(QMainWindow):
    def __init__(self):
        super().__init__()

        self.unitUI = Ui_MainWindow()
        self.unitUI.setupUi(self)

        self.serial = Communication()

        self.comboBoxesAddItem()
        self.actionTrigger()
        self.initFonks()

        self.serial.data_received.connect(self.updateTable)
        self.serial.data_received.connect(self.updateCSVFile)

        #init live video
        self.init_frame()
        self.video_receiver = VideoReceiverThread()
        self.video_receiver.new_frame.connect(self.update_frame)
        self.video_receiver.resolution_ready.connect(self.set_resolution)

        
    def init_frame(self):
        self.videoLabel = QLabel()
        self.videoLabel.setAlignment(Qt.AlignCenter)
        self.videoLabel.setMaximumSize(1000, 300)
        self.unitUI.verticalLayout.addWidget(self.videoLabel)

    def update_frame(self, frame):
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        height, width, _ = rgb_image.shape
        q_image = QImage(rgb_image.data, width, height, 3 * width, QImage.Format_RGB888)  
        pixmap = QPixmap.fromImage(q_image)  
        self.videoLabel.setPixmap(pixmap)

    def set_resolution(self, width, height):
        self.video_receiver.width = width
        self.video_receiver.height = height

    def start_recording_and_connect(self):
        self.video_receiver.start_recording()
        self.video_receiver.start()

    def stop_recording_and_disconnect(self):
        self.video_receiver.stop_recording_and_save()
        self.video_receiver.stop_connection_sync()

    def actionTrigger(self):
        self.unitUI.pushButtonConnect.clicked.connect(self.fonkConnect)
        self.unitUI.pushButtonDisconnect.clicked.connect(self.fonkDisconnect)
        self.unitUI.pushButtonFileOpen.clicked.connect(self.fonkFileOpen)
        self.unitUI.pushButtonSendVideo.clicked.connect(self.startVideoThread)
        self.unitUI.pushButton_9.clicked.connect(self.sendMekanikFiltreleme)
        self.unitUI.pushButton_10.clicked.connect(self.tasiyiciAyir)
        self.unitUI.pushButton.clicked.connect(self.start_recording_and_connect)
        self.unitUI.pushButton_2.clicked.connect(self.stop_recording_and_disconnect)

    def initFonks(self):
        self.init3DVisualizerWidget()
        self.initGraphs()
        self.initMap()
        self.initTexts()
        self.initCSVFile()
        self.initTable()
        self.initTimers()
        self.initProgressBar()

    def initTimers(self):
        self.timerUpdate3dVisualizer = QTimer()
        self.timerUpdate3dVisualizer.timeout.connect(self.update3DVisualizer)

        self.timerUpdateGraph1 = QTimer()
        self.timerUpdateGraph1.timeout.connect(self.updateGraph1)
        self.timerUpdateGraph2 = QTimer()
        self.timerUpdateGraph2.timeout.connect(self.updateGraph2)
        self.timerUpdateGraph3 = QTimer()
        self.timerUpdateGraph3.timeout.connect(self.updateGraph3)
        self.timerUpdateGraph4 = QTimer()
        self.timerUpdateGraph4.timeout.connect(self.updateGraph4)
        self.timerUpdateGraph5 = QTimer()
        self.timerUpdateGraph5.timeout.connect(self.updateGraph5)
        self.timerUpdateGraph6 = QTimer()
        self.timerUpdateGraph6.timeout.connect(self.updateGraph6)

        self.timerUpdateMap = QTimer()
        self.timerUpdateMap.timeout.connect(self.updateMap)

        self.timerUpdateText = QTimer()
        self.timerUpdateText.timeout.connect(self.updateTexts)

        self.timerUpdateTable = QTimer()
        self.timerUpdateTable.timeout.connect(self.updateTable)

    def startTimers(self):
        self.timerUpdate3dVisualizer.start(1000)

        self.timerUpdateGraph1.start(1000)
        self.timerUpdateGraph2.start(1000)
        self.timerUpdateGraph3.start(1000)
        self.timerUpdateGraph4.start(1000)
        self.timerUpdateGraph5.start(1000)
        self.timerUpdateGraph6.start(1000)

        self.timerUpdateMap.start(1000)
        self.timerUpdateTable.start(1000)
        self.timerUpdateText.start(1000)

    def stopTimers(self):
        self.timerUpdate3dVisualizer.stop()

        self.timerUpdateGraph1.stop()
        self.timerUpdateGraph2.stop()
        self.timerUpdateGraph3.stop()
        self.timerUpdateGraph4.stop()
        self.timerUpdateGraph5.stop()
        self.timerUpdateGraph6.stop()

        self.timerUpdateMap.stop()
        self.timerUpdateTable.stop()

    def initTexts(self):
        global TakımID

        GyroText = "x:\ty:\tz:\t" 
        self.unitUI.labelGyro.setText(GyroText)

        mapText = "GPS Latitude:\nGPS Longitude:\nGPS Altitude:" 
        self.unitUI.labelGPS.setText(mapText)

        paketNumarasıText = "Paket Numarası:\n"
        self.unitUI.labelPaketNumarasi.setText(paketNumarasıText)             

        uyduStatusuText = "Uydu statüsü:\n"
        self.unitUI.labelUyduStatusu.setText(uyduStatusuText)

        hataKoduText = "Hata Kodu:\n"
        self.unitUI.labelHataKodu.setText(hataKoduText)

        göndermeSaatiText = "Gönderim Saati:\n"
        self.unitUI.labelGondermeSaati.setText(göndermeSaatiText)  

        irtifaFarkıText = "İrtifa Farkı:\n"
        self.unitUI.labelIrtifaFarki.setText(irtifaFarkıText) 

        taşıyıcıBasınçText = "Taşıyıcı Basınç:\n"
        self.unitUI.labelTasiyicibasinc.setText(taşıyıcıBasınçText) 

        taşıyıcıYükseklikText = "Taşıyıcı Yükseklik:\n"
        self.unitUI.labelTasiyciYukseklik.setText(taşıyıcıYükseklikText)  

        takımIDText = f"Takım ID:\n{TakımID}"
        self.unitUI.labelTakmID.setText(takımIDText)
    
    def updateTexts(self):
        global Roll, Pitch, Yaw, GPS1Latitude, GPS1Longitude, GPS1Altitude, PaketNumarası, UyduStatusu, HataKodu, GöndermeSaati, Basınç2, Yükseklik2

        GyroText = "x: {:.2f}\t".format(Pitch) + \
               "y: {:.2f}\t".format(Roll) + \
               "z: {:.2f}".format(Yaw)
        self.unitUI.labelGyro.setText(GyroText)

        mapText = "GPS Latitude: " + str(GPS1Latitude) + "\n" + \
            "GPS Longitude: " + str(GPS1Longitude) + "\n" + \
            "GPS Altitude: " + str(GPS1Altitude) 
        self.unitUI.labelGPS.setText(mapText)

        paketNumarasıText = f"Paket Numarası:\n{PaketNumarası}"
        self.unitUI.labelPaketNumarasi.setText(paketNumarasıText)             

        uyduStatusuText = f"Uydu statüsü:\n{UyduStatusu}"
        self.unitUI.labelUyduStatusu.setText(uyduStatusuText)

        hataKoduText = f"Hata Kodu:\n{HataKodu}"
        self.unitUI.labelHataKodu.setText(hataKoduText)

        göndermeSaatiText = f"Gönderim Saati:\n{GöndermeSaati}"
        self.unitUI.labelGondermeSaati.setText(göndermeSaatiText)  

        irtifaFarkıText = f"İrtifa Farkı:\n{İrtifaFarkı}"
        self.unitUI.labelIrtifaFarki.setText(irtifaFarkıText) 

        taşıyıcıBasınçText = f"Taşıyıcı Basınç:\n{Basınç2}"
        self.unitUI.labelTasiyicibasinc.setText(taşıyıcıBasınçText) 

        taşıyıcıYükseklikText = f"Taşıyıcı Yükseklik:\n{Yükseklik2}"
        self.unitUI.labelTasiyciYukseklik.setText(taşıyıcıYükseklikText)  

    def comboBoxesAddItem(self):
        self.unitUI.comboBoxPort.clear()
        self.unitUI.comboBoxBaudRate.clear()

        serialPorts = serial.tools.list_ports.comports()
        serialPortNames = [port.device for port in serialPorts]
        self.unitUI.comboBoxPort.addItems(serialPortNames)

        baudRates = [9600,1200, 19200, 38400, 57600, 115200]
        self.unitUI.comboBoxBaudRate.addItems(map(str,baudRates))

    def fonkConnect(self):
        portName = self.unitUI.comboBoxPort.currentText()
        baudRate = int(self.unitUI.comboBoxBaudRate.currentText())

        self.serial.serialPort.port = portName
        self.serial.serialPort.baudrate = baudRate
        self.serial.connect()

        if self.serial.serialPort.is_open: #self.alive.isSet() and self.serialPort.is_open
            self.startTimers()

            self.unitUI.pushButtonConnect.setEnabled(False)
            self.unitUI.pushButtonDisconnect.setEnabled(True)

            self.unitUI.comboBoxPort.setEnabled(False)
            self.unitUI.comboBoxBaudRate.setEnabled(False)
    
    def fonkDisconnect(self):
        self.serial.disconnect()

        if not self.serial.serialPort.is_open:
            print("if bloğuna girdi")
            self.stopTimers()
            self.unitUI.pushButtonConnect.setEnabled(True)
            self.unitUI.pushButtonDisconnect.setEnabled(False)

            self.unitUI.comboBoxPort.setEnabled(True)
            self.unitUI.comboBoxBaudRate.setEnabled(True)

    def init3DVisualizerWidget(self):
        self.gyroWidget = QWidget()
        self.unitUI.verticalLayoutGyro.addWidget(self.gyroWidget)
        self.vbox = QVBoxLayout()
        self.glWidget = GLWidget()
        self.vbox.addWidget(self.glWidget)
        self.gyroWidget.setLayout(self.vbox)

    def update3DVisualizer(self):
        self.glWidget.update()

    def initGraphs(self):
        self.graphWidget1 = pg.PlotWidget()
        self.graphWidget2 = pg.PlotWidget()
        self.graphWidget3 = pg.PlotWidget()
        self.graphWidget4 = pg.PlotWidget()
        self.graphWidget5 = pg.PlotWidget()
        self.graphWidget6 = pg.PlotWidget()

        self.unitUI.horizontalLayoutGraph.addWidget(self.graphWidget1)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.unitUI.horizontalLayoutGraph.addItem(spacerItem2)
        self.unitUI.horizontalLayoutGraph.addWidget(self.graphWidget2)
        self.unitUI.horizontalLayoutGraph.addWidget(self.graphWidget3)
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.unitUI.horizontalLayoutGraph.addItem(spacerItem3)

        self.unitUI.horizontalLayoutGraph1.addWidget(self.graphWidget4)
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.unitUI.horizontalLayoutGraph1.addItem(spacerItem3)
        self.unitUI.horizontalLayoutGraph1.addWidget(self.graphWidget5)
        self.unitUI.horizontalLayoutGraph1.addWidget(self.graphWidget6)
        spacerItem4 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.unitUI.horizontalLayoutGraph1.addItem(spacerItem4)

        self.graphWidget1.setBackground('w')
        self.graphWidget2.setBackground('w')
        self.graphWidget3.setBackground('w')
        self.graphWidget4.setBackground('w')
        self.graphWidget5.setBackground('w')
        self.graphWidget6.setBackground('w')

        self.graphWidget1.showGrid(x=True, y=True)
        self.graphWidget2.showGrid(x=True, y=True)
        self.graphWidget3.showGrid(x=True, y=True)
        self.graphWidget4.showGrid(x=True, y=True)
        self.graphWidget5.showGrid(x=True, y=True)
        self.graphWidget6.showGrid(x=True, y=True)

        self.graphWidget1.setTitle('<html><font size="3" color="#131313">Basınç Grafiği</font></html>')
        self.graphWidget2.setTitle('<html><font size="3" color="#131313">Sıcaklık Grafiği</font></html>')
        self.graphWidget3.setTitle('<html><font size="3" color="#131313">Nem Grafiği</font></html>')
        self.graphWidget4.setTitle('<html><font size="3" color="#131313">Pil Gerilimi Grafiği</font></html>')
        self.graphWidget5.setTitle('<html><font size="3" color="#131313">Yükseklik Grafiği</font></html>')
        self.graphWidget6.setTitle('<html><font size="3" color="#131313">Hız Grafiği</font></html>')

        self.graphWidget1.setLabel('left', 'Basınç (Pa)')
        self.graphWidget1.setLabel('bottom', 'Zaman')

        self.graphWidget2.setLabel('left', 'Sıcaklık (°C)')
        self.graphWidget2.setLabel('bottom', 'Zaman')

        self.graphWidget3.setLabel('left', 'Nem (g/m³)')
        self.graphWidget3.setLabel('bottom', 'Zaman')

        self.graphWidget4.setLabel('left', 'Pil Gerilimi (V)')
        self.graphWidget4.setLabel('bottom', 'Zaman')

        self.graphWidget5.setLabel('left', 'Yükseklik (m)')
        self.graphWidget5.setLabel('bottom', 'Zaman')

        self.graphWidget6.setLabel('left', 'Hız (m/s)')
        self.graphWidget6.setLabel('bottom', 'Zaman')

        self.curve1 = self.graphWidget1.plot(pen={'color': '#054569', 'width': 2})
        self.curve2 = self.graphWidget2.plot(pen={'color': '#054569', 'width': 2})
        self.curve3 = self.graphWidget3.plot(pen={'color': '#054569', 'width': 2})
        self.curve4 = self.graphWidget4.plot(pen={'color': '#054569', 'width': 2})
        self.curve5 = self.graphWidget5.plot(pen={'color': '#054569', 'width': 2})
        self.curve6 = self.graphWidget6.plot(pen={'color': '#054569', 'width': 2})

        self.x_values1 = []
        self.y_values1 = []
        self.x_values2 = []
        self.y_values2 = []
        self.x_values3 = []
        self.y_values3 = []
        self.x_values4 = []
        self.y_values4 = []
        self.x_values5 = []
        self.y_values5 = []
        self.x_values6 = []
        self.y_values6 = []

    def updateGraph1(self):
        global Basınç1
        self.x_values1.append(len(self.x_values1))
        self.y_values1.append(float(Basınç1))

        x_values1 = self.x_values1[-5:]
        y_values1 = self.y_values1[-5:]

        self.graphWidget1.setYRange(self.y_values1[-1] -3, self.y_values1[-1] + 3)
        self.curve1.setData(x_values1, y_values1)

    def updateGraph2(self):
        global Sıcaklık
        self.x_values2.append(len(self.x_values2))
        self.y_values2.append(float(Sıcaklık))

        x_values2 = self.x_values2[-5:]
        y_values2 = self.y_values2[-5:]

        self.graphWidget2.setYRange(self.y_values2[-1] -0.5,self.y_values2[-1] +0.5)
        self.curve2.setData(x_values2, y_values2)

    def updateGraph3(self):
        global IoTData
        self.x_values3.append(len(self.x_values3))
        self.y_values3.append(float(IoTData))

        x_values3 = self.x_values3[-5:]
        y_values3 = self.y_values3[-5:]

        self.graphWidget3.setYRange(self.y_values3[-1] - 0.5, self.y_values3[-1] + 0.5)
        self.curve3.setData(x_values3, y_values3)

    def updateGraph4(self):
        global PilGerilimi
        self.x_values4.append(len(self.x_values4))
        self.y_values4.append(float(PilGerilimi))

        x_values4 = self.x_values4[-5:]
        y_values4 = self.y_values4[-5:]

        self.graphWidget4.setYRange(self.y_values4[-1] -0.5, self.y_values4[-1] + 0.5)
        self.curve4.setData(x_values4, y_values4)

    def updateGraph5(self):
        global Yükseklik1
        self.x_values5.append(len(self.x_values5))
        self.y_values5.append(float(Yükseklik1))

        x_values5 = self.x_values5[-5:]
        y_values5 = self.y_values5[-5:]

        self.graphWidget5.setYRange(self.y_values5[-1] - 0.5, self.y_values5[-1] + 0.5)
        self.curve5.setData(x_values5, y_values5)

    def updateGraph6(self):
        global İnişHızı
        self.x_values6.append(len(self.x_values6))
        self.y_values6.append(float(İnişHızı))

        x_values6 = self.x_values6[-5:]
        y_values6 = self.y_values6[-5:]

        self.graphWidget6.setYRange(self.y_values6[-1] - 0.5, self.y_values6[-1] + 0.5)
        self.curve6.setData(x_values6, y_values6)

    def initMap(self):
        global GPS1Latitude, GPS1Longitude
        coordinate = (GPS1Latitude,GPS1Longitude)
        self.mapp = folium.Map(
            location=coordinate,
            zoom_start=15,
        )

        folium.Marker([GPS1Latitude, GPS1Longitude], popup='gps').add_to(self.mapp)

        data = io.BytesIO()
        self.mapp.save(data, close_file=False)

        self.web_view = QWebEngineView()
        self.web_view.setHtml(data.getvalue().decode())
        self.unitUI.verticalLayoutGPS.addWidget(self.web_view)

    def updateMap(self):
        global GPS1Latitude, GPS1Longitude
        self.coordinate = [GPS1Latitude, GPS1Longitude]

        self.mapp = folium.Map(
            location=self.coordinate,
            zoom_start=15,
        )

        folium.Marker([GPS1Latitude, GPS1Altitude], popup='gps').add_to(self.mapp)
        
        data = io.BytesIO()
        self.mapp.save(data, close_file=False)
        self.web_view.setHtml(data.getvalue().decode())

    def initCSVFile(self):
        global headerList
        self.csv_dosyasi = 'veri.csv'
        with open(self.csv_dosyasi, 'w', newline='', encoding='utf-8') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(headerList)

    def updateCSVFile(self):
        global veriPaketi
        with open(self.csv_dosyasi, 'a', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(veriPaketi)

    def initTable(self):
        global headerList 
        self.tableWidget = QTableWidget()
        self.tableWidget.setStyleSheet("background-color: #CED7E0;")
        self.tableWidget.verticalHeader().hide()
        self.values = 0
        self.tableWidget.setRowCount(self.values + 1)
        self.tableWidget.setColumnCount(21)
        self.tableWidget.setRowHeight(0,10)
      
        for index, header in enumerate(headerList):
            header_item = QTableWidgetItem(header)
            header_item.setForeground(QColor("#131313"))
            self.tableWidget.setHorizontalHeaderItem(index, header_item)
        
        self.unitUI.verticalLayoutTable.addWidget(self.tableWidget)

        #for i in range(self.tableWidget.columnCount()):
        #    self.tableWidget.setColumnWidth(i, int(self.tableWidget.columnWidth(i) * 0.9))
        #self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

    def updateTable(self):
        global veriPaketi
        print("updateTable",veriPaketi)
        print(len(veriPaketi))
        
        def floatToStr(number):
            return str(number)
        
        if (len(veriPaketi) == 21):

            self.tableWidget.selectRow(self.values)

            table_list = veriPaketi
            table_list = list(map(floatToStr, table_list))
            index = 0
            while index <= 20:
                self.tableWidget.setItem(self.values, index, QTableWidgetItem(table_list[index]))
                self.tableWidget.setRowHeight(index,10)
                index += 1
            self.values += 1
            self.tableWidget.setRowCount(self.values + 1)
            self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        else:
            print("pas geçildi")

    def sendMekanikFiltreleme(self):
        global yerIstasyonuSocket

        R = self.unitUI.lineEdit_17.text()
        H = self.unitUI.lineEdit_18.text()
        R1 = self.unitUI.lineEdit_19.text()
        H1 = self.unitUI.lineEdit_20.text()
        command = R + H + R1 + H1 
        print(command)
        yerIstasyonuSocket.send(command.encode())

    def tasiyiciAyir(self):
        global yerIstasyonuSocket
        command = "taşıyıcıyı ayır"
        print(command)
        yerIstasyonuSocket.send(command.encode())
        
    def fonkFileOpen(self):
        global videoPath
        filter = "Video Files (*.mp4 *.m4a);;All Files (*)"
        url = QFileDialog.getOpenFileName(self, "Dosya Seç", "",filter)  # ;özel bir yol tanımlamak için;
        videoPath = url[0]
        print(videoPath)

    def initProgressBar(self):
        self.unitUI.progressBar.setValue(0)
        self.videoThread = SendVideo()

    def startVideoThread(self):
        self.videoThread.updateProgress.connect(self.updateProgressBar)
        self.videoThread.start()

    def updateProgressBar(self,val):
        self.unitUI.progressBar.setValue(val)

class VideoReceiverThread(QThread):
    new_frame = pyqtSignal(np.ndarray)
    resolution_ready = pyqtSignal(int, int)

    def __init__(self):
        super().__init__()
        self.frames = []  # Kayıt edilecek tüm kareleri saklamak için bir liste
        self.recording = False
        self.filename = 'output.mp4'
        self.audio_filename = 'output_audio.wav'
        self.final_filename = 'final_output.mp4'
        self.fps = 20.0
        self.width = None
        self.height = None
        self.video_writer = None
        self.websocket = None
        self.loop = asyncio.new_event_loop()  # Yeni bir event loop oluştur
        asyncio.set_event_loop(self.loop)
        self.audio_stream = None
        self.audio_frames = []

    async def receive_video(self):
        if self.websocket is None:
            self.websocket = await websockets.connect("ws://localhost:8888")
        
        while self.websocket is not None:
            try:
                data = await self.websocket.recv()
                nparr = np.frombuffer(data, np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                if img is not None:
                    if self.width is None or self.height is None:
                        # İlk görüntü alındığında boyutları belirle
                        self.height, self.width, _ = img.shape
                        self.resolution_ready.emit(self.width, self.height)
                    
                    self.new_frame.emit(img)
                    
                    if self.recording:
                        self.frames.append(img)  # Frame'leri listeye ekle
            except Exception as e:
                print(f"An error occurred while receiving video: {e}")
                break

    def run(self):
        self.audio_stream = self.start_audio_recording()  # Ses kaydını başlat
        self.loop.run_until_complete(self.receive_video())

    def start_recording(self):
        self.recording = True
        self.frames = []  # Önceki kareleri temizle
        self.audio_frames = []

    def stop_recording_and_save(self):
        self.recording = False
        self.stop_audio_recording()  # Ses kaydını durdur ve kaydet
        if self.frames and self.width and self.height:
            try:
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                self.video_writer = cv2.VideoWriter(self.filename, fourcc, self.fps, (self.width, self.height))
                
                if not self.video_writer.isOpened():
                    print("Error: VideoWriter could not be opened.")
                    return
        
                for frame in self.frames:
                    resized_frame = cv2.resize(frame, (self.width, self.height))
                    self.video_writer.write(resized_frame)
                self.video_writer.release()
                print("Recording saved successfully.")
            except Exception as e:
                print(f"An error occurred: {e}")
            finally:
                self.frames = []  # Kayıt tamamlandığında listeyi temizle
            
            # Video ve ses dosyalarını birleştir
            self.merge_audio_video()

    def start_audio_recording(self):
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16,
                        channels=2,
                        rate=44100,
                        input=True,
                        frames_per_buffer=1024)
        return stream

    def stop_audio_recording(self):
        self.audio_stream.stop_stream()
        self.audio_stream.close()

        # Ses verilerini .wav dosyasına kaydet
        p = pyaudio.PyAudio()
        wf = wave.open(self.audio_filename, 'wb')
        wf.setnchannels(2)
        wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(44100)
        wf.writeframes(b''.join(self.audio_frames))
        wf.close()

    async def receive_audio(self):
        while self.recording:
            data = self.audio_stream.read(1024)
            self.audio_frames.append(data)

    async def stop_connection(self):
        if self.websocket:
            try:
                await self.websocket.close()
            except Exception as e:
                print(f"An error occurred while closing websocket: {e}")
            finally:
                self.websocket = None

    def stop_connection_sync(self):
        asyncio.run(self.stop_connection())

    def merge_audio_video(self):
        import subprocess

        command = f'ffmpeg -y -i {self.filename} -i {self.audio_filename} -c:v copy -c:a aac -strict experimental {self.final_filename}'
        subprocess.run(command, shell=True)
        print(f"Final video saved as {self.final_filename}")

class GLWidget(QOpenGLWidget):
    def __init__(self, parent=None):
        super(GLWidget, self).__init__(parent)

        stl_path = "model_uydu.stl"
        stl_model = mesh.Mesh.from_file(stl_path)

        self.vectors = stl_model.vectors
        self.normals = stl_model.normals

    def initializeGL(self):
        GL.glClearColor(1,1,1,1)
        GL.glEnable(GL.GL_DEPTH_TEST)

    def resizeGL(self, width, height):
        if height == 0:
            height = 1

        GL.glViewport(0, 0, width, height)

        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()

        GLU.gluPerspective(45.0, width / float(height), 1.0, 100.0)
        GL.glMatrixMode(GL.GL_MODELVIEW)

    def paintGL(self):
        global Roll, Pitch, Yaw

        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        GL.glLoadIdentity()
        GL.glPushMatrix()

        GL.glTranslatef(0.0, 0.0, -50.0)

        GL.glRotatef(Roll, 1, 0, 0)
        GL.glRotatef(Pitch, 0, 1, 0)
        GL.glRotatef(Yaw, 0, 0, 1)

        GL.glLineWidth(2.0)
        GL.glBegin(GL.GL_LINES)
        # X Ekseni
        GL.glColor3f(0.278,0.302,0.318)
        GL.glVertex3f(-100.0, 0.0, 0.0)
        GL.glVertex3f(100.0, 0.0, 0.0)
        # Y Ekseni
        GL.glColor3f(0.278,0.302,0.318) 
        GL.glVertex3f(0.0, -100.0, 0.0)
        GL.glVertex3f(0.0, 100.0, 0.0)
        # Z Ekseni
        GL.glColor3f(0.278,0.302,0.318)
        GL.glVertex3f(0.0, 0.0, -100.0)
        GL.glVertex3f(0.0, 0.0, 100.0)
        GL.glEnd()

        GL.glEnableClientState(GL.GL_VERTEX_ARRAY)
        GL.glEnableClientState(GL.GL_COLOR_ARRAY)

        GL.glPolygonMode(GL.GL_FRONT_AND_BACK, GL.GL_FILL)

        GL.glBegin(GL.GL_TRIANGLES)
        GL.glColor3f(0.0, 0.4, 0.5) 
        for triangle in self.vectors:
            for vertex in triangle:
                GL.glVertex3fv(vertex)
        GL.glEnd()

        GL.glPolygonMode(GL.GL_FRONT_AND_BACK, GL.GL_LINE)

        GL.glLineWidth(1.0)
        GL.glBegin(GL.GL_TRIANGLES)
        GL.glColor3f(0.01960784313, 0.27058823529, 0.41176470588)
        for triangle in self.vectors:
            for vertex in triangle:
                GL.glVertex3fv(vertex)
        GL.glEnd()

        GL.glDisableClientState(GL.GL_VERTEX_ARRAY)
        GL.glDisableClientState(GL.GL_COLOR_ARRAY)

        GL.glPopMatrix()

class Communication(QObject):
    data_received = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.serialPort = serial.Serial()

        self.t = None
        self.alive = Event()

        self.roll_list = []
        self.pitch_list = []
        self.yaw_list = []

        self.value = 0

    def connect(self):
        try:
            if not self.serialPort.is_open:
                self.serialPort.open()
                print("Bağlantı açıldı")
                self.startThread()
            else:
                print("Bağlantı zaten açık")

        except Exception as e:
            print(f"Bağlantı açılamadı: {e}")

    def disconnect(self):
        self.stopThread()
        if self.serialPort.is_open:
            self.serialPort.close()
            print("Bağlantı kapatıldı")

    def readData(self):
        global veriPaketi
        global PaketNumarası, UyduStatusu, HataKodu, GöndermeSaati, Basınç1, Basınç2
        global Yükseklik1, Yükseklik2, İrtifaFarkı, İnişHızı, Sıcaklık, PilGerilimi
        global GPS1Latitude, GPS1Longitude, GPS1Altitude, Pitch, Roll, Yaw
        global RHRH, IoTData, TakımNo

        while(self.alive.isSet() and self.serialPort.is_open):
            data = self.serialPort.readline().decode("utf-8").strip()
            received_data = data.split()
            print("received data: ",received_data)
            print(len(received_data))
            
            if (len(received_data) == 14):
                print("---------------------")
            #if (len(received_data) == 21):
                """
                PaketNumarası = int(received_data[0])
                UyduStatusu = received_data[1]
                HataKodu = received_data[2]
                GöndermeSaati = received_data[3]
                Basınç1 = float(received_data[4])
                Basınç2 = float(received_data[5])
                Yükseklik1 = float(received_data[6])
                Yükseklik2 = float(received_data[7])
                İrtifaFarkı = float(received_data[8])
                İnişHızı = float(received_data[9])
                Sıcaklık = float(received_data[10])
                PilGerilimi = float(received_data[11])
                GPS1Latitude = float(received_data[12])
                GPS1Longitude = float(received_data[13])
                GPS1Altitude = float(received_data[14])
                Pitch = float(received_data[15])
                Roll = float(received_data[16])
                Yaw = float(received_data[17])
                RHRH = received_data[18]
                IoTData = float(received_data[19])
                TakımNo = received_data[20]
                """

                PaketNumarası = 0
                UyduStatusu = 0
                HataKodu = "00000"
                GöndermeSaati = "00/00/0000-00:00:00"
                Basınç2 = 0.0
                Yükseklik2 = 0.0
                İrtifaFarkı = 0.0
                İnişHızı = 0.0
                PilGerilimi = 0.0
                GPS1Latitude = 0.0
                GPS1Longitude = 0.0
                GPS1Altitude = 0.0
                RHRH = "0000"
                TakımNo = "000000"

                Sıcaklık = float(received_data[10])
                Basınç1 = float(received_data[11])
                IoTData = float(received_data[12]) / 100.0
                Yükseklik1 = float(received_data[13])

                accelX = float(received_data[0])
                accelY = float(received_data[1])
                accelZ = float(received_data[2])
                gyroX = float(received_data[3])
                gyroY = float(received_data[4])
                gyroZ = float(received_data[5])
                """
                Roll = float(received_data[6])
                Pitch = float(received_data[7])
                Yaw = float(received_data[8])
                """
                
                #Roll = np.arctan2(accelY, accelZ) * 180 / np.pi
                #Pitch = np.arctan2(-accelX, np.sqrt(accelY ** 2 + accelZ ** 2)) * 180 / np.pi
                #Yaw = gyroZ
                 
                self.roll_list.append(float(received_data[6]))
                self.pitch_list.append(float(received_data[7]))
                self.yaw_list.append(float(received_data[8]))

                roll_list = np.array(self.roll_list[-4:])
                pitch_list = np.array(self.pitch_list[-4:])
                yaw_list = np.array(self.yaw_list[-4:])

                Roll = np.mean(roll_list) 
                Pitch = np.mean(pitch_list)
                Yaw = np.mean(yaw_list)

                veriPaketi = [
                    PaketNumarası, UyduStatusu, HataKodu, 
                    GöndermeSaati, Basınç1, Basınç2, 
                    Yükseklik1, Yükseklik2, İrtifaFarkı, 
                    İnişHızı, Sıcaklık, PilGerilimi, 
                    GPS1Latitude, GPS1Longitude, GPS1Altitude, 
                    Pitch, Roll, Yaw, RHRH, IoTData, TakımNo]
                
                veriPaketiStr = ",".join(map(str, veriPaketi))
                veriPaketiStr = veriPaketiStr.strip()
                print("veriPaketiStr",veriPaketiStr)
                print(len(veriPaketiStr))

                if self.value % 4 == 0:
                    #self.data_received.emit(data)
                    self.data_received.emit(veriPaketiStr)
                self.value += 1 
                
                

    def startThread(self):
        if self.t is None or not self.t.is_alive():
            self.t = Thread(target=self.readData)
            self.t.setDaemon(True)
            self.alive.set()
            self.t.start()
            print("İş parçacığı başlatıldı")

    def stopThread(self):
        if self.t and self.t.is_alive():
            self.alive.clear()  # Olayı temizle ve iş parçacığının durmasını sağla
            self.t.join()  # İş parçacığının bitmesini bekle
            print("İş parçacığı durduruldu")
            self.t = None

class SendVideo(QThread):
    updateProgress = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.file_name =  'test_video.mp4'
        self.host_ip = '127.0.0.1'
        self.video_port = 65432
        self.WIDTH = 400
        self.FPS = None
        self.TS = None
        self.server_socket = None
        self.vid = None

    def run(self):
        self.setup_video()
        self.start_video_stream()

    def setup_video(self):
        global BUFF_SIZE

        # Video dosyasını aç
        self.vid = cv2.VideoCapture(self.file_name)
        self.FPS = self.vid.get(cv2.CAP_PROP_FPS)
        self.TS = 0.5 / self.FPS
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, BUFF_SIZE)
        socket_address = (self.host_ip, self.video_port)
        self.server_socket.bind(socket_address)
        print(f'Listening for video on: {socket_address}')

    def start_video_stream(self):
        def video_stream_gen():
            while self.vid.isOpened():
                try:
                    _, frame = self.vid.read()
                    if frame is None:
                        break
                    frame = imutils.resize(frame, width=self.WIDTH)
                    q.put(frame)
                except Exception as e:
                    print(f"Video stream error: {e}")
                    self.vid.release()
                    return

        def video_stream():
            global q, BUFF_SIZE
            fps, st, frames_to_count, cnt = (0, 0, 1, 0)
            cv2.namedWindow('TRANSMITTING VIDEO')
            cv2.moveWindow('TRANSMITTING VIDEO', 10, 30)
            while True:
                msg, client_addr = self.server_socket.recvfrom(BUFF_SIZE)
                print('GOT connection from ', client_addr)

                while True:
                    frame = q.get()
                    encoded, buffer = cv2.imencode('.jpeg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
                    message = base64.b64encode(buffer)
                    self.server_socket.sendto(message, client_addr)
                    frame = cv2.putText(frame, 'FPS: ' + str(round(fps, 1)), (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    if cnt == frames_to_count:
                        try:
                            fps = (frames_to_count / (time.time() - st))
                            st = time.time()
                            cnt = 0
                            if fps > self.FPS:
                                self.TS += 0.001
                            elif fps < self.FPS:
                                self.TS -= 0.001
                        except Exception as e:
                            print(f"FPS calculation error: {e}")
                    cnt += 1
                    self.updateProgress.emit(int((cnt / frames_to_count) * 100))
                    key = cv2.waitKey(int(1000 * self.TS)) & 0xFF
                    if key == ord('q'):
                        print("Exiting video stream")
                        return

        video_thread_gen = threading.Thread(target=video_stream_gen)
        video_thread = threading.Thread(target=video_stream)
        video_thread_gen.start()
        video_thread.start()


def main():
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()