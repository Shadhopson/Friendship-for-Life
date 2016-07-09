import os
import sys

dtv1Path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, "%s/.."%dtv1Path)

from DecisionTreeDecisionMaker import *

maker = DecisionTreeCreator( dtv1Path, "%s/../../random/random2000PointChange.csv"%dtv1Path )

print maker.outDir
print maker.sourceCsvFile

maker.create()
