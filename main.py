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
from datetime import datetime
import pyqtgraph as pg
from gui import *
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

from communication import Communication
from data_axis_item import DateAxisItem
from video_receivered_with_websocket import VideoReceiverThread
import global_variables as gv
from global_functions import * 



class Window(QMainWindow):
    def __init__(self):
        super().__init__()

        self.unitUI = Ui_MainWindow()
        self.unitUI.setupUi(self)





def main():
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()