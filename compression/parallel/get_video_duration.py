import json
import boto3
import cv2

def lambda_handler(event, context):
    s3_client = boto3.client("s3")
    s3_resource=boto3.resource("s3")
    s3_bucket=event['Bucket']
    key=event['key']
    url = s3_client.generate_presigned_url('get_object',Params = {'Bucket': s3_bucket, 'Key': key}, ExpiresIn = 6000)
    try:
        vid = cv2.VideoCapture(url)
        if vid.isOpened():
            # Making sure we can read at least two frames from video
            ret, frame = vid.read()
            ret, frame = vid.read()

            frame_size_in_bytes = frame.size
            fps = vid.get(cv2.CAP_PROP_FPS)
            frame_count = vid.get(cv2.CAP_PROP_FRAME_COUNT)
            
            video_duration = round((frame_count / fps), 2)
        else:
            return {
                    'value': "False",
                }
        return {
                    'value': "True",
                    'Bucket':s3_bucket,
                    "key":key,
                    "duration":video_duration
                }
    except Exception as e:
        return {
            'value': "False",
            "except":"exception in getting video duration"
    }
