# -*- coding: utf-8 -*-

import boto3
from ring_doorbell import Ring, Auth
import json
from pathlib import Path
from oauthlib.oauth2 import MissingTokenError
from moviepy.editor import VideoFileClip
from datetime import datetime
CACHE_FILE_NAME="/tmp/token.cache"
TEMP_VIDEO_NAME="/tmp/last_trigger.mp4"
cache_file=Path("/tmp/token.cache")
BUCKET_NAME="<INSERT BUCKET NAME HERE>"
VIDEO_FRAME_NAME="/tmp/video_frame.png"
dynamoDBTable="<INSERT DYNAMODB TABLE NAME HERE>"

rekognition=boto3.client('rekognition')

def getCacheFileFromBucket(bucketname,filename):
    s3=boto3.resource('s3')
    s3.Bucket(bucketname).download_file(filename,CACHE_FILE_NAME)

def uploadCacheFileToBucket(bucketname,filename,emailname):
    s3=boto3.client('s3')
    s3.upload_file(filename,bucketname,emailname)

def getlabels(bucket,key):
    labelresponse = rekognition.detect_labels(
    Image={
    'S3Object':{
    'Bucket':bucket,
    'Name':key
    }
    },
    MaxLabels=3,
    MinConfidence=80.0
    )
    return labelresponse


def getfaces(bucket,key):
    response = rekognition.detect_faces(
    Image={
        'S3Object': {
            'Bucket':bucket,
            'Name': key,

        }
    },
    Attributes=[
        'ALL',
    ]
)
    return response


def gettext(bucket,key):
    #response = rekognition.detect_text(
    #Image={

    #    'S3Object': {
    #        'Bucket': bucket,
    #        'Name': key,

    #    }
    #}
#)
    response = {}
    return response

def getleftorright(leftvalue):
    if leftvalue < .15:
        return "Leftmost"
    elif leftvalue >=.15 and leftvalue< .4:
        return "Left"
    elif leftvalue >.6 and leftvalue <=.85:
        return "Right"
    elif leftvalue > .85:
        return "Rightmost"
    else:
        return "Center"


def gettoporbottom(topvalue):
    if topvalue < .15:
        return "Top"
    elif topvalue >=.15 and topvalue< .4:
        return "Upper"
    elif topvalue >.6 and topvalue <=.85:
        return "Lower"
    elif topvalue > .85:
        return "Bottom"
    else:
        return "Center"


def getLatestMotionVideo(devices):

    doorbell=devices['doorbots'][0]
    doorbell.recording_download(
    doorbell.history(limit=100, kind='motion')[0]['id'],
                     filename=TEMP_VIDEO_NAME,
                     override=True)

def getFrameFromVideo():
    clip=VideoFileClip("/tmp/last_trigger.mp4")
    clip.save_frame(VIDEO_FRAME_NAME,t=0.75,withmask=True)
    uploadCacheFileToBucket(BUCKET_NAME,VIDEO_FRAME_NAME,"video_frame.png")

def addImageInfotoTable(labelresponse, textresponse, facesresponse):
    dynamodb = boto3.client('dynamodb')
    facedict={}
    labeldict={}
    textdict={}
    counter=1
    for face in facesresponse['FaceDetails']:
        if 'BoundingBox' in face.keys():
            topstring=gettoporbottom(face['BoundingBox']['Top'])
            leftstring = getleftorright(face['BoundingBox']['Left'])
            locationstring = topstring + " " + leftstring
            facedict["faces"+str(counter)]={
            "M":{

            "Location":{"S":str(locationstring)},
            "ageLow":{"N":str(face['AgeRange']['Low'])},
            "ageHigh":{"N":str(face['AgeRange']['High'])},
            "genderValue":{"S":str(face['Gender']['Value'])},
            "genderConf":{"N":str(face['Gender']['Confidence'])},
            "emotion":{"S":str(face['Emotions'][0]['Type'])},
            "emotionConf":{"N":str(face["Emotions"][0]['Confidence'])}
            }
            }
            counter +=1
    counter = 1
    for label in labelresponse['Labels']:
        for instance in label['Instances']:
            if 'BoundingBox' in instance.keys():
                topstring=gettoporbottom(instance['BoundingBox']["Top"])
                leftstring=getleftorright(instance['BoundingBox']["Left"])
                locationstring = topstring + " " + leftstring
                labeldict["labels"+str(counter)]={"L":[{"S":str(label['Name'])},{"S":str(locationstring)}]}
                counter +=1
    counter = 1

    currenttime="123"
    dynamodb.put_item(
    TableName=dynamoDBTable,
    Item={
    'id':{
    'N':"1"

    },
    'timestamp':{
    'N':currenttime
    },
    'FaceDict':{
    'M':facedict

    },
    'LabelDict':{
    'M':labeldict

    },
    'TextDict':{
    'M':textdict
    }
    }
    )


def token_updated(token):
    cachefile=open(CACHE_FILE_NAME,"w")
    cachefile.write(json.dumps(token))
    cachefile.close()

def ringOperations(emailname):
    s3=boto3.client('s3')
    getCacheFileFromBucket(BUCKET_NAME,emailname)

    if cache_file.is_file():
        cachefile=open(CACHE_FILE_NAME,"r")
        tokendata=json.loads(cachefile.read())
        cachefile.close()
        auth = Auth("MyProject/1.0", tokendata, token_updated)
        uploadCacheFileToBucket(BUCKET_NAME,CACHE_FILE_NAME,emailname)

    ring = Ring(auth)
    ring.update_data()

    devices = ring.devices()

    getLatestMotionVideo(devices)
    getFrameFromVideo()
    sourceKey="video_frame.png"
    imagelabels=getlabels(BUCKET_NAME,sourceKey)
    imagefaces=getfaces(BUCKET_NAME,sourceKey)
    imagetext=gettext(BUCKET_NAME,sourceKey)
    addImageInfotoTable(imagelabels, imagetext, imagefaces)

    s3.delete_object(
    Bucket=BUCKET_NAME,
    Key=sourceKey
    )
    s3.delete_object(
    Bucket=BUCKET_NAME,
    Key="last_trigger.mp4"
    )


def handler(event, context):
    statuscode=200
    bodydata=None
    email = event.get('email')
    ringOperations(email)
    bodydata=json.dumps({
                'returndata' : "success",
                'successcode':'0'
            })
    finalresponse={}
    finalresponse["headers"]={
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*'
    }
    finalresponse['statusCode']=statuscode
    finalresponse['body']=bodydata
    return finalresponse
