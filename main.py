import cv2
import numpy as np

# RTSP manzillarini shu yerga yozing
treams = [
    'rtsp://username:password@ip1:554/stream1',
    'rtsp://username:password@ip2:554/stream2',
    'rtsp://username:password@ip3:554/stream3',
    'rtsp://username:password@ip4:554/stream4',
]

caps = [cv2.VideoCapture(url) for url in treams]

while True:
    frames = []
    for cap in caps:
        ret, frame = cap.read()
        if not ret:
            frame = np.zeros((240, 320, 3), dtype=np.uint8)
        frame = cv2.resize(frame, (320, 240))
        # Hozirgi vaqtni olish va chiqarish
        from datetime import datetime
        now = datetime.now()
        time_str = now.strftime('%H:%M:%S.%f')[:-3]  # soat:minut:sekund.millisekund
        cv2.putText(frame, time_str, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)
        frames.append(frame)

    top = np.hstack((frames[0], frames[1]))
    bottom = np.hstack((frames[2], frames[3]))
    grid = np.vstack((top, bottom))

    cv2.imshow('4 Camera Grid', grid)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

for cap in caps:
    cap.release()
cv2.destroyAllWindows()
