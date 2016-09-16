import os
sandboxPath = os.path.dirname(os.path.realpath(__file__))

import sys
sys.path.insert(0, "%s/../simulator"%sandboxPath)
sys.path.insert(0, "%s/../decisionTree"%sandboxPath)

from sklearn import tree
import numpy as np
import json
import pickle
import csv 
import re
import pandas as pd
from DataManager import *
from GameManager import *
from DecisionTreeDecisionMaker import *

from sklearn import preprocessing

#from scikits.statsmodels.tools import categorical

csvPath = "%s/test.csv"%sandboxPath

f = open( csvPath )
csvFile = csv.reader(f)
out = []

hobbyCards = [item['HobbyCode'] for item in DataManager.getRows( "SELECT HobbyCode FROM Hobby" )]
partnerCards = [item['PartnerCode'] for item in DataManager.getRows( "SELECT PartnerCode FROM Partner" )]
childCards = [item['ChildCode'] for item in DataManager.getRows( "SELECT ChildCode FROM Child" )]
jobCards = [item['JobCode'] for item in DataManager.getRows( "SELECT JobCode FROM Job" )]

skills = [item['SkillCode'] for item in DataManager.getRows( "SELECT SkillCode FROM Skill" )]
needs = [item['NeedCode'] for item in DataManager.getRows( "SELECT NeedCode FROM Need" )]

header = [
  "Time",
  "Round",
  "Money",
  "FinalScore",
  "ActionType",
  "Decision",
]

has_card_map = {}
fired_card_map = {}
passed_card_map = {}
need_map = {}
skill_map = {}

for card in hobbyCards:
  has_card_map[card] = len(header)
  header.append("Has_"+card)

for card in partnerCards:
  has_card_map[card] = len(header)
  header.append("Has_"+card)
  fired_card_map[card] = len(header)
  header.append("Fired_"+card)
  passed_card_map[card] = len(header)
  header.append("Passed_"+card)

for card in childCards:
  has_card_map[card] = len(header)
  header.append("Has_"+card)

for card in jobCards:
  has_card_map[card] = len(header)
  header.append("Has_"+card)
  fired_card_map[card] = len(header)
  header.append("Fired_"+card)
  passed_card_map[card] = len(header)
  header.append("Passed_"+card)

for need in needs:
  need_map[need] = len(header)
  header.append("NeedKnowledge_"+need)

for skill in skills:
  skill_map[skill] = len(header)
  header.append("SkillKnowledge_"+skill)

out.append(header)

col_types = [None] * len(header)
skill_type_cols = [None] * 6
skill_code_cols = [None] * 6
skill_code_type_map = None
for ri,row in enumerate(csvFile):
  out_row = [None] * len(header)
  if( ri != 0 ):
    for ci,cell in enumerate(row):
      if col_types[ci] == 'copy':
        out_row[ci] = cell
      elif(col_types[ci] == 'has_card'): 
        if( cell ):
          out_row[has_card_map[cell]] = 1
      elif(col_types[ci] == 'fired_card'): 
        if( cell ):
          out_row[fired_card_map[cell]] = 1
      elif(col_types[ci] == 'passed_card'): 
        if( cell ):
          out_row[passed_card_map[cell]] = 1
      elif(col_types[ci] == 'need_knowledge'): 
        if( cell ):
          out_row[need_map[cell]] = 1
      elif(col_types[ci] == 'skill_knowledge_code'): 
        if( cell ):
          val = None
          type_val = row[skill_code_type_map[ci]];
          if type_val == 'low':
            val = 1
          elif type_val == 'medium':
            val = 2
          elif type_val == 'high':
            val = 3

          out_row[skill_map[cell]] = val

    out.append(out_row)
  else:
    for ci,cell in enumerate(row):
      if cell == 'Time':
        col_types[ci] = "copy"
      elif cell == 'Round':
        col_types[ci] = "copy"
      elif cell == 'Money':
        col_types[ci] = "copy"
      elif cell == 'FinalScore':
        col_types[ci] = "copy"
      elif cell == 'ActionType':
        col_types[ci] = "copy"
      elif cell == 'Decision':
        col_types[ci] = "copy"
      elif re.search( '^(C|J|H|P)\d', cell ):
        col_types[ci] = "has_card"
      elif re.search( '^(FP|FJ)\d', cell ):
        col_types[ci] = "fired_card"
      elif re.search( '^(PP|PJ)\d', cell ):
        col_types[ci] = "passed_card"
      elif re.search( '^(N)\d', cell ):
        col_types[ci] = "need_knowledge"
      elif re.search( '^(S)\dCode', cell ):
        col_types[ci] = "skill_knowledge_code"
        if re.search( '1', cell ):
          skill_code_cols[1] = ci
        elif re.search( '2', cell ):
          skill_code_cols[2] = ci
        elif re.search( '3', cell ):
          skill_code_cols[3] = ci
        elif re.search( '4', cell ):
          skill_code_cols[4] = ci
        elif re.search( '5', cell ):
          skill_code_cols[5] = ci

      elif re.search( '^(S)\dType', cell ):
        col_types[ci] = "skill_knowledge_type"
        if re.search( '1', cell ):
          skill_type_cols[1] = ci
        elif re.search( '2', cell ):
          skill_type_cols[2] = ci
        elif re.search( '3', cell ):
          skill_type_cols[3] = ci
        elif re.search( '4', cell ):
          skill_type_cols[4] = ci
        elif re.search( '5', cell ):
          skill_type_cols[5] = ci
    skill_code_type_map = [None] * len(row)
    for ti,type in enumerate(skill_code_cols):
      if( type != None ):
        skill_code_type_map[type] = skill_type_cols[ti]

outPath = "%s/out.csv"%sandboxPath
outFile = open(outPath,'wb')
writer = csv.writer(outFile)
writer.writerows(out)
outFile.close()

