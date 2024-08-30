from PyQt5.QtCore import QThread, pyqtSignal
import numpy as np
import websockets
import asyncio
import cv2


class VideoReceiverThread(QThread):
    new_frame = pyqtSignal(np.ndarray)
    resolution_ready = pyqtSignal(int, int)

    def __init__(self):
        super().__init__()
        self.frames = []  # Kayıt edilecek tüm kareleri saklamak için bir liste
        self.recording = False
        self.filename = 'output.mp4'
        self.fps = 20.0
        self.width = None
        self.height = None
        self.video_writer = None
        self.websocket = None
        self.loop = asyncio.new_event_loop()  # Yeni bir event loop oluştur
        asyncio.set_event_loop(self.loop)

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
        self.loop.run_until_complete(self.receive_video())

    def start_recording(self):
        self.recording = True
        self.frames = []  # Önceki kareleri temizle

    def stop_recording_and_save(self):
        self.recording = False
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

