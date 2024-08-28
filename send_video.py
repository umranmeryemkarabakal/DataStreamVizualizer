from PyQt5.QtCore import QThread,pyqtSignal
import threading
import imutils
import socket
import base64
import time
import cv2
import global_variables

class SendVideo(QThread):
    updateProgress = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        global file_name
        #self.file_name = file_name
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
