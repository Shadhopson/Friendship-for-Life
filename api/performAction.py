import os
import sys
apiCreatePath = os.path.dirname(os.path.realpath(__file__))

from Api import *

if len(sys.argv) != 3:
  print "Invalid # of args - expecting: (gameCode,decisionIndex)"
  exit()
gameCode = sys.argv[1]
decision = sys.argv[2]

api = Api.loadGame(gameCode)
api.performAction(decision)
