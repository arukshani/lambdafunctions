import json
import ffmpy
from imageio_ffmpeg import get_ffmpeg_exe
import os
import boto3
from random import randrange

def lambda_handler(event, context):
    # TODO implement
    
    s3_client = boto3.client("s3")
    s3_resource=boto3.resource("s3")
    s3_bucket=event['Bucket']
    key=event['key']
    video_name = key
    # random_id = randrange(100000)
    # video_name = video_name.split(".")[0] + "ID" + str(random_id)
    video_name = video_name.split(".")[0]
    url = s3_client.generate_presigned_url('get_object', 
                                    Params = {'Bucket': s3_bucket, 'Key': key}, 
                                    ExpiresIn = 6000)
    # print("URL = ", url)
    duration=event['duration']
    clip_start = 0
    min_video_duration = 5.0
    clipped_files = []
    FFMPEG_BINARY = os.getenv("FFMPEG_BINARY", "ffmpeg-imageio")
    os.environ["FFMPEG_BINARY"] = FFMPEG_BINARY
    FFMPEG_BINARY = get_ffmpeg_exe()
    # chunk_bucket="outputvideocse291"
    chunk_bucket="interchunkbucket"
    
    # if duration > 50:
    #     break_point = 25
    # elif duration < 20:
    #     break_point = 10
        
    if duration > 90:
        break_point = 40
    elif duration <= 90:
        break_point = 25
    
    
        
        
    # Loop over the video duration to get the clip stating point and end point to split the video
    while clip_start < duration:
        clip_end = clip_start + break_point
        # Setting the end position of the particular clip equals to the end time of original clip,
        # if end position or end position added with the **min_video_duration** is greater than
        # the end time of original video
        if clip_end > duration or (clip_end + min_video_duration) > duration:
            clip_end = duration
        #Split Video
        # creating a unique name for the clip video
        # Naming Format: <video name>_<start position>_<end position>.mp4
        # chunk_name = "{0}_ID{1}_{2}_{3}.mp4".format(
        #         key.split(".")[0], random_id, int(1000 * clip_start), int(1000 * clip_end)
        # )
        chunk_name = "{0}_{1}_{2}.mp4".format(
                key.split(".")[0], int(1000 * clip_start), int(1000 * clip_end)
        )
        
        chunk_json = {"chunk_name": chunk_name}
        clipped_files.append(chunk_json)
        
        t1 = clip_start
        t2 = clip_end
        
        #video filename and extension
        name, ext = os.path.splitext(key)
        ssParameter = "-ss " + "%0.2f" % t1
        timeParamter = " -t " + "%0.2f" % (t2 - t1)
        hideBannerParameter = " -y -hide_banner -loglevel panic  "
        codecParameter = " -vcodec libx264 -max_muxing_queue_size 9999"
        # codecParameter = " -vcodec copy -avoid_negative_ts 1 -max_muxing_queue_size 9999"
        
        ff = ffmpy.FFmpeg(
            executable=FFMPEG_BINARY,
            inputs={url: ssParameter + hideBannerParameter},
            outputs={"/tmp/chunkoutput_{}".format(chunk_name): timeParamter + codecParameter},
        )
        
        try:
            ff.run()
            # s3_client.upload_file("/tmp/chunkoutput_{}".format(chunk_name), chunk_bucket, chunk_name)
            with open("/tmp/chunkoutput_{}".format(chunk_name), 'rb') as file:
                s3_resource.Bucket(chunk_bucket).put_object(Key=chunk_name, Body=file)
            # return {'statusCode': 200,
            #     'body': json.dumps('Hello from Lambda! Inside try')
            # }
        except Exception as e:
            print(e)
            return {'statusCode': 400,
                'body': json.dumps("Exception")
            }
        
        clip_start = clip_end
    
    return {
        'value': "True",
        "clip_start":clip_start,
        'break_point':break_point,
        "clip_end":clip_end,
        "duration":duration,
        "video_name":video_name,
        "chunk_names":clipped_files
    }
