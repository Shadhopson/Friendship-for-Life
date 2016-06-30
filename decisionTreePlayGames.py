from GameManager import *
from DataManager import *
from DecisionTreeDecisionMaker import *

dm = DecisionTreeDecisionMaker()

game = Game()
game.decisionMaker = dm
scores = []
playerScores = {}
DataManager.settings['gameResultsDbPath'] = 'decisionTreeGameOut.db'
DataManager.clearGameLogDb()
for i in range(len(game.playerCardDeck)):
  playerScores["Player%d"%(i+1)] = []
  for j in range(100):
    game.resetGame()
    game.addPlayer( "Player%d"%(i+1) )
    while game.isNextStep():
      game.performNextStep( game.decisionMaker.makeDecision( game, game.nextStepAvailableActions() ) )
    #DataManager.insertGameLogIntoDb(game.gameLog)
    scores.append( game.players[0].points() )
    playerScores["Player%d"%(i+1)].append( game.players[0].points() )
    #print "Player%d - round %d - score: %d"%(i+1,j,game.players[0].points())

print "Avg Score: %.2f"%( sum(scores) / float(len(scores) ) )
for player in sorted(playerScores):
  print "%s Avg Score: %.2f"%(player, sum(playerScores[player]) / float(len(playerScores[player])))
