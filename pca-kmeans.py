#!/usr/bin/python
# encoding: utf-8
# code: pca
# purpose: run pca on validators to start grouping validators

# thanks Sebastial http://bit.ly/2npnTT8

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA as sklearnPCA
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
%matplotlib inline

#%% CLEAN DATAFRAME, SCALE FOR PCA


# read in validators, set index to user name, rid the uid
validators = pd.read_csv("output/validators_analysis.csv")
validatorsTMP = validators.drop(['user_id','user_name'],axis=1).dropna()
validatorsFIN = validators.drop(['user_id'],axis=1)
validatorsTMP = validatorsTMP[validatorsTMP.validations > 0]
validatorsFIN = validatorsFIN[validatorsFIN.validations > 0]
validatorsTMP = validatorsTMP.drop(['mapping_freq','validations'],axis=1)

# 0 = mean, +-1 = +-standard devation
vStd = StandardScaler().fit_transform(validatorsTMP)

#%% EIGENDECOMPOSITION

vMeanVec = np.mean(vStd, axis=0)
covMat = (vStd - vMeanVec).T.dot((vStd - vMeanVec)) / (vStd.shape[0]-1)


#%% CORRELATION MATRIX
covMat = np.cov(vStd.T)
eigVals, eigVecs = np.linalg.eig(covMat)

#%% SORT EIGENPAIRS

for ev in eigVecs:
    np.testing.assert_array_almost_equal(1.0, np.linalg.norm(ev))

# Make a list of (eigenvalue, eigenvector) tuples
eigPairs = [(np.abs(eigVals[i]), eigVecs[:,i]) for i in range(len(eigVals))]
# Sort the (eigenvalue, eigenvector) tuples from high to low
eigPairs.sort(key=lambda x: x[0], reverse=True)

#%% EXPLAINED VARIANCE
tot = sum(eigVals)
varExp = [(i / tot)*100 for i in sorted(eigVals, reverse=True)]
cumVarExp = np.cumsum(varExp)
#%% PLOT EXPLAINED VARIANCE FOR EIGEN PAIRS

plt.plot(varExp)
plt.plot(cumVarExp)

#%% PUSH OUT A DATAFRAME

vPCA = sklearnPCA()
yPCA = vPCA.fit_transform(vStd)

ComName = ["c" + str(x+1) for x in range(int(yPCA.size/495))]
validatorsPCA = pd.DataFrame(yPCA, columns = ComName)
validatorsPCA=validatorsPCA.merge(
    validatorsTMP,
    left_index=True,
    right_index=True).merge(
    validatorsFIN,
    left_index=True,
    right_index=True)
validatorsPCA.to_csv('output/validatorsPCA.csv')

#%% CLASSIFY IT WITH KMEANS

# create nd.array of components 1 and 2 for kmeans classification
c1c2List = []
for i in range(0,len(validatorsPCA.c1)):
    c1c2List.append([validatorsPCA.c1[i],validatorsPCA.c2[i]])
c1c2Array = np.array(c1c2List)
kMeans = KMeans(n_clusters=3,init='k-means++',n_init=300, verbose=1)
kMeans.fit(c1c2Array)
centroids = kMeans.cluster_centers_
labels = kMeans.labels_
labels
validatorsLST = []
for i in range(len(c1c2Array)):
    validatorsLST.append(labels[i])
validatorsTMP = pd.DataFrame(validatorsLST)
validatorsTMP.columns = ['kmeansClass']
validatorsPCA=validatorsPCA.merge(
    validatorsTMP,
    left_index=True,
    right_index=True)
validatorsPCA.to_csv('output/validatorsPCAclassified.csv')
# next http://bit.ly/2nqWArk
