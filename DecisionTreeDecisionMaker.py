from sklearn import tree
import numpy as np
import json
import pickle
from GameManager import *
from DataManager import *

class DecisionTreeDecisionMaker:
  def convertChoice(self,content):
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

        if option['action'] == 'addJob':
          input.append( self.convertChoice( option['jobCard'] ) )
        elif option['action'] == 'addPartner':
          input.append( self.convertChoice( option['partnerCard'] ) )
        elif option['action'] == 'addHobby':
          input.append( self.convertChoice( option['hobbyCard'] ) )
        else:
          input.append( self.convertChoice( option['action'] ) )
        inputs.append(input)
      if isSearch == False:
        print inputs
        print isSearch 
        print options
        print choices
        exit()
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
