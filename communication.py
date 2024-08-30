from PyQt5.QtCore import QObject, pyqtSignal
from threading import Thread, Event
import serial
import global_variables as gv


class Communication(QObject):
    data_received = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.serialPort = serial.Serial()

        self.t = None
        self.alive = Event()

    def connect(self):
        try:
            if not self.serialPort.is_open:
                self.serialPort.open()
                print("Connection opened")
                self.startThread()
            else:
                print("Connection is already open")

        except Exception as e:
            print(f"Failed to open connection: {e}")

    def disconnect(self):
        self.stopThread()
        if self.serialPort.is_open:
            self.serialPort.close()
            print("Connection closed")

    def readData(self):

        while self.alive.isSet() and self.serialPort.is_open:
            received_data = self.serialPort.readline().decode("utf-8").strip()
            data_packet = received_data.split()
            print("Received data: ", received_data)
            print(len(data_packet))
            
            if len(data_packet) == 10:

                # Extracting data from received data
                gv.packet_number = int(data_packet[0])
                gv.send_datetime = str(data_packet[1])
                gv.altitude = float(data_packet[2])
                gv.temperature = float(data_packet[3])
                gv.pressure = float(data_packet[4])
                gv.latitude = float(data_packet[5])
                gv.altitude = float(data_packet[6])
                gv.pitch = float(data_packet[7])
                gv.roll = float(data_packet[8])
                gv.yaw = float(data_packet[9])

                # Preparing data packet to be emitted                
                data_packet_str = ",".join(map(str, data_packet))
                data_packet_str = data_packet_str.strip()

                self.data_received.emit(data_packet_str)

    def startThread(self):
        if self.t is None or not self.t.is_alive():
            self.t = Thread(target=self.readData)
            self.t.setDaemon(True)
            self.alive.set()
            self.t.start()
            print("Thread started")

    def stopThread(self):
        if self.t and self.t.is_alive():
            self.alive.clear()  # Clear the event to stop the thread
            self.t.join()  # Wait for the thread to finish
            print("Thread stopped")
            self.t = None

