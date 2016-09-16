import os
import sys

dtv1Path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, "%s/.."%dtv1Path)

from DecisionTreeDecisionMaker import *

maker = DecisionTreeCreator( dtv1Path, "%s/../decisionTreeRound1FinalScore.csv"%dtv1Path )

maker.create()
