import json
import boto3
import cv2
import tempfile

def lambda_handler(event, context):
    # TODO implement
    key = "Tidead.mp4"
    url = event["url"]
    try:
        vid = cv2.VideoCapture(url)
        if vid.isOpened():
            # Making sure we can read at least two frames from video
            ret, frame = vid.read()
            ret, frame = vid.read()
            # Making sure video frame is not empty
            if frame is not None:
                print("frame is read")
                return {
                    'value': "True",
                    'function': "hello from checkvalid"
                }
            else:
                return {
                    'value': "False",
                }
        else:
            return {
                    'value': "False",
                }
    except Exception as e:
        return {
            'value': "False",
    }
