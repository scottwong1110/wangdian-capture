import cv2
import os 
import datetime
ipList=os.environ['IPLIST']
ips=ipList.split(',')

def main():
    while True:
        now = datetime.datetime.now()
        if now.second == 0:
        #if now.hour == 18 and now.minute==0 and now.second==0
            print(now.hour)
            print(now.minute)
            for ip in ips:
                rtsp = 'rtsp://admin:a123456789@%s/Streaming/Channels/101' % ip
                cap = cv2.VideoCapture(rtsp)
                if cap.isOpened():
                    ret, frame = cap.read()
                    if ret==True:
                        cv2.imshow(frame)
                        cv2.waitKey(1)
                       
if __name__ == '__main__':
    main()

 
