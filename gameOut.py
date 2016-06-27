from GameManager import *

#DataManager.clearGameLogDb()
game = Game()
for i in range(len(game.playerCardDeck)):
  for j in range(1000):
    if j%100 == 0:
      print "Player%d - round %d"%(i+1,j)
    game.resetGame()
    game.addPlayer( "Player%d"%(i+1) )
    while game.isNextStep():
      game.performNextStep( game.decisionMaker.makeDecision( game, game.nextStepAvailableActions() ) )
    DataManager.insertGameLogIntoDb(game.gameLog)

