import cv2
import os 
import datetime
import json
from urllib.request import urlretrieve

#face_lib_config
#HOUR_list_face = os.environ['HOUR_FACE'].split(',')
#HOURS_face = [int(i) for i in HOUR_list]
#MINUTE_face = int(os.environ['MINUTE_FACE'])
#face_token = os.environ['FACE_TOKEN']
#getFaceListUrl = os.environ['GET_FACE_LIST_URL']
#aibee interface
#getGroupUrl = os.environ['AIBEE_HOST_URL']+'/users/v1/list-user'
#updateFaceUrl = os.environ['AIBEE_HOST_URL']+'/users/v1/add'
#deleteFaceUrl = os.environ['AIBEE_HOST_URL']+'/users/v1/remove-image'

#face_list = []
#face_list['wangshengyu345']={'imageUrl':'','updatedTime':'',"isUm":""}

#wangdian_capture_config
#HOUR_list = os.environ['HOUR'].split(',')
#HOURS = [int(i) for i in HOUR_list]
#MINUTE = int(os.environ['MINUTE'])

run_env = os.environ['RUN_ENV']
RTSP_KEY = os.environ['RTSP_KEY']
if run_env == 'PRD':
    verify = True
else:
    verify = False
    
cameraList=os.environ['CAMERA_LIST']
cameras=cameraList.split(',')
camera_arr = []
for camera in cameras:
    print(camera)
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
        else:
            print('ret=',ret)
    else:
        print('cap is not opened')
            
def getCertificate(equipSn):
    data = {
        'orgId':orgId,
        'queryDate':datetime.datetime.now().strftime( "%Y-%m-%d %H:%M:%S" ),
        'equipmentSn':equipSn
    }
    r = requests.post(getCertUrl,data = data, verify=verify)
    #print(r.text)
    result =json.loads(r.text)
    url = result['returnData']['url']
    return url
    
def uploadImage(equipSn):
    upload_url  = getCertificate(equipSn)
    weFileToken = upload_url.split('&weFileToken=')[1]
    upload_url=upload_url.split('&weFileToken=')[0]
    data = {'file':("file", open(equipSn+'.jpg','rb').read()),
            'isCover':1,
            'fileName':equipSn+'.jpg',
            'weFileToken':weFileToken
            }
    encode_data = encode_multipart_formdata(data)
    data = encode_data[0]
    headers = {
      "content-Type":encode_data[1]
    }
    print(datetime.datetime.now().strftime( "%Y-%m-%d %H:%M:%S" )+'start upload')
    r = requests.post(upload_url,headers=headers,data=data,timeout=10, verify=verify)
    result =json.loads(r.text)
    if result['responseCode']=='000000':
        print(datetime.datetime.now().strftime( "%Y-%m-%d %H:%M:%S" )+'finish upload')
        return result['data']['fileId']
    else:
        return False
    
def collectData(query):
    query = ','.join(query)
    impressInfoStr = '['+query+']'
    
    data ={
      'orgId':orgId,
      'impressInfoStr':impressInfoStr
    }

    r = requests.post(collectDataUrl,json=data,verify=verify)
    print('collectData returned')
    result =json.loads(r.text)
    return result['returnData']

def main():
    query = []
    for camera in camera_arr:
        ip = camera['ip']
        print('start get picture from ip:',ip)
        print_time = datetime.datetime.now().strftime( "%Y-%m-%d %H:%M:%S" )
        rtsp = 'rtsp://admin:'+RTSP_KEY+'@%s/Streaming/Channels/101' % ip
        try:
            savePic(rtsp,camera['equipSn'])
        except Exception as e:
            print(e)
            print('cannot capture image',camera['ip'])
        try:
            print_fileId = uploadImage(camera['equipSn'])

            if print_fileId==False:
                print_fileId = uploadImage(camera['equipSn'])
            if print_fileId!=False:
                query.append(json.dumps({
                    'networkNo':orgId,
                    'equipSn':camera['equipSn'],
                    'printTime':print_time,
                    'printFileId':print_fileId
                }))
            print('finished get picture from ip:',ip)
        except Exception as e:
            print(e)
            print('cannot upload image',camera['ip'])
    try:    
        result = collectData(query)
        if result=='success':
            print('!!!!!!!!!!!!!!!!done upload all images once')
        else:
            result = collectData(query)
            if result=='success':
                print('!!!!!!!!!!!!!!!!done upload all images once')
            else:
                print('cannot collect data')
    except Exception as e:
        print(e)
        print('cannot collect data')
                                           
if __name__ == '__main__':
    main()
