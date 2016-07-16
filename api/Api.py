import os
import sys
import pickle
apiPath = os.path.dirname(os.path.realpath(__file__))
sys.path.insert( 0, "%s/../simulator"%apiPath )

from GameManager import *
from DataManager import *

#GameManager.playGames( pNumRounds=1,  pPlayerCodes=['Player1'], pOutPath="%s/saveFiles"%apiCreatePath )

class Api(object):

  def __init__( self, pCode ):
    self.game = None
    self.code = pCode

  #API METHODS
  def createGame( self, pPlayerCodes=None ):

    saveHomeDir = "%s/saveFiles"%(apiPath)
    if os.path.isdir( saveHomeDir ) == False:
      os.mkdir( saveDir )

    saveDir = "%s/saveFiles/%s"%(apiPath,self.code)
    if os.path.isdir( saveDir ) == False:
      os.mkdir( saveDir )

    DataManager.initSettings()
    DataManager.settings['gameResultsDbPath'] = "%s/games.db"%(saveDir)
    DataManager.createGameDb()

    self.game = Game()
    self.game.resetGame()
    playerCodes = pPlayerCodes
    if playerCodes == None:
      playerCodes = [self.game.playerCardDeck[0].code]

    for code in playerCodes:
      self.game.addPlayer( code )

    self.game.decisionMaker = self

    self.saveGame()

  def getGame(self):
    return self.game.jsonData();

  def performAction(self,pAction):
    action = int(pAction) - 1
    if action < 0 or action >= len(self.game.nextStepAvailableActions()):
      print "invalid selection";
      exit()
    self.game.performNextStep( action )
    self.saveGame()

  #INTERNAL METHODS
  def saveGame(self):

    saveData = {}
    saveData['api'] = self
    saveData['DataManagerSettings'] = DataManager.settings
    saveData['GameManagerSettings'] = GameManager.settings

    s = pickle.dumps(saveData)
    saveDir = "%s/saveFiles/%s"%(apiPath,self.code)
    saveFile = open( "%s/gameSave.pkl"%saveDir, 'w' )
    saveFile.write(s)
    saveFile.close()


  @staticmethod
  def loadGame(pCode):
    saveDir = "%s/saveFiles/%s"%(apiPath,pCode)
    saveFile = open( "%s/gameSave.pkl"%saveDir, 'r' )

    data = pickle.loads(saveFile.read())
    DataManager.settings = data['DataManagerSettings']
    GameManager.settings = data['GameManagerSettings']
    return data['api']

  def makeDecision( self, pGame, pOptions ):
    return 0
