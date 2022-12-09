import json
import numpy as np
from scipy.signal import argrelextrema
def lambda_handler(event, context):
    # TODO implement
    sm_diff_array=np.asarray(event['array'])
    
    frame_indexes=np.asarray(argrelextrema(sm_diff_array, np.greater)[0])
    print(frame_indexes)
    
    return { "frame":frame_indexes.tolist()}
