import sys
import cv2
import numpy as np
from datetime import datetime
import pytz
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QHBoxLayout, QInputDialog
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap, QFont

class CameraRecorder(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Camera Recorder")
        self.resize(960, 500)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Status label - yuqoriga va o‘rtaga
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)  # O‘rtaga tekislandi
        self.status_label.setFont(QFont("Arial", 14, QFont.Bold))
        self.layout.addWidget(self.status_label)

        # Tugmalarni alohida qatorda pastroqqa joylashtiramiz
        btn_layout = QHBoxLayout()
        self.start_btn = QPushButton("Start")
        self.start_btn.setStyleSheet(
            "background-color: green; color: white; font-size: 12px; padding: 4px 16px;"
        )
        self.stop_btn = QPushButton("Stop")
        self.stop_btn.setStyleSheet(
            "background-color: red; color: white; font-size: 12px; padding: 4px 16px;"
        )
        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.stop_btn)
        btn_layout.addStretch()
        self.layout.addLayout(btn_layout)

        self.label = QLabel()
        self.layout.addWidget(self.label)

        self.start_btn.clicked.connect(self.start_recording)
        self.stop_btn.clicked.connect(self.stop_recording)
        self.stop_btn.hide()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)

        self.treams = [

        ]
        self.caps = [cv2.VideoCapture(url) for url in self.treams]
        self.screen_width = 1920
        self.screen_height = 1080
        self.cam_width = self.screen_width // 2
        self.cam_height = self.screen_height // 2

        self.recording = False
        self.writers = [None for _ in range(len(self.caps))]
        self.start_str = ""
        self.tz = pytz.timezone('Asia/Tashkent')

        self.timer.start(30)

    def start_recording(self):
        self.recording = True
        self.start_time = datetime.now(self.tz)
        self.start_str = self.start_time.strftime('%H-%M-%S.%f')[:-3]
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        for i in range(len(self.caps)):
            filename = f'camera_{i+1}_{self.start_str}.avi'
            self.writers[i] = cv2.VideoWriter(filename, fourcc, 20.0, (self.cam_width, self.cam_height))
        self.start_btn.hide()
        self.stop_btn.show()
        self.status_label.setText("● Yozuv ketmoqda...")
        self.status_label.setStyleSheet("color: red; font-weight: bold;")

    def stop_recording(self):
        if self.recording:
            end_time = datetime.now(self.tz)
            end_str = end_time.strftime('%H-%M-%S.%f')[:-3]
            import os
            for i, writer in enumerate(self.writers):
                if writer:
                    writer.release()
                    old_name = f'camera_{i+1}_{self.start_str}.avi'
                    new_name = f'camera_{i+1}_{self.start_str}-{end_str}.avi'
                    os.rename(old_name, new_name)
                    self.writers[i] = None
            self.recording = False
        self.stop_btn.hide()
        self.start_btn.show()
        self.status_label.setText("")

    def update_frame(self):
        frames = []
        now = datetime.now(self.tz)
        time_str = now.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

        # --- TIMER QO‘SHILDI ---
        if self.recording and hasattr(self, 'start_time') and self.start_time:
            elapsed = now - self.start_time
            hours, remainder = divmod(elapsed.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            timer_str = f"{hours:02}:{minutes:02}:{seconds:02}"
            self.status_label.setText(f"● Yozuv ketmoqda...  {timer_str}")
        # ---

        for i, cap in enumerate(self.caps):
            ret, frame = cap.read()
            if not ret:
                frame = np.zeros((self.cam_height, self.cam_width, 3), dtype=np.uint8)
            else:
                frame = cv2.resize(frame, (self.cam_width, self.cam_height))
            cv2.putText(frame, time_str, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0,0,0), 3)
            frames.append(frame)
            if self.recording and self.writers[i]:
                self.writers[i].write(frame)

        if len(frames) == 4:
            top = np.hstack((frames[0], frames[1]))
            bottom = np.hstack((frames[2], frames[3]))
            grid = np.vstack((top, bottom))
        else:
            grid = np.hstack(frames)

        rgb_image = cv2.cvtColor(grid, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        self.label.setPixmap(QPixmap.fromImage(qt_image))

    def closeEvent(self, event):
        self.stop_recording()
        for cap in self.caps:
            cap.release()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CameraRecorder()
    window.show()
    sys.exit(app.exec_())