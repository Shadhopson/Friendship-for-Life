import os
import sys
randomPath = os.path.dirname(os.path.realpath(__file__))
sys.path.insert( 0, "%s/../../simulator"%randomPath )

from GameManager import *

GameManager.setting('forceShareKnowledge')
GameManager.settings['forceShareKnowledge'] = True

GameManager.playGames( pNumRounds=100,  pOutPath=randomPath )

