import cv2
import os 
import datetime
import json
from urllib.request import urlretrieve
import time

#face_lib_config
#HOUR_list_face = os.environ['HOUR_FACE'].split(',')
#HOURS_face = [int(i) for i in HOUR_list]
#MINUTE_face = int(os.environ['MINUTE_FACE'])
face_token = '123'
getFaceListUrl = os.environ['GET_FACE_LIST_URL']
#aibee interface
getGroupUrl = os.environ['AIBEE_HOST_URL']+'/users/v1/list-user'
updateFaceUrl = os.environ['AIBEE_HOST_URL']+'/users/v1/add'
deleteFaceUrl = os.environ['AIBEE_HOST_URL']+'/users/v1/remove-image'

face_list = []
#face_list['wangshengyu345']={'imageUrl':'','updatedTime':'',"isUm":""}

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
    data = {
        "user":{
            'user_id':um,
            'imageUrl': face_obj['imageUrl'],
        },
        "groups":[
            run_env
        ],
        "check": True
    }
    print(json.dumps(data))
    r = requests.post(updateFaceUrl,json = json.dumps(data))
    result =json.loads(r.text)
    if result['error_no']==0:
        print('update face pic successfully!,um='+um)

def deleteFace(um):
    data = {
        "user_id":um,
        "group_id":run_env
    } 
    print(json.dumps(data))
    r = requests.post(deleteFaceUrl,json = json.dumps(data))
    result =json.loads(r.text)
    if result['error_no']==0:
        print('delete face pic successfully!,um='+um)


def saveFacePic(um,imageUrl):
    urlretrieve(imageUrl, os.path.join('face_pic',um+'.jpg'))  

def getRunningFaceList(group_id):
    data = {
        "group_id":group_id
    } 
    print(json.dumps(data))
    r = requests.post(getGroupUrl,json = json.dumps(data))
    result =json.loads(r.text)
    if result['error_no']==0:
        print('group user number:'+len(result['data']['list']))
        print('group user:'+result['data']['list'])

def getBranchFaceListAndUpdate(orgId):
    data = {
        'branchNo':orgId,
        'token':face_token
    }
    r = requests.post(getFaceListUrl,data = data, verify=verify)
    print(r.text)
    result =json.loads(r.text)
    updatedTime = 0
    for data in result['data']:
        if data['status']=='0':
            newUm = data['umCode'] 
            #not existed
            if newUm not in face_list.keys():
                face_list[newUm] = {'imageUrl':data['imageUrl'],'updatedTime':data['updatedTime'],"isUm":data['isUm']}
                #save picture and update
                saveFacePic(newUm,data['imageUrl'])
                updateFace(newUm,face_list[newUm])

            else:
                #newer info
                if data['updatedTime'] > face_list[newUm]['updatedTime']:
                    face_list[newUm] = {'imageUrl':data['imageUrl'],'updatedTime':data['updatedTime'],"isUm":data['isUm']}
                    #save picture and update
                    saveFacePic(newUm,data['imageUrl'])
                    updateFace(newUm,face_list[newUm])
    #need deletion
    for key in face_list:
        delete = 1
        for data in result['data']:
            if data['status']=='0':
                if data['umCode'] == key:
                    delete = 0
        if delete == 1:
            deleteFace(key)

    #show running face list
    getRunningFaceList(run_env)

    #return faceList

    


def main():
    while True:
        try :
            getBranchFaceListAndUpdate(orgId)
        except Exception as e:
            print('error from getBranchFaceList')
            print(e)
        time.sleep(20)

                                           
if __name__ == '__main__':
    main()