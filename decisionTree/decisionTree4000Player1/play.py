import os
import sys

dtpPath = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, "%s/.."%dtpPath)
sys.path.insert(0, "%s/../../simulator"%dtpPath)

from GameManager import *
from DecisionTreeDecisionMaker import *

decisionMaker = DecisionTreeDecisionMaker( dtpPath )

GameManager.playGames( pDecisionMaker=decisionMaker, pNumRounds=2000,  pOutPath=dtpPath, pPlayerCodes=['Player1'] )
