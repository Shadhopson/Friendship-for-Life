import os
import sys
from collections import OrderedDict
apiCreatePath = os.path.dirname(os.path.realpath(__file__))

from Api import *

if len(sys.argv) != 2:
  print "Invalid # of args - expecting: (gameCode)"
  exit()
gameCode = sys.argv[1]

api = Api(gameCode)
api.createGame()

while api.game.isNextStep():
  outData = api.getGame()
  printData = OrderedDict()

  printData['Round'] = outData['Round']
  printData['TotalRounds'] = outData['TotalRounds']
  printData['CurrentStep'] = outData['CurrentStep']

  for player in outData['Players']:
    printData['Time'] = player['CurrentTime']
    printData['Money'] = player['Money']
    printData['TrustTokens'] = player['TrustTokens']
    if player['BankruptcyCounter']:
      printData['BankruptcyCounter'] = player['BankruptcyCounter']

    if len(player['Jobs']):
      printData['Jobs'] = []
      for job in player['Jobs']:
        printData['Jobs'].append( job['Label'] )
    if len(player['Hobbies']):
      printData['Hobbies'] = []
      for hobby in player['Hobbies']:
        printData['Hobbies'].append( hobby['Label'] )
    if len(player['Partners']):
      printData['Partners'] = []
      for partner in player['Partners']:
        printData['Partners'].append( partner['Label'] )
    if len(player['Children']):
      printData['Children'] = []
      for partner in player['Children']:
        printData['Children'].append( partner['Label'] )

    if len(player['SkillKnowledge']):
      printData['SkillKnowledge'] = []
      for knowledge in player['SkillKnowledge']:
        printData['SkillKnowledge'].append( "%s: %s"%(knowledge,player['SkillKnowledge'][knowledge]) )

    if len(player['NeedKnowledge']):
      printData['NeedKnowledge'] = player['NeedKnowledge']

    if len(player['JobSkillModifications']):
      printData['JobSkillModifications'] = []
      for jCode in player['JobSkillModifications']:
        for sCode in player['JobSkillModifications'][jCode]:
          printData['JobSkillModifications'].append( "%s: %s - %s"%(jCode,sCode,player['JobSkillModifications'][jCode][sCode]) )

    if len(player['PartnerSkillModifications']):
      printData['PartnerSkillModifications'] = []
      for pCode in player['PartnerSkillModifications']:
        for sCode in player['PartnerSkillModifications'][pCode]:
          printData['PartnerSkillModifications'].append( "%s: %s - %s"%(pCode,sCode,player['PartnerSkillModifications'][pCode][sCode]) )

    if len(player['JobFiredCounts']):
      printData['JobFiredCounts'] = []
      for code in player['JobFiredCounts']:
        printData['JobFiredCounts'].append( "%s: %s"%(code,player['JobFiredCounts'][code]) )

    if len(player['JobPassedCounts']):
      printData['JobPassedCounts'] = []
      for code in player['JobPassedCounts']:
        printData['JobPassedCounts'].append( "%s: %s"%(code,player['JobPassedCounts'][code]) )

    if len(player['PartnerFiredCounts']):
      printData['PartnerFiredCounts'] = []
      for code in player['PartnerFiredCounts']:
        printData['PartnerFiredCounts'].append( "%s: %s"%(code,player['PartnerFiredCounts'][code]) )

    if len(player['PartnerPassedCounts']):
      printData['PartnerPassedCounts'] = []
      for code in player['PartnerPassedCounts']:
        printData['PartnerPassedCounts'].append( "%s: %s"%(code,player['PartnerPassedCounts'][code]) )

    if len(player['PlayerNeedModifications']):
      printData['PlayerNeedModifications'] = []
      for code in player['PlayerNeedModifications']:
        printData['PlayerNeedModifications'].append( "%s: %s"%(code,player['PlayerNeedModifications'][code]) )

    for code in player['PlayerSkillModifications']:
      skillMods = []
      if int(player['PlayerSkillModifications'][code]) > 0:
        skillMods.append( "%s: %s"%(code,player['PlayerSkillModifications'][code]) )
    if len(skillMods):
      printData['PlayerSkillModifications'] = skillMods

  if len(outData['RevealedPartnerCards']):
    printData['RevealedPartnerCards'] = []
    for card in outData['RevealedPartnerCards']:
      printData['RevealedPartnerCards'].append( card['Label'] )

  if len(outData['RevealedJobCards']):
    printData['RevealedJobCards'] = []
    for card in outData['RevealedJobCards']:
      printData['RevealedJobCards'].append( card['Label'] )

  if len(outData['RevealedHobbyCards']):
    printData['RevealedHobbyCards'] = []
    for card in outData['RevealedHobbyCards']:
      printData['RevealedHobbyCards'].append( card['Label'] )

  printData['Actions'] = []
  for k,action in enumerate( outData['Actions'] ):
    lbl_arr = []
    for lbl in action:
      if lbl != 'step':
        lbl_arr.append( action[lbl] )
    label = " - ".join( lbl_arr )
    printData['Actions'].append( "%d: %s"%(k+1,label) )


  d(printData)

  sys.stdout.write( "Enter Action #: " )
  sys.stdout.flush()
  result = input()
  api.performAction( result )
  print ""
  print ""


d([api.getGame()])

DataManager.insertGameLogIntoDb(api.game.gameLog)
DataManager.closeConnection("gameConn")
