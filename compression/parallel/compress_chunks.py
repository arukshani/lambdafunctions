import json
import ffmpy
from imageio_ffmpeg import get_ffmpeg_exe
import os
import boto3

def lambda_handler(event, context):
    s3_client = boto3.client("s3")
    s3_resource=boto3.resource("s3")
    crf_parameter = 35
    output_video_codec = "libx264"
    FFMPEG_BINARY = os.getenv("FFMPEG_BINARY", "ffmpeg-imageio")
    os.environ["FFMPEG_BINARY"] = FFMPEG_BINARY
    FFMPEG_BINARY = get_ffmpeg_exe()
    ffmpeg_output_parameters = (
            "-vcodec " + output_video_codec + " -crf " + str(crf_parameter)
        )
    s3_bucket = "interchunkbucket"
    s3_compressed_chunk_bucket = "compressedchunkbucket"
    # chunk_names = event['chunk_names']
    chunk = event['chunk_name']
    # video_name = event['video_name']
    # for chunk in chunk_names:
    print(chunk)
    url = s3_client.generate_presigned_url('get_object',Params = {'Bucket': s3_bucket, 'Key': chunk}, ExpiresIn = 6000)
    ff = ffmpy.FFmpeg(
        executable=FFMPEG_BINARY,
        inputs={url: "-y -hide_banner -nostats -loglevel panic"},
        outputs={"/tmp/outputcompressedchunk_{}".format(chunk): ffmpeg_output_parameters},
    )
    try:
        ff.run()
        with open("/tmp/outputcompressedchunk_{}".format(chunk), 'rb') as file:
            s3_resource.Bucket(s3_compressed_chunk_bucket).put_object(Key=chunk, Body=file)
    except Exception as e:
        print(e)
        return {'statusCode': 400,
            'body': json.dumps('Exception')
        }
        # break
    return {
        "chunk_name":chunk
    }
    