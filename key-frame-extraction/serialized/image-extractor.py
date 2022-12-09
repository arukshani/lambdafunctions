import boto3
import cv2
import numpy as np
import itertools
import json
import pickle
import re


lambda_client = boto3.client("lambda")

class ImageSelector(object):
    def __init__(self, n_processes=1):
        self.nb_clusters=0
        self.n_processes = n_processes

        self.min_brightness_value = 10.0
        self.max_brightness_value = 90.0
        self.brightness_step = 2.0 

        self.min_entropy_value = 1.0
        self.max_entropy_value = 10.0
        self.entropy_step = 0.5 
    
    def select_best_frames(self, input_key_frames, number_of_frames, Key):
        self.nb_clusters = number_of_frames

        filtered_key_frames = []
        filtered_images_list = []
        
        min_brightness_values = np.arange(self.min_brightness_value, -0.01, -self.brightness_step)
        max_brightness_values = np.arange(self.max_brightness_value, 100.01, self.brightness_step)
        min_entropy_values = np.arange(self.min_entropy_value, -0.01, -self.entropy_step)
        max_entropy_values = np.arange(self.max_entropy_value, 10.01, self.entropy_step)
        
        for (min_brightness_value, max_brightness_value, min_entropy_value, max_entropy_value) in itertools.zip_longest(min_brightness_values, max_brightness_values, min_entropy_values, max_entropy_values): 
            if min_brightness_value is None:
                min_brightness_value = 0.0
            if max_brightness_value is None:
                max_brightness_value = 100.0
            if min_entropy_value is None:
                min_entropy_value = 0.0
            if max_entropy_value is None:
                max_entropy_value = 10.0
            self.min_brightness_value = min_brightness_value
            self.max_brightness_value = max_brightness_value
            self.min_entropy_value = min_entropy_value
            self.max_entropy_value = max_entropy_value 
            filtered_key_frames = self.__filter_optimum_brightness_and_contrast_images__(
                input_key_frames, Key,
            )
            # failedhere1
            if len(filtered_key_frames) >= number_of_frames:
                break
        if len(filtered_key_frames) >= self.nb_clusters:
            files_clusters_index_array = self.__prepare_cluster_sets__(filtered_key_frames)
            selected_images_index = self.__get_best_images_index_from_each_cluster__(
                filtered_key_frames, files_clusters_index_array
            )

            for index in selected_images_index:
                img = filtered_key_frames[index]
                filtered_images_list.append(img)
        else:
            for img in filtered_key_frames:
                filtered_images_list.append(img)
        return filtered_images_list
    
    def __filter_optimum_brightness_and_contrast_images__(self, input_img_files, Key):
        n_files = len(input_img_files)

        brightness_score = []
        for i in input_img_files:
            brightness_score.append(self.__get_brightness_score__(i))
        
        
        gray_score = []
        print (n_files)
        for i in input_img_files: 
            gray_score.append(self.__get_gray_input__(i))
            
        s3 = boto3.resource('s3')
        s3object = s3.Object('tempstoragejson', Key.split(".")[0]+"gray_input")

        s3object.put(
            Body=(pickle.dumps(gray_score))
            )
            
        resp = lambda_client.invoke(
            FunctionName = 'arn:aws:lambda:us-west-2:072775118116:function:entropy_with_sklearn',
            InvocationType = 'RequestResponse',
            Payload = json.dumps(Key.split(".")[0]+"gray_input")
        )
        response1 = json.load(resp['Payload'])
        # print (response1)
        entropy_score = response1['entropy_score']
        # for i in input_img_files:
        #     entropy_score.append(self.__get_entropy_score__(i)) 
            
        entropy_score=np.array(entropy_score)
        brightness_score=np.array(brightness_score)

        brightness_ok = np.where(
            np.logical_and(
                brightness_score > self.min_brightness_value,
                brightness_score < self.max_brightness_value,
            ),
            True,
            False,
        )
        contrast_ok = np.where(
            np.logical_and(
                entropy_score > self.min_entropy_value,
                entropy_score < self.max_entropy_value,
            ),
            True,
            False,
        )

        return [
            input_img_files[i]
            for i in range(n_files)
            if brightness_ok[i] and contrast_ok[i]
        ]
    
    def __get_brightness_score__(self, image):
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        _, _, v = cv2.split(hsv)
        sum = np.sum(v, dtype=np.float32)
        num_of_pixels = v.shape[0] * v.shape[1]
        brightness_score = (sum * 100.0) / (num_of_pixels * 255.0)
        return brightness_score
        
    def __get_gray_input__(self, image):
        
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        length=len(gray)
        size=len(gray[0])
        gray_input=np.concatenate(gray).tolist()
        
        input = {
            "gray": gray_input,
            "length":length,
            "size":size
        }
        print (input) 
        print("\n")
        return input 
        
        
        
        # resp = lambda_client.invoke(
        #     FunctionName = 'arn:aws:lambda:us-west-2:072775118116:function:entropy-with-sklearn',
        #     InvocationType = 'RequestResponse',
        #     Payload = json.dumps(input)
        # )
        
        # response1 = json.load(resp['Payload'])
        # print("Resp")
        # print(response1)
        # print("end")
        # return response1["entropy_score"]
        
        
        
     
    def __get_best_images_index_from_each_cluster__(
        self, files, files_clusters_index_array
    ):
        filtered_items = []
        clusters = np.arange(len(files_clusters_index_array))
        for cluster_i in clusters:
            curr_row = files_clusters_index_array[cluster_i][0]
            
            n_images = np.arange(len(curr_row))
            variance_laplacians = self.__get_laplacian_scores(files, n_images)

            selected_frame_of_current_cluster = curr_row[np.argmax(variance_laplacians)]
            filtered_items.append(selected_frame_of_current_cluster)

        return filtered_items
    def __get_laplacian_scores(self, files, n_images):
        
        variance_laplacians = []
        
        for image_i in n_images:
            img_file = files[n_images[image_i]]
            img = cv2.cvtColor(img_file, cv2.COLOR_BGR2GRAY)

            variance_laplacian = self.__variance_of_laplacian__(img)
            variance_laplacians.append(variance_laplacian)
            
    def __prepare_cluster_sets__(self, files):
        all_hists = []

        for img_file in files:
            img = cv2.cvtColor(img_file, cv2.COLOR_BGR2GRAY)
            hist = cv2.calcHist([img], [0], None, [256], [0, 256])
            hist = hist.reshape((256))
            all_hists.append(hist)
        all_hists_byte=np.concatenate(all_hists)
        all_hists_byte=all_hists_byte.tolist()
        
        input = {
            "all_hists": all_hists_byte,
            "length":len(all_hists),
            "size":len(all_hists[0]),
            'nb_clusters':self.nb_clusters
        }
        resp = lambda_client.invoke(
            FunctionName = 'arn:aws:lambda:us-west-2:072775118116:function:keyframe-kmeans',
            InvocationType = 'RequestResponse',
            Payload = json.dumps(input)
        )
        response = json.load(resp['Payload'])
        
        labels=np.array(response['labels'])
        
        files_clusters_index_array = []
        for i in np.arange(self.nb_clusters):
            index_array = np.where(labels == i)
            files_clusters_index_array.append(index_array)

        files_clusters_index_array = np.array(files_clusters_index_array, dtype=object)
        return files_clusters_index_array
        
    def __variance_of_laplacian__(self, image):
        return cv2.Laplacian(image, cv2.CV_64F).var()

def lambda_handler(event, context):
    Key=event['key']
    s3 = boto3.client('s3')

    obj = s3.get_object(Bucket='tempstoragejson',Key=Key)
    frames=pickle.loads(obj["Body"].read())
    # return {}
    image_selector = ImageSelector()
    top_frames = image_selector.select_best_frames(
      frames, 5, Key    ) 
    
    dir_name = re.sub("\_\d+\_\d+$", "", Key) 
    print (dir_name)
    i = 0
    for frames in top_frames:
        image_string = cv2.imencode('.jpg', frames)[1].tostring()
        key = Key+"frame-" + str(i) + "-output.jpeg"
        s3.put_object(Bucket="outputvideocse291", Key = (dir_name+"/"+key), Body=image_string)
        i += 1
    

