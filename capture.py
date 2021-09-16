import cv2
import os 
import datetime
cameraList=os.environ['CAMERA_LIST']
cameras=cameraList.split(',')
camera_arr = []
for camera in cameras:
    camera_arr.append({
    'ip':camera.split('#')[0],
    'equipSn':camera.split('#')[1]    
    })
    
getCertUrl = os.environ['GET_CERT_URL']
collectDataUrl = os.environ['COLLECT_DATA_URL']
orgId=os.environ['ORG_ID']

from urllib3 import encode_multipart_formdata
import sys
import requests

def savePic(rtsp,equipSn):       
    cap = cv2.VideoCapture(rtsp)
    if cap.isOpened():
        ret, frame = cap.read()
        if ret==True:
            cv2.imwrite(equipSn+'.jpg',frame)
            
def getCertificate(equipSn):
    data = {
        'orgId':orgId,
        'queryDate':datetime.datetime.now().strftime( "%Y-%m-%d %H:%M:%S" ),
        'equipmentSn':equipSn
    }
    r = requests.post(getCertUrl,data = data)
    result =r.json()
    url = result['returnData']['url']
    return url
    
def uploadImage(equipSn):
    upload_url  = getCertificate(equipSn)
    data = {'file':("file", open(equipSn+'.jpg','rb').read())}
    encode_data = encode_multipart_formdata(data)
    data = encode_data[0]
    headers = {
      "content-Type":encode_data[1]
    }
    print(datetime.datetime.now().strftime( "%Y-%m-%d %H:%M:%S" )+'start upload')
    r = requests.post(upload_url,headers=headers,data=data,timeout=10)
    result = r.json()
    if result['responseCode']=='000000':
        print(datetime.datetime.now().strftime( "%Y-%m-%d %H:%M:%S" )+'finish upload')
        return result['data']['docId']
    else:
        return False
    
def collectData(equipSn,print_time,print_fileId):
    query = {
        'networkNo':orgId,
        'equipSn':equipSn,
        'printTime':print_time,
        'printFileId':print_fileId
    }
    
    impressInfoStr = json.dumps(query)
    
    data ={
      'orgId':orgId,
      'impressInfoStr':impressInfoStr
    }
    
    r = requests.post(collectDataUrl,data = data)
    result =r.json()
    print('collect Data return:',result)
    if result['returnData']=='success':
        collectDataUrl

def main():
    while True:
        now = datetime.datetime.now()
        if now.second == 0:
        #if now.hour == 18 and now.minute==0 and now.second==0
            print(now.hour)
            print(now.minute)
            for camera in camera_arr:
                ip = camera['ip']
                print_time = datetime.datetime.now().strftime( "%Y-%m-%d %H:%M:%S" )
                rtsp = 'rtsp://admin:a123456789@%s/Streaming/Channels/101' % ip
                savePic(rtsp,camera['equipSn'])
                print_fileId = uploadImage(camera['equipSn'])
                if print_fileId==False:
                    for i in range(2):
                        print_fileId = uploadImage(camera['equipSn'])
                if print_fileId!=False:
                    collectDataUrl(camera['equipSn'],print_time,print_fileId)
                else:
                    print('cannot upload image,camera ip=',camera['ip'])
                        
if __name__ == '__main__':
    main()

 
