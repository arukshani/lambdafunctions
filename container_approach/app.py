import sys

import os
import os.path
import cv2
from Katna.video import Video

def handler(event, context):

    vd = Video()

    # folder to save extracted images
    out_dir_path = "/tmp"
    # out_dir_path = os.path.join(".", output_folder_video_image)

    # if not os.path.isdir(out_dir_path):
    #     os.mkdir(out_dir_path)

    # Video file path
    video_file_path = os.path.join(".", "tests", "data", "pos_video.mp4")
    print(f"Input video file path = {video_file_path}")

    status = vd.compress_video(
        file_path=video_file_path, 
        out_dir_path=out_dir_path
    )


    # Video folder path
    video_folder_path = os.path.join(".", "tests", "data")
    print(f"Input video folder path = {video_folder_path}")

    status = vd.compress_videos_from_dir(
        dir_path=video_folder_path,
        force_overwrite=True,
        out_dir_path=out_dir_path
    )

    return 'Hello from AWS Lambda using Python' + sys.version + '!'        
