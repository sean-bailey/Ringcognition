# Ringcognition
This repository contains the files for the Ringkognition project

#rekognize-alert
- Contains the python-lambda formatted service for lambda for the SNS based alert service for Ringkognition

#rekognize-service
- Contains the python-lambda formatted service for lambda for the processing of video clips from Ring

This is an extensive DIY project which aims to solve the main problem I had with Ring:
_You have to look at the videos to see what is going on_.

What if there were a way to get a quick message via text or email that told you what
happened? That way you wouldn't have to check your Ring alert each time a car passed
or a person walked down the sidewalk. And if the information is important, you
could easily get detailed information about what was seen in a quickly read
text format.

I'm going to leverage AWS Rekogntion to do the power lifting in this case.

This project will leverage DynamoDB, Lambda, Rekognition, S3, SNS and API Gateway.

Oh and of course, Ring.

This Readme will cover all the steps required to get the end-to-end system set up.
*This is not for the faint of heart!* While in the future I aim to make this easy
to do, as it stands right now there are many steps which you must do manually.


First, you'll need to get your AWS and Ring credentials set up. I'm going to assume
you have a Ring account and an AWS account.

Go here https://github.com/tchellomello/python-ring-doorbell and install the library for Python.

<generate code here> WIP
