import os
sandboxPath = os.path.dirname(os.path.realpath(__file__))

import sys
sys.path.insert(0, "%s/../simulator"%sandboxPath)
sys.path.insert(0, "%s/../decisionTree"%sandboxPath)

from sklearn import tree
import numpy as np
import json
import pickle
import csv 
import re
import pandas as pd
from DataManager import *
from GameManager import *
from DecisionTreeDecisionMaker import *

from sklearn import preprocessing

#from scikits.statsmodels.tools import categorical

csvPath = "%s/out.csv"%sandboxPath
dataset = np.loadtxt( csvPath, dtype='int', delimiter=",", skiprows=1,converters={ \
    4: convertCell, \
    5: convertCell, \
    6: convertCell, \
    7: convertCell, \
    8: convertCell, \
    9: convertCell, \
    10: convertCell, \
    11: convertCell, \
    12: convertCell, \
    13: convertCell, \
    14: convertCell, \
    15: convertCell \
    } )

print 'asfd'
exit()

non_cat_data = dataset[:, [0,1,2] ]
cat_data = dataset[:, [4,5,6,7,8,9,10,11,12,13,14,15] ]

output_data = dataset[:, 3]

#enc =  preprocessing.OneHotEncoder()
#enc.fit(cat_data)
#cat_out = enc.transform(cat_data).toarray() 
merge_data = np.concatenate((non_cat_data,cat_data),axis=1)
#d(merge_data[0])

#clf = MLPClassifier(algorithm='l-bfgs', alpha=1e-5, hidden_layer_sizes=(5, 2), random_state=1)
clf = tree.DecisionTreeClassifier()
clf = clf.fit(merge_data, output_data)
