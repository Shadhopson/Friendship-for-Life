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
    playerData = OrderedDict()
    playerData['Time'] = player['CurrentTime']
    playerData['Money'] = player['Money']
    playerData['TrustTokens'] = player['TrustTokens']
    if player['BankruptcyCounter']:
      playerData['BankruptcyCounter'] = player['BankruptcyCounter']

    if len(player['Jobs']):
      playerData['Jobs'] = []
      for job in player['Jobs']:
        playerData['Jobs'].append( job['Label'] )
    if len(player['Hobbies']):
      playerData['Hobbies'] = []
      for hobby in player['Hobbies']:
        playerData['Hobbies'].append( hobby['Label'] )
    if len(player['Partners']):
      playerData['Partners'] = []
      for partner in player['Partners']:
        playerData['Partners'].append( partner['Label'] )
    if len(player['Children']):
      playerData['Children'] = []
      for partner in player['Children']:
        playerData['Children'].append( partner['Label'] )

    if len(player['SkillKnowledge']):
      playerData['SkillKnowledge'] = []
      for knowledge in player['SkillKnowledge']:
        playerData['SkillKnowledge'].append( "%s: %s"%(knowledge,player['SkillKnowledge'][knowledge]) )

    if len(player['NeedKnowledge']):
      playerData['NeedKnowledge'] = player['NeedKnowledge']

    if len(player['JobSkillModifications']):
      playerData['JobSkillModifications'] = []
      for jCode in player['JobSkillModifications']:
        for sCode in player['JobSkillModifications'][jCode]:
          playerData['JobSkillModifications'].append( "%s: %s - %s"%(jCode,sCode,player['JobSkillModifications'][jCode][sCode]) )

    if len(player['PartnerSkillModifications']):
      playerData['PartnerSkillModifications'] = []
      for pCode in player['PartnerSkillModifications']:
        for sCode in player['PartnerSkillModifications'][pCode]:
          playerData['PartnerSkillModifications'].append( "%s: %s - %s"%(pCode,sCode,player['PartnerSkillModifications'][pCode][sCode]) )

    if len(player['JobFiredCounts']):
      playerData['JobFiredCounts'] = []
      for code in player['JobFiredCounts']:
        playerData['JobFiredCounts'].append( "%s: %s"%(code,player['JobFiredCounts'][code]) )

    if len(player['JobPassedCounts']):
      playerData['JobPassedCounts'] = []
      for code in player['JobPassedCounts']:
        playerData['JobPassedCounts'].append( "%s: %s"%(code,player['JobPassedCounts'][code]) )

    if len(player['PartnerFiredCounts']):
      playerData['PartnerFiredCounts'] = []
      for code in player['PartnerFiredCounts']:
        playerData['PartnerFiredCounts'].append( "%s: %s"%(code,player['PartnerFiredCounts'][code]) )

    if len(player['PartnerPassedCounts']):
      playerData['PartnerPassedCounts'] = []
      for code in player['PartnerPassedCounts']:
        playerData['PartnerPassedCounts'].append( "%s: %s"%(code,player['PartnerPassedCounts'][code]) )

    if len(player['PlayerNeedModifications']):
      playerData['PlayerNeedModifications'] = []
      for code in player['PlayerNeedModifications']:
        playerData['PlayerNeedModifications'].append( "%s: %s"%(code,player['PlayerNeedModifications'][code]) )

    for code in player['PlayerSkillModifications']:
      skillMods = []
      if int(player['PlayerSkillModifications'][code]) > 0:
        skillMods.append( "%s: %s"%(code,player['PlayerSkillModifications'][code]) )
    if len(skillMods):
      playerData['PlayerSkillModifications'] = skillMods

    printData[player['Code']] = playerData

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
