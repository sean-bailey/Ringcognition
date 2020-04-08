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

This project will leverage DynamoDB, Lambda, Rekognition, S3, SNS, Alexa, IFTTT and API Gateway.

Oh and of course, Ring.

This Readme will cover all the steps required to get the end-to-end system set up.
*This is not for the faint of heart!* While in the future I aim to make this easy
to do, as it stands right now there are many steps which you must do manually.

Start by cloning this repo locally and `cd`ing in to it.

First, you'll need to get your AWS and Ring credentials set up. I'm going to assume
you have a Ring account and an AWS account.

Go here https://github.com/tchellomello/python-ring-doorbell and install the library for Python.

From there, `cd ./get-ring-token && python3 ring-token.py`
You'll be prompted for your email, and if this is the first time, your password
and MFA token Ring provides you. This process has to be done manually, and unfortunately it appears you've got to do it about once a month as it eventually expires.

You'll see a file which is named with your email address in the `get-ring-token` folder. That's the authentication token for Ring which is critical for this application to work!

Head over to the AWS Console and go to S3. Whip up an S3 bucket with default encryption and blocking all public access. Remember this bucket name!

Ensure that no other users have access to this bucket apart from you currently,
and upload your authentication token to it from before.

Next, you'll need to create a DynamoDB Table:

Go to DynamoDB and create a table with:
1) Primary Key of `id` and type `Number`
2) Sort Key of `timestamp` and type `Number`

Remember your database name!

You'll now need some IAM roles for your Lambda functions:

`rekognize-service-role`: This role is for the rekognize-service. It will need the AmazonRekognitionFullAccess, and CloudWatch Logs access for its function. You can retroactively apply it later. Create two policies and attach them to this role, one for DynamoDB and one for S3, for the table and the bucket you created earlier.

DynamoDB policy to attach to this role:
```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor1",
            "Effect": "Allow",
            "Action": "dynamodb:*",
            "Resource": [
                "arn:aws:dynamodb:*:136289114074:table/<your table>/stream/*",
                "arn:aws:dynamodb:*:136289114074:table/<your table>/index/*",
                "arn:aws:dynamodb:*:136289114074:table/<your table>"
            ]
        }
    ]

```

Policy for S3 to attach to this role:

```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": [
                "s3:PutEncryptionConfiguration",
                "s3:PutObject",
                "s3:GetObject",
                "s3:ListBucket",
                "s3:DeleteObject"
                ],
            "Resource": [
                "arn:aws:s3:::<your bucket name>/*",
                "arn:aws:s3:::<your bucket name>"
            ]
        },
        {
            "Sid": "VisualEditor1",
            "Effect": "Allow",
            "Action": [
                "s3:ListAllMyBuckets",
                "s3:HeadBucket"
            ],
            "Resource": "*"
        }
    ]
}

```


Next, head here:
https://github.com/nficano/python-lambda

Follow the instructions, get yourself started. You may see issues when using `mkvirtualenv`. To get around them, add the following to the end of your `~/.profile` file:

```
export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3
source `which virtualenvwrapper.sh`
```
then, in the terminal you're going to be working in, run `source ~/.profile`.
`mkvirtualenv` should be working now!

`cd` in to the `rekognize-service` directory, and examine the `config.yaml`, `event.json` and `service.py` files and fill in the appropriate information required.

Now, while in the `rekognize-service` directory, run `mkvirtualenv rekognize-service --no-site-packages`.

Once complete, run `pip3 install python-lambda`, then `pip3 install -r requirements.txt`

If everything is currently configured correctly, you should be able to now run `lambda invoke -v`, and once the function is completed, you can check the DynamoDB for the new changes the function has added to it. Neat!

Next comes building it. The bad news is that the build is far to large to upload via the Lambda API. The good news is we can side load it via an S3 bucket. Should I make it more efficient? Probably. It's on the To-do list.

`lambda deploy-s3` comes next. It will build and deploy to your AWS account as per the configuration in your `config.yaml` file.

 Once done, feel free to test it, it should populate the DynamoDB table appropriately.

###Congratulations, the core of the work is done, and you're about halfway there.###

Now for the SNS topic to leverage for alerts. Head over to SNS:

Create a new topic for SNS and add your preferred endpoints to it. Email and phone numbers work well.

Head back to IAM and create another Lambda role:


- Role for the `rekognize-alert` Lambda:
  Create a new role called `rekognize-alert-role`. Give it Access to the cloudwatch logs for the given function (can be updated retroactively), and then add the following policy:

  ```
  {
      "Version": "2012-10-17",
      "Statement": [

          {
              "Sid": "VisualEditor1",
              "Effect": "Allow",
              "Action": "sns:Publish",
              "Resource": "<YOUR SNS TOPIC ARN>"
          }
      ]
  }

  ```

Now, locally, `cd` into the `rekognize-alert` directory. `deactivate` any current virtualenv you're working on, and then `mkvirtualenv rekognize-alert --no-site-packages`.

Once in, `pip3 install python-lambda`, then examine the `config.yaml` and `service.py` files and fill in the appropriate ARN for SNS as well as the role name.

Do a `lambda invoke -v` to verify everything is functioning, then do a `lambda deploy`.

Go to DynamoDB and set a trigger for any changes in the table to invoke this lambda function.

Now, when testing your `rekognize-service` function, you should get a message of a digest of the most recent motion alert your doorbell has seen. Let's get that sent to you automatically!

Head over to API Gateway. Create a new REST Api, call it `RKNAPI`. Add a method, GET, and head over to INTEGRATION REQUEST. In there, under Mapping templates, add a content type of application/json. Put this in there:

```
{
"email":"$input.params('email')"
}
```

Save it, Go up to Actions > Enable CORS, save it, and deploy your API. Save the URL.

Time for the cool stuff. Head over to IFTTT and create an account. Once done, click on your profile and select Create.

The code is pretty simple:

For the If, Select Alexa / Say a specific phrase. Remember the phrase, this is important later, but it's probably good if its something you wouldn't say to Alexa normally.

For Then, Select Webhook. For the URL, put in your API Gateway URL, followed by
`?email=<your_email_here>`. The method is GET, and that's all that matters here. Save it.

Head on over to your Alexa application and create a Routine. Name it appropriately, and trigger it when your Ring doorbell detects motion. Add two actions:
1) Wait 1 minute and 30 seconds (this gives Ring the time to upload the video)
2) IFTTT start "your phrase here" (from before)

Save it and Enable it.

If everything is working correctly, you can now walk in front of your front door, and a minute and a half later, you'll get a message telling you the details of what the doorbell saw.

Pull requests welcome!
