from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QImage
import cv2
import struct
import pickle
import socket 

class VideoStreamThread(QThread):
    frame_signal = pyqtSignal(QImage)
    
    def __init__(self, host, port, output_file='output.mp4'):
        super().__init__()
        self.host = host
        self.port = port
        self.running = True
        self.output_file = output_file

    def run(self):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((self.host, self.port))

        data = b""
        payload_size = struct.calcsize("Q")

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # MP4 codec
        # Genişlik ve yükseklik değerlerini uygun şekilde ayarlayın
        out = cv2.VideoWriter(self.output_file, fourcc, 20.0, (640, 480))

        while self.running:
            while len(data) < payload_size:
                packet = client_socket.recv(4*1024)  # Veri paketlerini alma
                if not packet: break
                data += packet

            packed_msg_size = data[:payload_size]
            data = data[payload_size:]
            msg_size = struct.unpack("Q", packed_msg_size)[0]

            while len(data) < msg_size:
                data += client_socket.recv(4*1024)

            frame_data = data[:msg_size]
            data = data[msg_size:]

            # Görüntüyü çözme
            frame = pickle.loads(frame_data)
            height, width, channels = frame.shape
            bytes_per_line = channels * width
            q_image = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888)

            # Sinyali tetikleyerek GUI'yi güncelle
            self.frame_signal.emit(q_image)

            # OpenCV VideoWriter ile videoyu dosyaya yaz
            out.write(cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))

        out.release()
        client_socket.close()

    def stop(self):
        self.running = False
        self.wait()
