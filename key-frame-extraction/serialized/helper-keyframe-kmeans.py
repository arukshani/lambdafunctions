import json
from sklearn.cluster import KMeans
import numpy as np 
def lambda_handler(event, context):
    
    all_hists = event['all_hists']
    length=event['length']
    size=event['size']
    nb_clusters=event['nb_clusters']
    hist=[]
    for i in range(length):
        hist.append(np.array(all_hists[(i)*size:(i+1)*size]))
    kmeans = KMeans(n_clusters=nb_clusters, random_state=0).fit(hist)
    labels = kmeans.labels_
    
    return { "labels":labels.tolist()}
