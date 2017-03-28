#!/usr/bin/python
# encoding: utf-8
# code: pca
# purpose: run pca on validators to start grouping validators

# thanks Sebastial http://bit.ly/2npnTT8

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA as sklearnPCA
import matplotlib.pyplot as plt


#%% CLEAN DATAFRAME, SCALE FOR PCA


# read in validators, set index to user name, rid the uid
validators = pd.read_csv("output/validators.csv")
validatorsTMP = validators.drop(['user_id','user_name'],axis=1).dropna()
validatorsFIN = validators.set_index(['user_name']).drop(['user_id'],axis=1)

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

#%% REDUCE BACK TO 2d FEATURE SPACE, PROJECT TO NEW FEATURE SPACE

matrixW = np.hstack((eigPairs[0][1].reshape(len(eigPairs),1),
                      eigPairs[1][1].reshape(len(eigPairs),1)))

validatorsNFS = vStd.dot(matrixW)
#%% PLOT to see separation

with plt.style.context('seaborn-whitegrid'):
    plt.figure(figsize=(6, 4))
    for i in validatorsNFS:
        plt.scatter(i[0],i[1])

#%% PUSH OUT A DATAFRAME

vPCA = sklearnPCA(n_components=1)
yPCA = vPCA.fit_transform(vStd)
ComName = ["com" + str(x+1) for x in range(1)]
validatorsPCA = pd.DataFrame(yPCA, columns = ComName)
validatorsPCA = pd.concat([validatorsTMP, validatorsPCA],axis=1)
validatorFIN = pd.merge(validatorsFIN,validatorsPCA,how='inner')
validatorsFIN.to_csv('output/validatorsPCA.csv')

# next http://bit.ly/2nqWArk




