import cv2
import os 
import datetime
ipList=os.environ['IPLIST']
ips=ipList.split(',')
getCertUrl=ps.environ['GET_CERT_URL']

from urllib3 import encode_multipart_formdata
import sys
import requests

def savePic(rtsp):       
    cap = cv2.VideoCapture(rtsp)
    if cap.isOpened():
        ret, frame = cap.read()
        if ret==True:
            cv2.imwrite(ip.replace('.','')+'.jpg',frame)

def getCertificate():
    data = {
        orgId='',
        queryDate='',
        equipmentSn=''
    }
    r = requests.post(getCertUrl,data = data)
    result =r.json()
    url = result['returnData']['url']
    
    
def uploadImage():
    
    

def main(test=False):
    while True:
        now = datetime.datetime.now()
        if now.second == 0:
        #if now.hour == 18 and now.minute==0 and now.second==0
            print(now.hour)
            print(now.minute)
            for ip in ips:
                rtsp = 'rtsp://admin:a123456789@%s/Streaming/Channels/101' % ip
                savePic(rtsp)
                
                getToken(getCertificate)
            for ip in ips:
                uploadImage()
                
                        
                       
if __name__ == '__main__':
    main()

 
