import json
import ffmpy
from imageio_ffmpeg import get_ffmpeg_exe
import os
import boto3
from subprocess import call

def lambda_handler(event, context):
    s3_client = boto3.client("s3")
    s3_resource=boto3.resource("s3")
    chunk_names = event
    video_name_ext = event[0]
    video_name = video_name_ext['chunk_name'].split("_")[0]
    # chunk_name2 = event[1]
    # chunk_name3 = event[2]
    # chunk_name4 = event[3]
    # print(chunk_name1)
    # video_name = event['video_name']
    s3_bucket = "compressedchunkbucket"
    s3_output_bucket = "outputvideocse291"
    
    FFMPEG_BINARY = os.getenv("FFMPEG_BINARY", "ffmpeg-imageio")
    os.environ["FFMPEG_BINARY"] = FFMPEG_BINARY
    FFMPEG_BINARY = get_ffmpeg_exe()
    
    all_chunks = {}
    exp = ""
    local_file_name = ""
    
    # print(chunk_names)
    number_of_chunks = 0
    
    for chunk in chunk_names:
        try:
            print(chunk)
            chunkname = chunk['chunk_name']
            print(chunkname)
            local_file_name = '/tmp/'+chunkname
            s3_resource.Bucket(s3_bucket).download_file(chunkname, local_file_name)
        except Exception as e:
            return {'statusCode': 400,
            'body': json.dumps('Exception in downloading')
            }
        all_chunks[local_file_name] = exp
        number_of_chunks += 1
        
    ffmpeg_output_parameters = '-filter_complex "[0:0][0:1][1:0][1:1]concat=n={}:v=1:a=1[outv][outa]" -map "[outv]" -map "[outa]" '.format(number_of_chunks)
    compressed_final_video = video_name + "_final_compressed_video.mp4"
    if (number_of_chunks > 1):
        ff = ffmpy.FFmpeg(
                executable=FFMPEG_BINARY,
                inputs=all_chunks,
                outputs={"/tmp/outputcompressedchunk_{}".format(compressed_final_video): ffmpeg_output_parameters},
            )
        try:
            ff.run()
            with open("/tmp/outputcompressedchunk_{}".format(compressed_final_video), 'rb') as file:
                s3_resource.Bucket(s3_output_bucket).put_object(Key=compressed_final_video, Body=file)
        except Exception as e:
            print(e)
            return {'statusCode': 400,
                'body': json.dumps('Exception')
            }
    else: 
        try:
            
            with open(('/tmp/'+chunkname).format(compressed_final_video), 'rb') as file:
                s3_resource.Bucket(s3_output_bucket).put_object(Key=compressed_final_video, Body=file)
        except Exception as e:
            print(e)
            return {'statusCode': 400,
                'body': json.dumps('Exception')
            }
    call('rm -rf /tmp/*', shell=True)
    return {
        'statusCode': 200,
        'body': json.dumps('Compressed Chunks are Merged!')
    }
