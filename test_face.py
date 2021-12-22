import cv2
import os 
import datetime
import json
from urllib.request import urlretrieve
import time
import base64
import hashlib
from PIL import Image

def get_size(file):
    # 获取文件大小:KB
    size = os.path.getsize(file)
    return size / 1024

def compress_image(infile, mb=1024, step=10, quality=80):
    """不改变图片尺寸压缩到指定大小
    :param infile: 压缩源文件
    :param outfile: 压缩文件保存地址
    :param mb: 压缩目标，KB
    :param step: 每次调整的压缩比率
    :param quality: 初始压缩比率
    :return: 压缩文件地址，压缩文件大小
    """
    #if outfile is None:
    #    outfile = infile
    o_size = get_size(infile)
    if o_size <= mb:
        im = Image.open(infile)
        im.save(infile)

    while o_size > mb:
        im = Image.open(infile)
        im.save(infile, quality=quality)
        if quality - step < 0:
            break
        quality -= step
        o_size = get_size(infile)

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
deleteFaceUrl = os.environ['AIBEE_HOST_URL']+'/users/v1/remove-group'
deleteImageUrl = os.environ['AIBEE_HOST_URL']+'/users/v1/remove-image'
api_key = os.environ['API_KEY']
api_secret = os.environ['API_SECRET']

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

def updateFace(um,face_obj,pic_base64):
    data = {
        "user":{
            'user_id':um.strip(),
            #need to change to download from edge
            'image':pic_base64
            #'image_url': face_obj['downloadUrl']
        },
        "groups":[
            run_env
        ]
    }
    body = json.dumps(data)
    sign_header = sign(method='post', body=body, api_key=api_key, api_secret=api_secret)
    sign_header["Content-Type"] = "application/json"
    r = requests.post(updateFaceUrl,data=body,headers = sign_header)
    print('update response')
    print(r.text,flush=True)
    
    result =json.loads(r.text)
    if result['error_no']==0:
        print('update face pic successfully!,um='+um)
    else:
        r = requests.post(updateFaceUrl,data=body,headers = sign_header)
        print('update response')
        print(r.text,flush=True)
        result =json.loads(r.text)
        if result['error_no']==0:
            print('update face pic successfully!,um='+um)

def deleteFace(um,image_urls):
    for image_url in image_urls:
        data = {
           "user_id":um.strip(),
           "image_url": image_url
        }

        body = json.dumps(data)
        sign_header = sign(method='post', body=body, api_key=api_key, api_secret=api_secret)
        sign_header["Content-Type"] = "application/json"
        r = requests.post(deleteImageUrl,data=body,headers = sign_header)
        print('delete response')
        print(r.text,flush=True)
        result =json.loads(r.text) 
        if result['error_no']==0:
            print('delete face Image pic successfully!,um='+um)
    
    data = {
        "user_id":um.strip(),
        "group_id":run_env
    } 
    body = json.dumps(data)
    sign_header = sign(method='post', body=body, api_key=api_key, api_secret=api_secret)
    sign_header["Content-Type"] = "application/json"
    r = requests.post(deleteFaceUrl,data=body,headers = sign_header)
    print('delete response')
    print(r.text,flush=True)
    result =json.loads(r.text) 
    if result['error_no']==0:
        print('delete face pic successfully!,um='+um)
    else:
        r = requests.post(deleteFaceUrl,data=body,headers = sign_header)
        print('delete response')
        print(r.text,flush=True)
        result =json.loads(r.text)
        if result['error_no']==0:
            print('delete person successfully!,um='+um)


def saveFacePic(um,imageUrl):
    pic_path = os.path.join('face_pic',um+'.jpg')
    urlretrieve(imageUrl, pic_path)
    compress_image(pic_path)
    print('compressed_file_size=',flush=True)
    print(str(get_size(pic_path)),flush=True)
    return get_image_base64(pic_path)

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
    print(r.text,flush=True)
    result =json.loads(r.text) 
    if result['error_no']==0:
        if 'list' in result['data'] and type(result['data']['list'])==list:
            for i in range(len(result['data']['list'])):
                face_list[result['data']['list'][i]['user_id']]={'image_urls':result['data']['list'][i]['image_urls']}
            print('face_list=',face_list,flush=True)
        else:
            print('no one exists',flush=True)
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
    #print('printed every person',flush=True)
    updatedDate = 0
    for data in result['data']:
        if data['status']=='1' or 'staffId' not in data:
            print('person already deleted')
        else:
            print(data,flush=True)
            newUm = data['staffId'] 
            print('newUm=',newUm,flush=True)
            #ADD
            newface = {'downloadUrl':data['downloadUrl'],'updatedDate':data['updatedDate']}
            #save picture and update
            download_url = data['downloadUrl'] + '&fileId=' + data['faceImgId'] + '&suffix=jpg'
            print('download url=',download_url,flush=True)
            pic_base64 = saveFacePic(newUm,download_url)
            
            # delete all past faces
            if newUm in face_list:
                image_urls = face_list[newUm]['image_urls']
                deleteFace(newUm,image_urls)
            
            updateFace(newUm,newface,pic_base64)
            
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
            if data['status']=='1' or 'staffId' not in data:
                print('person already deleted')    
            else:
                if data['staffId'] == key:
                    delete = 0
        if delete == 1:
            deleteFace(key,face_list[key]['image_urls'])
    

    #show running face list
    face_list = getRunningFaceList(run_env)
    print('face_list=',face_list,flush=True)
    #return faceList

def main():
    getBranchFaceListAndUpdate(orgId)
    #while True:
        #try :
        #getBranchFaceListAndUpdate(orgId)
        #except Exception as e:
        #    print('error from getBranchFaceList',flush=True)
        #    print(e,flush=True)
        #time.sleep(20)

                                           
if __name__ == '__main__':
    main()
