import json
import ffmpy
from imageio_ffmpeg import get_ffmpeg_exe
import os
import boto3
def lambda_handler(event, context):
    # TODO implement
    
    s3_client = boto3.client("s3")
    s3_resource=boto3.resource("s3")
    s3_bucket=event['Bucket']
    key=event['key']
    bucket="outputvideocse291"
    url = s3_client.generate_presigned_url('get_object',Params = {'Bucket': s3_bucket, 'Key': key}, ExpiresIn = 6000)
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
            outputs={"/tmp/output_{}".format(event['key']): ffmpeg_output_parameters},
        )
        try:
            ff.run()
            with open("/tmp/output_{}".format(event['key']), 'rb') as file:
                s3_resource.Bucket(bucket).put_object(Key=key, Body=file)
            return {'statusCode': 200,
                'body': json.dumps('Hello from Lambda! Inside try')
            }
        except Exception as e:
            print(e)
            return {'statusCode': 400,
                'body': json.dumps('Exception')
            }
       
    else:
        print("Error")
    
    return {
        'statusCode': 200,
        'body': json.dumps('End of func')
    }
