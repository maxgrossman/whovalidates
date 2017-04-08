#!/usr/bin/python
# encoding: utf-8
# code: pca-kmeans
# purpose: classify pca run on validators.csv
import matplotlib.pyplot as pp
import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans

validators = pd.read_csv("output/validators.csv")
validatorsTMP = validators.set_index(['user_name']).drop(['user_id','Unnamed: 0'],axis=1)
validatorsPCA = PCA(n_components=2,whiten=True).fit_transform(validatorsFIN)
kMeans = KMeans(n_clusters=3,init='k-means++',n_init=300, verbose=1)
kMeans.fit(validatorsPCA)
centroids = kMeans.cluster_centers_
labels = kMeans.labels_
labels
for i in range(len(validatorsPCA)):
    pp.plot(validatorsPCA[i][0],validatorsPCA[i][1],colors[labels[i]],markersize=10)

validatorsLST = []
for i in range(len(validatorsPCA)):
    currentList = np.append(validatorsPCA[i],labels[i])
    currentList = np.append(currentList,i)
    validatorsLST.append(currentList)
validatorsLST
validatorsTMP = pd.DataFrame(validatorsLST)
validatorsTMP.columns = ['pcaX','pcaY','kmeansClass','Unnamed: 0']
validatorsTMP.set_index('Unnamed: 0')
validatorsFIN = pd.merge(validators,validatorsTMP,how='inner')
validatorsFIN.to_csv('output/validatorsClassified.csv')
