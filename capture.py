import cv2
import os 
import datetime
ipList=os.environ[IPLIST]
ips=ipList.split(',')
while True:
    now = datetime.datetime.now()
    if now.hour == 18 and now.minute = 0 
      #TODO request
      print(now.hour)
      print(now.minute)
      for ip in ips:
          rtsp = 'rtsp://admin:1234567a@%s/Streaming/Channels/101' % ip
          cap = cv2.VideoCapture(rtsp)
          if cap.isOpened():
              ret, frame = cap.read()
              if ret==True:
                  cv2.imshow(frame)
                  cv2.waitKey(1)
          
 
