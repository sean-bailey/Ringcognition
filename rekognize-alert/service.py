# -*- coding: utf-8 -*-
from __future__ import print_function
import random
import boto3
TABLE_NAME="ringkognition-table"
SNS_TOPIC_ARN="<INSERT SNS TOPIC ARN HERE>"
from datetime import datetime


def getAge():
    dynamodb=boto3.client('dynamodb')
    mydata=dynamodb.scan(TableName=TABLE_NAME)
    facedict=mydata['Items'][0]["FaceDict"]
    tectdict=mydata['Items'][0]["TextDict"]
    labeldict=mydata['Items'][0]["LabelDict"]
    finalstringresponse=""
    card_title="Get Age"
    counter = 1

    if len(facedict['M'])>0:


        for face in facedict['M']:
            stringcounter = ""
            agelow=facedict['M'][face]['M']['ageLow']['N']
            agehigh=facedict['M'][face]['M']['ageHigh']['N']
            location=facedict['M'][face]['M']['Location']['S']
            gendervalue=facedict['M'][face]['M']['genderValue']['S']
            if counter == 1:
                stringcounter = "1st"
            elif counter == 2:
                stringcounter = "2nd"
            elif counter == 3:
                stringcounter ="3rd"
            else:
                stringcounter = str(counter)+"th"
            counter+=1
            finalstringresponse = finalstringresponse + "The "+str(stringcounter)+" "+str(gendervalue)+" in the "+str(location)+" appears to be between "+str(agelow)+" and "+str(agehigh)+" years old. "
    else:
        finalstringresponse=""
    return finalstringresponse

def getLabels():
    dynamodb=boto3.client('dynamodb')
    mydata=dynamodb.scan(TableName=TABLE_NAME)
    facedict=mydata['Items'][0]["FaceDict"]
    tectdict=mydata['Items'][0]["TextDict"]
    labeldict=mydata['Items'][0]["LabelDict"]
    stringcounter = ""
    finalstringresponse=""
    card_title="What's up in this picture"
    counter = 1
    if len(labeldict['M'])>0:

        for label in labeldict['M']:
            seenobject=labeldict['M'][label]['L'][0]['S']
            objectlocation=labeldict['M'][label]['L'][1]['S']
            if counter == 1:
                stringcounter = "1st"
            elif counter == 2:
                stringcounter = "2nd"
            elif counter == 3:
                stringcounter ="3rd"
            else:
                stringcounter = str(counter)+"th"
            counter+=1
            finalstringresponse = finalstringresponse + "There is a "+str(seenobject)+ " in the "+str(objectlocation)+ " of the image. "
    else:
        finalstringresponse="There was nothing detected in the image."
    return finalstringresponse

def getEmotion():
    dynamodb=boto3.client('dynamodb')
    mydata=dynamodb.scan(TableName=TABLE_NAME)
    facedict=mydata['Items'][0]["FaceDict"]
    tectdict=mydata['Items'][0]["TextDict"]
    labeldict=mydata['Items'][0]["LabelDict"]
    finalstringresponse=""
    card_title="Get Emotional Sentiment"
    counter = 1
    if len(facedict['M'])>0:
        for face in facedict['M']:
            stringcounter = ""
            emotion=facedict['M'][face]['M']['emotion']['S']
            emotconf=facedict['M'][face]['M']['emotionConf']['N'][:4]
            location=facedict['M'][face]['M']['Location']['S']
            gendervalue=facedict['M'][face]['M']['genderValue']['S']
            if counter == 1:
                stringcounter = "1st"
            elif counter == 2:
                stringcounter = "2nd"
            elif counter == 3:
                stringcounter ="3rd"
            else:
                stringcounter = str(counter)+"th"
            counter+=1
            finalstringresponse = finalstringresponse + "The "+str(stringcounter)+" "+str(gendervalue)+" in the "+str(location)+" appears to be "+str(emotion)+", and I am " +str(emotconf) + " percent sure on that. "
    else:
        finalstringresponse=""
    return finalstringresponse

def getText():
    dynamodb=boto3.client('dynamodb')
    mydata=dynamodb.scan(TableName=TABLE_NAME)
    print(mydata)
    facedict=mydata['Items'][0]["FaceDict"]
    textdict=mydata['Items'][0]["TextDict"]
    labeldict=mydata['Items'][0]["LabelDict"]
    stringcounter = ""
    finalstringresponse=""
    card_title="What's up in this picture"
    counter = 1
    if len(textdict['M']) > 0:
        for text in textdict['M']:
            transcription=textdict['M'][text]['L'][0]['S']
            objectlocation=textdict['M'][text]['L'][1]['S']
            if counter == 1:
                stringcounter = "1st"
            elif counter == 2:
                stringcounter = "2nd"
            elif counter == 3:
                stringcounter ="3rd"
            else:
                stringcounter = str(counter)+"th"
            counter+=1
            finalstringresponse = finalstringresponse + "There is a "+str(transcription)+ " in the "+str(objectlocation)+ " of the image. "
    else:
        finalstringresponse=""
    return finalstringresponse

def handler(event, context):
    # Your code goes here!
    agestring = getAge()
    labelstring=getLabels()
    emotionstring=getEmotion()
    textstring=getText()
    subject = "Motion Digest from Ring Motion Alert at "+str(datetime.now())
    message = agestring + " " + labelstring + " " + emotionstring + " " + textstring
    client=boto3.client('sns')
    client.publish(
    TargetArn=SNS_TOPIC_ARN,
    Message=message,
    Subject=subject
    )
