import cv2
import numpy as np
from datetime import datetime
import pytz

# RTSP manzillarini shu yerga yozing
treams = [

    
    
]

caps = [cv2.VideoCapture(url) for url in treams]

# Ekran o'lchamini aniqlash (masalan, 1920x1080)
screen_width = 1920
screen_height = 1080

# Har bir kamera uchun o'lcham
cam_width = screen_width // 2
cam_height = screen_height // 2

# Toshkent vaqti
tz = pytz.timezone('Asia/Tashkent')
start_time = datetime.now(tz)
start_str = start_time.strftime('%H-%M-%S.%f')[:-3]

# VideoWriter obyektlarini hozircha None qilib e'lon qilamiz
writers = [None for _ in range(len(caps))]

while True:
    frames = []
    now = datetime.now(tz)
    # Format: YYYY-MM-DD HH:MM:SS.mmm
    time_str = now.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    for i, cap in enumerate(caps):
        ret, frame = cap.read()
        if not ret:
            frame = np.zeros((cam_height, cam_width, 3), dtype=np.uint8)
        else:
            frame = cv2.resize(frame, (cam_width, cam_height))
        # Qalinroq va katta shrift bilan vaqtni chiqarish
        cv2.putText(frame, time_str, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0,0,0), 3)
        frames.append(frame)
        # Faylga yozishni faqat birinchi siklda yaratamiz
        if writers[i] is None:
            filename = f'camera_{i+1}_{start_str}.avi'
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            writers[i] = cv2.VideoWriter(filename, fourcc, 20.0, (cam_width, cam_height))
        writers[i].write(frame)  # Faylga yozish

    if len(frames) == 4:
        top = np.hstack((frames[0], frames[1]))
        bottom = np.hstack((frames[2], frames[3]))
        grid = np.vstack((top, bottom))
    else:
        grid = np.hstack(frames)

    cv2.namedWindow('4 Camera Grid', cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty('4 Camera Grid', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    cv2.imshow('4 Camera Grid', grid)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

end_time = datetime.now(tz)
end_str = end_time.strftime('%H-%M-%S.%f')[:-3]

# Fayllarni yakuniy nom bilan qayta nomlash
for i, writer in enumerate(writers):
    writer.release()
    old_name = f'camera_{i+1}_{start_str}.avi'
    new_name = f'camera_{i+1}_{start_str}-{end_str}.avi'
    import os
    os.rename(old_name, new_name)

for cap in caps:
    cap.release()
cv2.destroyAllWindows()