import time
from multiprocessing import Process, Pipe
import boto3
import cv2
import numpy as np
import functools
import operator
import itertools
import json
import pickle
# from scipy.signal import argrelextrema

lambda_client = boto3.client("lambda")

class FrameExtractor(object):

    def extract_candidate_frames(self, videopath):

        extracted_candidate_key_frames = []
        print(videopath)

        # Get all frames from video in chunks using python Generators
        frame_extractor_from_video_generator = self.__extract_all_frames_from_video__(
            videopath
        )
        # Loop over every frame in the frame extractor generator object and calculate the
        # local maxima of frames
        count=0
        for frames, frame_diffs in frame_extractor_from_video_generator:
            count+=1
            extracted_candidate_key_frames_chunk = []
            #if self.USE_LOCAL_MAXIMA:
            if True:

                # Getting the frame with maximum frame difference
                extracted_candidate_key_frames_chunk = self.__get_frames_in_local_maxima__(
                    frames, frame_diffs
                )
                extracted_candidate_key_frames.extend(
                    extracted_candidate_key_frames_chunk
                )
        print(count)
        print(len(extracted_candidate_key_frames))
        return extracted_candidate_key_frames
    
    def __get_frames_in_local_maxima__(self, frames, frame_diffs):
        
        extracted_key_frames = []
        diff_array = np.array(frame_diffs)
        sm_diff_array = self.__smooth__(diff_array, 20)

        input = {
            "array": sm_diff_array.tolist()
        }
        resp = lambda_client.invoke(
            FunctionName = 'arn:aws:lambda:us-west-2:072775118116:function:scipy-argrelextrema',
            InvocationType = 'RequestResponse',
            Payload = json.dumps(input)
        )
        response = json.load(resp['Payload'])

        frame_indexes = np.asarray(response['frame'])
        for frame_index in frame_indexes:
            extracted_key_frames.append(frames[frame_index - 1])
        del frames[:]
        del sm_diff_array
        del diff_array
        del frame_diffs[:]
        return extracted_key_frames
    
    def __extract_all_frames_from_video__(self, videopath):
        cap = cv2.VideoCapture(videopath)

        ret, frame = cap.read()
        i = 1
        chunk_no = 0
        
        while ret:
            curr_frame = None
            prev_frame = None

            frame_diffs = []
            frames = []
            for _ in range(0, 500):
                if ret:
                    prev_frame, curr_frame = self.__process_frame(frame, prev_frame, frame_diffs, frames)
                    i = i + 1
                    ret, frame = cap.read()
                    
                else:
                    cap.release()
                    break
            chunk_no = chunk_no + 1
            yield frames, frame_diffs
        cap.release()

    def __process_frame(self, frame, prev_frame, frame_diffs, frames):
        luv = cv2.cvtColor(frame, cv2.COLOR_BGR2LUV)
        curr_frame = luv
        frame_diff = self.__calculate_frame_difference(curr_frame, prev_frame)
        
        if frame_diff is not None:
            frame_diffs.append(frame_diff)
            frames.append(frame)
        del prev_frame
        prev_frame = curr_frame
        
        return prev_frame, curr_frame
    
    def __smooth__(self, x, window_len, window="hanning"):

        if x.ndim != 1:
            raise ValueError("smooth only accepts 1 dimension arrays.")

        if x.size < window_len:
            return x

        if not window in ["flat", "hanning", "hamming", "bartlett", "blackman"]:
            raise ValueError("Smoothing Window is on of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'")

        s = np.r_[2 * x[0] - x[window_len:1:-1], x, 2 * x[-1] - x[-1:-window_len:-1]]

        if window == "flat":  # moving average
            w = np.ones(window_len, "d")
        else:
            w = getattr(np, window)(window_len)
        y = np.convolve(w / w.sum(), s, mode="same")
        return y[window_len - 1 : -window_len + 1]
    
    def __calculate_frame_difference(self, curr_frame, prev_frame):
        if curr_frame is not None and prev_frame is not None:
            # Calculating difference between current and previous frame
            diff = cv2.absdiff(curr_frame, prev_frame)
            count = np.sum(diff)
            return count
        return None
   
def lambda_handler(event, context):
    s3_client = boto3.client("s3")
    # bucket=event['Bucket']
    # key=event['Key']
    # bucket=event['detail']['bucket']['name']
    bucket = "interchunkbucket"
    # key = event['detail']['object']['key']
    # print(bucket)
    # print(event['chunk_name'])
    key = event['chunk_name']
    # key = "Tidead_75000_98530.mp4"
    # print(event)
    url = s3_client.generate_presigned_url('get_object', Params = {'Bucket': bucket, 'Key': key},ExpiresIn = 6000000) 
    frameExtractor=FrameExtractor()
    frames=frameExtractor.extract_candidate_frames(url)
    output={
        "key":key.split(".")[0]
    }
    print(frames)
    s3 = boto3.resource('s3')
    s3object = s3.Object('tempstoragejson', key.split(".")[0])

    s3object.put(
    Body=(pickle.dumps(frames))
    )
    return output