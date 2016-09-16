import os
dtPath = os.path.dirname(os.path.realpath(__file__))

import sys
sys.path.insert(0, "%s/../simulator"%dtPath)


from sklearn import tree
from sklearn import preprocessing
from sklearn.neural_network import MLPClassifier
import numpy as np
import json
import pickle
from DataManager import *
from GameManager import *

choiceArr = [ "" ]
def convertCell(pContent):
  if pContent not in choiceArr:
    choiceArr.append(pContent)
  return choiceArr.index(pContent)


class DecisionTreeCreator:
  def __init__(self,pOutDir,pSourceCsvFile):
    self.sourceCsvFile = pSourceCsvFile
    if os.path.isfile( self.sourceCsvFile ) == False and os.path.isfile( "%s/%s"%(dtPath,self.sourceCsvFile) ) == True:
      self.sourceCsvFile = "%s/%s"%(dtPath,self.sourceCsvFile)

    self.outDir = pOutDir
    if os.path.isdir( self.outDir ) == False and os.path.isdir( "%s/%s"%(dtPath,self.outDir) ) == True:
      self.outDir = "%s/%s"%(dtPath,self.outDir)
    if os.path.isdir(self.outDir) == False:
      os.mkdir( self.outDir )

  def create(self):
    csvPath = self.sourceCsvFile

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

    non_cat_data = dataset[:, [0,1,2] ]
    cat_data = dataset[:, [4,5,6,7,8,9,10,11,12,13,14,15] ]

    output_data = dataset[:, 3]

    enc =  preprocessing.OneHotEncoder()
    enc.fit(cat_data)
    cat_out = enc.transform(cat_data).toarray() 
    merge_data = np.concatenate((non_cat_data,cat_data),axis=1)
    d(merge_data[0])

    clf = MLPClassifier(algorithm='l-bfgs', alpha=1e-5, hidden_layer_sizes=(5, 2), random_state=1)
    #clf = tree.DecisionTreeClassifier()
    clf = clf.fit(merge_data, output_data)

    s = pickle.dumps(clf)
    dtFileName = "%s\\save.pkl"%self.outDir
    dtFile = open( dtFileName, 'w' )
    print dtFileName
    dtFile.write( s );
    dtFile.close()

    choicesFile = open( "%s\\choices.pkl"%self.outDir, 'w' )
    s = pickle.dumps(choiceArr)
    choicesFile.write( s );
    choicesFile.close()

    sample_inputs = []
    for i in range( 100 ):
      sample_inputs.append( merge_data[i*500] )
    file = open( "%s\\sampleInputs.pkl"%self.outDir, 'w' )
    file.write( pickle.dumps(sample_inputs) )
    file.close()

    file = open( "%s\\def.txt"%self.outDir, 'w' )
    file.write( "input file: %s\n"%self.sourceCsvFile )
    file.close()

    print dataset[722]
    print merge_data[722]
    print output_data[722]
    print clf.predict( sample_inputs ) 

