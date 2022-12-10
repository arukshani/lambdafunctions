import json
import boto3
import json
import pickle
from skimage.filters.rank import entropy
from skimage.morphology import disk
import numpy as np
def lambda_handler(event, context):
    
    Key=event
    # Key = "Tidead_75000_98530gray_input"
    s3 = boto3.client('s3')

    obj = s3.get_object(Bucket='tempstoragejson',Key=Key)
    frames=pickle.loads(obj["Body"].read())
    print("111111\n")
    print(frames[0]['length'])
    print("2\n")
    # TODO implement
    entropy_score_list= []
    for frame in frames:
        gray_input=frame['gray']
        length=frame['length']
        size=frame['size']
        gray=[]
        for i in range(length):
            gray.append(np.array(gray_input[(i)*size:(i+1)*size]))
        gray=np.array(gray)
        entr_img = entropy(gray, disk(5))
        all_sum = np.sum(entr_img)
        num_of_pixels = entr_img.shape[0] * entr_img.shape[1]
        entropy_score = (all_sum) / (num_of_pixels)
        entropy_score_list.append(entropy_score)
        
    return { "entropy_score": entropy_score_list}
