import json
import ffmpy
from imageio_ffmpeg import get_ffmpeg_exe
import os
import boto3

lambda_client = boto3.client("lambda")

def lambda_handler(event, context):
    # TODO implement
    
    s3_client = boto3.client("s3")
    s3_bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    bucket = "outputvideocse291"
    
    url = s3_client.generate_presigned_url('get_object', 
                                    Params = {'Bucket': s3_bucket, 'Key': key}, 
                                    ExpiresIn = 6000)
    input = {
        "url": url
    }
    resp = lambda_client.invoke(
        # the test-del function refers to the check-validity.py file
        FunctionName = 'arn:aws:lambda:us-west-2:072775118116:function:test-del',
        InvocationType = 'RequestResponse',
        Payload = json.dumps(input)
        )
    response = json.load(resp['Payload'])
    print(response)
    crf_parameter = 35
    output_video_codec = "libx264"
    FFMPEG_BINARY = os.getenv("FFMPEG_BINARY", "ffmpeg-imageio")
    
    if FFMPEG_BINARY == "ffmpeg-imageio":
        os.environ["FFMPEG_BINARY"] = FFMPEG_BINARY
        FFMPEG_BINARY = get_ffmpeg_exe()
        
        print(FFMPEG_BINARY)
        ffmpeg_output_parameters = (
            "-vcodec " + output_video_codec + " -crf " + str(crf_parameter)
        )
        ff = ffmpy.FFmpeg(
            executable=FFMPEG_BINARY,
            inputs={url: "-y -hide_banner -nostats -loglevel panic"},
            outputs={"/tmp/output_{}".format(key): ffmpeg_output_parameters},
        )
        try:
            p1 = ff.run()
            s3_client.upload_file("/tmp/output_{}".format(key), bucket, key)
            return {'statusCode': 200,
                'body': json.dumps('Hello from Lambda! Inside try')
            }
        except Exception as e:
            print("Error = ", e)
            return {'statusCode': 400,
                'body': json.dumps('Exception')
            }
       
    else:
        print("Error")
    
    return {
        'statusCode': 200,
        'body': json.dumps('End of func')
    }
