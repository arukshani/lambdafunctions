import json
import boto3
import cv2
import tempfile

def lambda_handler(event, context):
    # TODO implement
    print(event)
    s3_client = boto3.client("s3")
    # s3_bucket=event['Bucket']
    s3_bucket=event['detail']['bucket']['name']
    # key = event['key']
    key = event['detail']['object']['key']
    url = s3_client.generate_presigned_url('get_object', Params = {'Bucket': s3_bucket, 'Key': key}, ExpiresIn = 6000)
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
                    'Bucket':s3_bucket,
                    "key":key
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
            "except":"except"
    }
