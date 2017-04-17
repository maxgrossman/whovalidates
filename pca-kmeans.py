#!/usr/bin/python
# encoding: utf-8
# code: pca
# purpose: run pca on validators to start grouping validators

# thanks Sebastial for how to conduct PCA with sklearn bit.ly/2npnTT8
# thanks Yangki for guiding how to take a sklearn PCA and make a df of principal components bit.ly/2oNPtfj
# thanks sentdex for showing how to conduct kmeans classifcation bit.ly/2oBvLS1

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA as sklearnPCA
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import itertools
%matplotlib inline

#%% CLEAN DATAFRAME, SCALE FOR PCA


# read in validators, set index to user name, rid the uid
validators = pd.read_csv("output/validators_analysis.csv")
validatorsTMP = validators.drop(['user_id','a','user_name','mapping_freq'],axis=1)[validators['validations']>0].dropna()
validatorsFIN = validators.drop(['user_id'],axis=1)[validators['validations']>0]

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

# create and write out dataframe with eigenVec/Explained variance info for PCs

# this dataframe's columns are principal components. the first row is
# the explained variance, then following rows are each variable's and its eigenvector

EigVar =  pd.concat([pd.DataFrame(np.array(varExp)).T,pd.DataFrame(eigVecs)])

# set index so rows are better explained
Index = ['explained_variance'] + validatorsTMP.columns.tolist()
EigVar['Index'] = Index 
EigVar = EigVar.set_index('Index')

# make column names reflect components too. the 495 comes from # rows in 
# original csv. So yPCA/#rows = # of principal components 
ComponentNames = ["c" + str(x+1) for x in range(int(yPCA.size/495))]
EigVar.columns = ComponentNames

# write it to a csv
EigVar.to_csv('output/EigVar.csv')

#%% PLOT EXPLAINED VARIANCE FOR EIGEN PAIRS

plt.plot(varExp)
plt.plot(cumVarExp)

#%% PUSH OUT A DATAFRAME

vPCA = sklearnPCA()
yPCA = vPCA.fit_transform(vStd)
validatorsPCA = pd.DataFrame(yPCA, columns = ComponentNames)
validatorsPCA=validatorsPCA.merge(
    validatorsTMP,
    left_index=True,
    right_index=True).merge(
    validatorsFIN,
    left_index=True,
    right_index=True)
validatorsPCA.to_csv('output/validatorsPCA-validatorsOnly.csv')

#%% CLASSIFY IT WITH KMEANS
# create nd.array for each possible combination of the first 4 principal
# components
componentCombos = list(itertools.combinations(range(4),2))
kMeans = KMeans(n_clusters=3,init='k-means++',n_init=300, verbose=1)
for i in range(len(componentCombos)):
    cA = validatorsPCA['c' + str(componentCombos[i][0]+1)].tolist()
    cB = validatorsPCA['c' + str(componentCombos[i][1]+1)].tolist()
    cAcBList = [[cA[i],cB[i]] for i in range(0,len(cA))]
    cAcBArray = np.array(cAcBList)
    kMeans.fit(cAcBArray)
    centroids = kMeans.cluster_centers_
    labels = kMeans.labels_
    labels
    validatorsLST = []
    for j in range(len(cAcBArray)):
        validatorsLST.append(labels[j])
    validatorsTMP = pd.DataFrame(validatorsLST)
    validatorsTMP.columns = [
            'kmeansClass'+'c'+ str(componentCombos[i][0]+1) +
                          'c'+ str(componentCombos[i][1]+1) 
    ]
    validatorsPCA=validatorsPCA.merge(
        validatorsTMP,
        left_index=True,
        right_index=True)
validatorsPCA.to_csv('output/validatorsPCAclassified-validatorsOnly.csv')
# next http://bit.ly/2nqWArk