class DecisionTreeDecisionMaker:
  def convertChoice(self,content):
    if content not in self.choiceMap:
      self.unknowns.append(content)
      self.choiceMap.append(content)
    return self.choiceMap.index(content)

  def __init__( self, pDecisionTreeDirectory='.' ):

    dtFile = open( "%s\\save.pkl"%(pDecisionTreeDirectory), 'r' )
    self.clf = pickle.loads(dtFile.read())

    siFile = open( "%s\\sampleInputs.pkl"%(pDecisionTreeDirectory), 'r' )
    self.samples = pickle.loads(siFile.read())

    choiceFile = open( "%s\\choices.pkl"%(pDecisionTreeDirectory), 'r' )
    self.choiceMap = pickle.loads( choiceFile.read() )
    self.unknowns = []
    choiceFile.close()

  def makeDecision( self, pGame, pOptions ):
    choice = random.randint(0,len(pOptions)-1)
    if len(pOptions) > 1:
      choices = []
      for option in pOptions:
        choices.append( option['action'] )
      inputs = []
      searchChoices = [ 'jobSearch', 'hobbySearch', 'partnerSearch', 'childAttempt' ]
      isSearch = False
      isJobDecision = False
      isHobbyDecision = False
      isPartnerDecision = False
      for sChoice in searchChoices:
        if sChoice in choices:
          isSearch = True
          break

      isPrediction = True
      for option in pOptions:

        input = []

        input.append( pGame.players[0].currentTime() )
        input.append( pGame.currentRound )
        input.append( pGame.players[0].money )
        if isSearch:
          input.append( self.convertChoice( 'searchChoice' ) )
        elif 'addHobby' in choices:
          input.append( self.convertChoice( 'hobbySearch' ) )
        elif 'addJob' in choices:
          input.append( self.convertChoice( 'jobSearch' ) )
        elif 'addPartner' in choices:
          input.append( self.convertChoice( 'partnerSearch' ) )
        else:
          isPrediction = False
          break

        if option['action'] == 'addJob':
          input.append( self.convertChoice( option['jobCard'] ) )
          isJobDecision = True
        elif option['action'] == 'addPartner':
          input.append( self.convertChoice( option['partnerCard'] ) )
          isPartnerDecision = True
        elif option['action'] == 'addHobby':
          input.append( self.convertChoice( option['hobbyCard'] ) )
          isHobbyDecision = True 
        else:
          input.append( self.convertChoice( option['action'] ) )

        children_codes = []
        for child in pGame.players[0].children:
          children_codes.append(child.code)
        children_codes = sorted(children_codes)
        children_input = self.convertChoice( "_".join(children_codes) )
        input.append( children_input )

        jobs_codes = []
        for job in pGame.players[0].jobs:
          jobs_codes.append(job.code)
        jobs_codes = sorted(jobs_codes)
        jobs_input = self.convertChoice( "_".join(jobs_codes) )
        input.append( jobs_input )

        hobbies_codes = []
        for hobby in pGame.players[0].hobbies:
          hobbies_codes.append(hobby.code)
        hobbies_codes = sorted(hobbies_codes)
        hobbies_input = self.convertChoice( "_".join(hobbies_codes) )
        input.append( hobbies_input )

        partners_codes = []
        for partner in pGame.players[0].partners:
          partners_codes.append(partner.code)
        partners_codes = sorted(partners_codes)
        partners_input = self.convertChoice( "_".join(partners_codes) )
        input.append( partners_input )

        partners_codes = []
        for partner in pGame.players[0].partnerFiredCounts:
          partners_codes.append(partner)
        partners_codes = sorted(partners_codes)
        partners_input = self.convertChoice( "_".join(partners_codes) )
        input.append( partners_input )

        partners_codes = []
        for partner in pGame.players[0].partnerPassedCounts:
          partners_codes.append(partner)
        partners_codes = sorted(partners_codes)
        partners_input = self.convertChoice( "_".join(partners_codes) )
        input.append( partners_input )

        jobs_codes = []
        for job in pGame.players[0].jobFiredCounts:
          jobs_codes.append(job)
        jobs_codes = sorted(jobs_codes)
        jobs_input = self.convertChoice( "_".join(jobs_codes) )
        input.append( jobs_input )

        jobs_codes = []
        for job in pGame.players[0].jobPassedCounts:
          jobs_codes.append(job)
        jobs_codes = sorted(jobs_codes)
        jobs_input = self.convertChoice( "_".join(jobs_codes) )
        input.append( jobs_input )

        skill_knowledge = []
        for skill in pGame.players[0].skillKnowledge:
          skill_knowledge.append("%s%s"%(skill,pGame.players[0].skillKnowledge[skill]))
        skill_knowledge = sorted(skill_knowledge)
        skill_input = self.convertChoice( "_".join(skill_knowledge) )
        input.append( skill_input )

        need_knowledge = []
        for need in pGame.players[0].needKnowledge:
          need_knowledge.append("%sHasNeed"%need)
        need_knowledge = sorted(need_knowledge)
        need_input = self.convertChoice( "_".join(need_knowledge) )
        input.append( need_input )

        inputs.append(input)

      if isPrediction:
        predictions_pr = self.clf.predict_proba(inputs)
        best_score = None
        best_choice = None
        scores = []
        for prediction_i, prediction in enumerate(predictions_pr):
          score = 0
          for pi,p in enumerate(prediction):
            score += self.clf.classes_[pi] * p
          if best_score == None or score > best_score:
            best_score = score
            best_index = prediction_i
          scores.append(score)
        choice = best_index
    return choice

