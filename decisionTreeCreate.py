from sklearn import tree
import numpy as np
import json
import pickle

arr = [ "" ]
def convert_cell(content):
  if content not in arr:
    arr.append(content)
  return arr.index(content)

dataset = np.loadtxt('gameOut.csv', dtype='int', delimiter=",", skiprows=1,converters={ \
    4: convert_cell, \
    5: convert_cell, \
    6: convert_cell, \
    7: convert_cell, \
    8: convert_cell, \
    9: convert_cell, \
    10: convert_cell, \
    11: convert_cell, \
    12: convert_cell, \
    13: convert_cell } )
    

input_data = dataset[:, [0,1,2,4,5,6,7,8,9,10,11,12,13] ]
output_data = dataset[:, 3]

clf = tree.DecisionTreeClassifier()
clf = clf.fit(input_data, output_data)

s = pickle.dumps(clf)
dtFile = open( 'decisionTreeSave.pkl', 'w' )
dtFile.write( s );
dtFile.close()

choicesFile = open( 'decisionTreeChoices.pkl', 'w' )
s = pickle.dumps(arr)
choicesFile.write( s );
choicesFile.close()

sample_inputs = []
for i in range( 100 ):
  sample_inputs.append( input_data[i*500] )
file = open( 'decisionTreeSampleInputs.pkl', 'w' )
file.write( pickle.dumps(sample_inputs) )
file.close()

print dataset[722]
print input_data[722]
print output_data[722]
print clf.predict( sample_inputs ) 
