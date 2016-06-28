from sklearn import tree
import numpy as np
import json
import pickle
from GameManager import *
from DataManager import *

class DecisionTreeDecisionMaker:
  def convertChoice(self,content):
    if content not in self.choiceMap:
      self.choiceMap.append(content)
    return self.choiceMap.index(content)

  def __init__(self):
    dtFile = open( 'decisionTreeSave.pkl', 'r' )
    self.clf = pickle.loads(dtFile.read())

    siFile = open( 'decisionTreeSampleInputs.pkl', 'r' )
    self.samples = pickle.loads(siFile.read())

    choiceFile = open( 'decisionTreeChoices.pkl', 'r' )
    self.choiceMap = pickle.loads( choiceFile.read() )
    choiceFile.close()

  def makeDecision( self, game, options ):
    choice = random.randint(0,len(options)-1)
    if len(options) > 1:
      choices = []
      for option in options:
        choices.append( option['action'] )
      inputs = []
      searchChoices = [ 'jobSearch', 'hobbySearch', 'partnerSearch', 'childAttempt' ]
      addChoices = [ 'addHobby', 'addPartner', 'addJob' ]
      isSearch = False
      for sChoice in searchChoices:
        if sChoice in choices:
          isSearch = True
          break

      isPrediction = True
      for option in options:
        input = []

        input.append( game.players[0].currentTime() )
        input.append( game.currentRound )
        input.append( game.players[0].money )
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

        if option['action'] == 'addJob':
          input.append( self.convertChoice( option['jobCard'] ) )
        elif option['action'] == 'addPartner':
          input.append( self.convertChoice( option['partnerCard'] ) )
        elif option['action'] == 'addHobby':
          input.append( self.convertChoice( option['hobbyCard'] ) )
        else:
          input.append( self.convertChoice( option['action'] ) )

        children_codes = []
        for child in game.players[0].children:
          children_codes.append(child.code)
        children_codes = sorted(children_codes)
        children_input = self.convertChoice( "".join(children_codes) )
        input.append( children_input )

        jobs_codes = []
        for job in game.players[0].jobs:
          jobs_codes.append(job.code)
        jobs_codes = sorted(jobs_codes)
        jobs_input = self.convertChoice( "".join(jobs_codes) )
        input.append( jobs_input )

        hobbies_codes = []
        for hobby in game.players[0].hobbies:
          hobbies_codes.append(hobby.code)
        hobbies_codes = sorted(hobbies_codes)
        hobbies_input = self.convertChoice( "".join(hobbies_codes) )
        input.append( hobbies_input )

        partners_codes = []
        for partner in game.players[0].partners:
          partners_codes.append(partner.code)
        partners_codes = sorted(partners_codes)
        partners_input = self.convertChoice( "".join(partners_codes) )
        input.append( partners_input )

        partners_codes = []
        for partner in game.players[0].partnerFiredCounts:
          partners_codes.append(partner)
        partners_codes = sorted(partners_codes)
        partners_input = self.convertChoice( "".join(partners_codes) )
        input.append( partners_input )

        partners_codes = []
        for partner in game.players[0].partnerPassedCounts:
          partners_codes.append(partner)
        partners_codes = sorted(partners_codes)
        partners_input = self.convertChoice( "".join(partners_codes) )
        input.append( partners_input )

        jobs_codes = []
        for job in game.players[0].jobFiredCounts:
          jobs_codes.append(job)
        jobs_codes = sorted(jobs_codes)
        jobs_input = self.convertChoice( "".join(jobs_codes) )
        input.append( jobs_input )

        jobs_codes = []
        for job in game.players[0].jobPassedCounts:
          jobs_codes.append(job)
        jobs_codes = sorted(jobs_codes)
        jobs_input = self.convertChoice( "".join(jobs_codes) )
        input.append( jobs_input )

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
        print choice
    return choice

dm = DecisionTreeDecisionMaker()

game = Game()
game.decisionMaker = dm
DataManager.settings['gameResultsDbPath'] = 'decisionTreeGameOut.db'
for i in range(len(game.playerCardDeck)):
  for j in range(10):
    if j%100 == 0:
      print "Player%d - round %d"%(i+1,j)
    game.resetGame()
    game.addPlayer( "Player%d"%(i+1) )
    while game.isNextStep():
      game.performNextStep( dm.makeDecision( game, game.nextStepAvailableActions() ) )
    DataManager.insertGameLogIntoDb(game.gameLog)
    print game.players[0].points()
