from GameManager import *
from DataManager import *
from DecisionTreeDecisionMaker import *

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
