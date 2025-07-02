import cv2

rtsp_url = ''


cap = cv2.VideoCapture(rtsp_url)
cv2.setLogLevel(cv2.LOG_LEVEL_VERBOSE)
if not cap.isOpened():
    print('RTSP oqimi ochilmadi! Kamera yoki link ishlamayapti.')
else:
    ret, frame = cap.read()
    if ret:
        print('RTSP oqimi ishlayapti!')
    else:
        print('RTSP oqimi ochildi, lekin kadr olinmadi.')
cap.release()