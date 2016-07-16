import os
import sys
apiCreatePath = os.path.dirname(os.path.realpath(__file__))

from Api import *

if len(sys.argv) != 2:
  print sys.argv
  print "Invalid # of args - expecting: (gameCode)"
  exit()

gameCode = sys.argv[1]

api = Api(gameCode)
api.createGame()
