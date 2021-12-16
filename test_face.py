import cv2
import os 
import datetime
import json
from urllib.request import urlretrieve
import time
import base64
import hashlib

api_key = "Ne3XyaDSGWzkP120teh5rErB1dfIipMg"
api_secret = "6xz2hfoBAT7t1quppM0md3awg17xpOI5"

def sign(method=None, body=None, api_key=None, api_secret=None):
    current_timestamp = int(time.time())
    sha_1 = hashlib.sha1()
    sign_str = None
    if method.lower() in ('put', 'post'):
        sha_1.update('{}{}{}'.format(body, current_timestamp, api_secret).encode())
        sign_str = sha_1.hexdigest()
    return {
        'Aibee-Auth-ApiKey': api_key,
        'Aibee-Auth-Sign': sign_str,
        'Aibee-Auth-Timestamp': str(current_timestamp)
    }

def get_image_base64(ipath):
    base64_result = None
    with open(ipath, 'rb') as f:
        base64_result = base64.b64encode(f.read())
    return base64_result.decode("utf-8")

#face_lib_config
#HOUR_list_face = os.environ['HOUR_FACE'].split(',')
#HOURS_face = [int(i) for i in HOUR_list]
#MINUTE_face = int(os.environ['MINUTE_FACE'])
face_token = os.environ['FACE_TOKEN']
getFaceListUrl = os.environ['GET_FACE_LIST_URL']
#aibee interface
getGroupUrl = os.environ['AIBEE_HOST_URL']+'/groups/v1/list-user'
updateFaceUrl = os.environ['AIBEE_HOST_URL']+'/users/v1/add'
deleteFaceUrl = os.environ['AIBEE_HOST_URL']+'/users/v1/remove-image'

#face_list['wangshengyu345']={'downloadUrl':'','updatedDate':'',"isUm":""}

#wangdian_capture_config
#HOUR_list = os.environ['HOUR'].split(',')
#HOURS = [int(i) for i in HOUR_list]
#MINUTE = int(os.environ['MINUTE'])

run_env = os.environ['RUN_ENV']
#RTSP_KEY = os.environ['RTSP_KEY']
if run_env == 'PRD':
    verify = True
else:
    verify = False
    
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

def updateFace(um,face_obj):
    image_base64 = get_image_base64(os.path.join('face_pic',um+'.jpg'))
    data = {
        "user":{
            'user_id':um.strip(),
            #need to change to download from edge
            #'image':image_base64
            'image_url': face_obj['downloadUrl'],
            #'image_url':'https://gimg2.baidu.com/image_search/src=http%3A%2F%2Fhbimg.b0.upaiyun.com%2F8434dd571149b56667991898e2004376212d8267169b3-P2VD0B_fw236&refer=http%3A%2F%2Fhbimg.b0.upaiyun.com&app=2002&size=f9999,10000&q=a80&n=0&g=0n&fmt=jpeg?sec=1642149033&t=9e8bdb2249ae71015b39f669a8dfb85e'
        },
        "groups":[
            run_env
        ]
    }
    body = json.dumps(data)
    print('body:',flush=True)
    print(body,flush=True)
    sign_header = sign(method='post', body=body, api_key=api_key, api_secret=api_secret)
    sign_header["Content-Type"] = "application/json"
    print(sign_header,flush=True)
    r = requests.post(updateFaceUrl,data=body,headers = sign_header)
    print(r.text,flush=True)
    
    result =json.loads(r.text)
    if result['error_no']==0:
        print('update face pic successfully!,um='+um)

def deleteFace(um):
    data = {
        "user_id":um.strip(),
        "group_id":run_env
    } 
    print('deleteFace')
    body = json.dumps(data)
    sign_header = sign(method='post', body=body, api_key=api_key, api_secret=api_secret)
    sign_header["Content-Type"] = "application/json"
    r = requests.post(deleteFaceUrl,data=body,headers = sign_header)
    print(r.text,flush=True)
    result =json.loads(r.text) 
    if result['error_no']==0:
        print('delete face pic successfully!,um='+um)


def saveFacePic(um,imageUrl):
    urlretrieve(imageUrl, os.path.join('face_pic',um+'.jpg'))  

def getRunningFaceList(group_id):
    face_list={}
    data = {
        "group_id":group_id,
        "page":1,
        "page_size":1000
    } 
    body = json.dumps(data)
    sign_header = sign(method='post', body=body, api_key=api_key, api_secret=api_secret)
    sign_header["Content-Type"] = "application/json"
    r = requests.post(getGroupUrl,data=body,headers = sign_header)
    #print(r.text,flush=True)
    result =json.loads(r.text) 
    if result['error_no']==0:
        for i in range(len(result['data']['list'])):
            face_list[result['data']['list'][i]['user_id']]={'image_urls':result['data']['list'][i]['image_urls']}
        #print('face_list=',face_list,flush=True)
    return face_list
        

def getBranchFaceListAndUpdate(orgId):
    #get current aibee facelist
    face_list = getRunningFaceList(run_env)
    data = {
        'branchNo':orgId,
        'token':face_token
    }
    r = requests.post(getFaceListUrl,data = data, verify=verify)
    #print(r.text,flush=True)
    result =json.loads(r.text)
    print('printed every person',flush=True)
    updatedDate = 0
    for data in result['data']:
        if data['status']=='1':
            print('person already deleted')
        else:
            print(data,flush=True)
            newUm = data['staffId'] 
            print('newUm=',newUm,flush=True)
            #ADD
            newface = {'downloadUrl':data['downloadUrl'],'updatedDate':data['updatedDate']}
            #save picture and update
            saveFacePic(newUm,data['downloadUrl'])
            updateFace(newUm,newface)
            
            #else:
            #    #need modify,update person
            #    if data['updatedDate'] > face_list[newUm]['updatedDate']:
            #        newface = {'downloadUrl':data['downloadUrl'],'updatedDate':data['updatedDate']}
            #        #save picture and update
            #        saveFacePic(newUm,data['downloadUrl'])
            #        updateFace(newUm,newface)
    #need delete
    for key in face_list:
        delete = 1
        for data in result['data']:
            #person deleted 
            if data['status']=='1':
                print('person already deleted')    
            else:
                if data['staffId'] == key:
                    delete = 0
        if delete == 1:
            deleteFace(key)
    

    #show running face list
    face_list = getRunningFaceList(run_env)
    print('face_list=',face_list,flush=True)
    #return faceList

def main():
    while True:
        #try :
        getBranchFaceListAndUpdate(orgId)
        #except Exception as e:
        #    print('error from getBranchFaceList',flush=True)
        #    print(e,flush=True)
        time.sleep(20)

                                           
if __name__ == '__main__':
    main()
