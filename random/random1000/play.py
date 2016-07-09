import os
import sys
randomPath = os.path.dirname(os.path.realpath(__file__))
sys.path.insert( 0, "%s/../../simulator"%randomPath )

from GameManager import *

GameManager.playGames( pNumRounds=1000,  pOutPath=randomPath )

