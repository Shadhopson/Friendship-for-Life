import os
import sys

dtv1Path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, "%s/.."%dtv1Path)
sys.path.insert(0, "%s/../../simulator"%dtv1Path)

from GameManager import *
from DecisionTreeDecisionMaker import *

decisionMaker = DecisionTreeDecisionMaker( dtv1Path )

GameManager.playGames( pDecisionMaker=decisionMaker, pNumRounds=100,  pOutPath=dtv1Path )
