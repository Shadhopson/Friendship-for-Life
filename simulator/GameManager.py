import random
import json
import csv
import os
import re

def d(target):
  try:
    print json.dumps( target, sort_keys=False, indent=2 )
  except:
    out = { 'out': target }
    try:
      print json.dumps( out, sort_keys=False, indent=2 )
    except:
      print target

gameManagerPath = os.path.dirname(os.path.realpath(__file__))

from DataManager import DataManager

"""
" Card Classes 
"   used by simulator. Initializes card stats from the database
"""
class PlayerCard(object):
  def __init__(self, code ):
    self.code = code
    self.skills = DataManager.getRows( "SELECT * FROM PlayerSkill WHERE PlayerCode=?", [code] )
    self.needs = DataManager.getRows( "SELECT * FROM PlayerNeed WHERE PlayerCode=?", [code] )

  def __str__(self):
    ret = self.code;
    skill_arr = []
    for skill in self.skills:
      skill_arr.append( "%s:%d"%(skill['SkillCode'],skill['Value']) )
    if len(skill_arr):
      ret = "%s - Skills:[%s]"%(ret, ", ".join(skill_arr ) )
    need_arr = []
    for need in self.needs:
      need_arr.append( "%s:%d"%(need['NeedCode'],need['Value']) )
    if len(need_arr):
      ret = "%s - Needs:[%s]"%(ret, ", ".join(need_arr ) )

    return ret

  def jsonData(self):
    playerData = {}
    playerData['Code'] = self.code
    playerData['Label'] = str(self)
    playerData['Needs'] = {}
    for need in self.needs:
      playerData['Needs'][need['NeedCode']] = need['Value']
    playerData['Skills'] = {}
    for skill in self.skills:
      playerData['Skills'][skill['SkillCode']] = skill['Value']
    return playerData


class HobbyCard(object):
  def __init__(self, code ):
    hobby_row = DataManager.getRow( "SELECT * FROM Hobby WHERE HobbyCode=?", [code] )

    self.code = code
    self.expense = hobby_row['Expense']
    self.skills = DataManager.getRows( "SELECT * FROM HobbySkill WHERE HobbyCode=?", [code] )
    self.needs = DataManager.getRows( "SELECT * FROM HobbyNeed WHERE HobbyCode=?", [code] )

  def __str__(self):
    ret = self.code;
    skill_arr = []
    for skill in self.skills:
      skill_arr.append( "%s:%d"%(skill['SkillCode'],skill['Value']) )
    if len(skill_arr):
      ret = "%s - Skills:[%s]"%(ret, ", ".join(skill_arr ) )
    need_arr = []
    for need in self.needs:
      need_arr.append( "%s:%d"%(need['NeedCode'],need['Value']) )
    if len(need_arr):
      ret = "%s - Needs:[%s]"%(ret, ", ".join(need_arr ) )
    if self.expense:
      ret = "%s - Expense:%s"%(ret,self.expense)

    return ret

  def jsonData(self):
    hobbyData = {}
    hobbyData['Code'] = self.code
    hobbyData['Label'] = str(self)
    hobbyData['Needs'] = {}
    for need in self.needs:
      hobbyData['Needs'][need['NeedCode']] = need['Value']
    hobbyData['Skills'] = {}
    for skill in self.skills:
      hobbyData['Skills'][skill['SkillCode']] = skill['Value']
    return hobbyData


class ChildCard(object):
  def __init__(self, code ):
    child_row = DataManager.getRow( "SELECT * FROM Child WHERE ChildCode=?", [code] )

    self.code = code
    self.cost = child_row['Cost']
    self.skills = DataManager.getRows( "SELECT * FROM ChildSkill WHERE ChildCode=?", [code] )
    self.needs = DataManager.getRows( "SELECT * FROM ChildNeed WHERE ChildCode=?", [code] )

  def __str__(self):
    ret = self.code;
    skill_arr = []
    for skill in self.skills:
      skill_arr.append( "%s:%d"%(skill['SkillCode'],skill['Value']) )
    if len(skill_arr):
      ret = "%s - Skills:[%s]"%(ret, ", ".join(skill_arr ) )
    need_arr = []
    for need in self.needs:
      need_arr.append( "%s:%d"%(need['NeedCode'],need['Value']) )
    if len(need_arr):
      ret = "%s - Needs:[%s]"%(ret, ", ".join(need_arr ) )
    if self.cost:
      ret = "%s - Expense:%s"%(ret,self.cost)

    return ret

  def jsonData(self):
    childData = {}
    childData['Code'] = self.code
    childData['Label'] = str(self)
    childData['Needs'] = {}
    for need in self.needs:
      childData['Needs'][need['NeedCode']] = need['Value']
    childData['Skills'] = {}
    for skill in self.skills:
      childData['Skills'][skill['SkillCode']] = skill['Value']
    childData['Cost'] = self.cost
    return childData

class JobCard(object):
  def __init__(self, code ):
    job_row = DataManager.getRow( "SELECT * FROM Job WHERE JobCode=?", [code] )

    self.code = code
    self.pay = job_row['Pay']
    self.skillRequirements = DataManager.getRows( "SELECT * FROM JobSkillRequirement WHERE JobCode=?", [code] )
    self.needs = DataManager.getRows( "SELECT * FROM JobNeed WHERE JobCode=?", [code] )

  def onAdd(self):
    if self.code == 'Artist':
      self.pay = random.randint(1,6)
    elif self.code == 'SportPlayer':
      roll = random.randint(1,6)
      if roll == 6:
        self.pay = 8
      else:
        self.pay = 1

  def __str__(self):
    ret = self.code;
    skill_arr = []
    for skill in self.skillRequirements:
      skill_arr.append( "%s:%d"%(skill['SkillCode'],skill['Value']) )
    if len(skill_arr):
      ret = "%s - Skill Req:[%s]"%(ret, ", ".join(skill_arr ) )
    need_arr = []
    for need in self.needs:
      need_arr.append( "%s:%d"%(need['NeedCode'],need['Value']) )
    if len(need_arr):
      ret = "%s - Needs:[%s]"%(ret, ", ".join(need_arr ) )
    if self.pay:
      ret = "%s - Pay:%s"%(ret,self.pay)

    return ret

  def jsonData(self):
    jobData = {}
    jobData['Code'] = self.code
    jobData['Label'] = str(self)
    jobData['Needs'] = {}
    for need in self.needs:
      jobData['Needs'][need['NeedCode']] = need['Value']
    jobData['SkillRequirements'] = {}
    for skill in self.skillRequirements:
      jobData['SkillRequirements'][skill['SkillCode']] = skill['Value']

    jobData['Pay'] = self.pay
    return jobData

class PartnerCard(object):
  def __init__(self, code ):
    partner_row = DataManager.getRow( "SELECT * FROM Partner WHERE PartnerCode=?", [code] )

    self.code = code
    self.finances = partner_row['Finances']
    self.moneyRequirement = partner_row['MoneyRequirement']
    self.skillRequirements = DataManager.getRows( "SELECT * FROM PartnerSkillRequirement WHERE PartnerCode=?", [code] )
    self.needs = DataManager.getRows( "SELECT * FROM PartnerNeed WHERE PartnerCode=?", [code] )

  def jsonData(self):
    partnerData = {}
    partnerData['Code'] = self.code
    partnerData['Label'] = str(self)
    partnerData['Needs'] = {}
    for need in self.needs:
      partnerData['Needs'][need['NeedCode']] = need['Value']
    partnerData['SkillRequirements'] = {}
    for skill in self.skillRequirements:
      partnerData['SkillRequirements'][skill['SkillCode']] = skill['Value']
    partnerData['MoneyRequirement'] = self.moneyRequirement
    partnerData['Finances'] = self.finances
    return partnerData

  def __str__(self):
    ret = self.code;
    skill_arr = []
    for skill in self.skillRequirements:
      skill_arr.append( "%s:%d"%(skill['SkillCode'],skill['Value']) )
    if len(skill_arr):
      ret = "%s - Skill Req:[%s]"%(ret, ", ".join(skill_arr ) )
    if self.moneyRequirement:
      ret = "%s - Money Req:%s"%(ret,self.finances)
    need_arr = []
    for need in self.needs:
      need_arr.append( "%s:%d"%(need['NeedCode'],need['Value']) )
    if len(need_arr):
      ret = "%s - Needs:[%s]"%(ret, ", ".join(need_arr ) )
    if self.finances:
      ret = "%s - Finances:%s"%(ret,self.finances)

    return ret

"""
" Player Class 
"   keeps track of current state info of a player and provides methods for retreiving 
"   info and changing player state 
"""
class Player(object):

  def __init__(self, playerCard, money, trustTokens ):
    self.playerCard = playerCard
    self.playerSkillModifications = {}
    self.playerNeedModifications = {}
    self.money = money
    self.bankruptcyCounter = 0
    self.trustTokens = trustTokens
    self.children = []
    self.partners = []
    self.partnerSkillModifications = {}
    self.partnerFiredCounts = {}
    self.partnerPassedCounts = {}
    self.hobbies = []
    self.jobs = []
    self.jobPayModifications = {}
    self.jobSkillModifications = {}
    self.jobFiredCounts = {}
    self.jobPassedCounts = {}
    self.skillKnowledge = {}
    self.needKnowledge = []

    for skill in self.playerCard.skills:
      self.playerSkillModifications[skill['SkillCode']] = 0

  # adds a + or - modifier to a player's need 
  def modifyNeed( self, needCode, value ):
    if needCode not in self.playerNeedModifications:
      self.playerNeedModifications[needCode] = 0
    self.playerNeedModifications[needCode] += value

  # adds a + or - modifier to a player's need 
  def modifySkill( self, skillCode, value ):
    if skillCode not in self.playerSkillModifications:
      self.playerSkillModifications[skillCode] = 0
    self.playerSkillModifications[skillCode] += value

  # adds a + or - modifier to a jobs's  required skill
  def modifyJobSkill( self, job, skillCode, value ):
    if job.code not in self.jobSkillModifications:
      self.jobSkillModifications[job.code] = {}
    if skillCode not in self.jobSkillModifications[job.code]:
      self.jobSkillModifications[job.code][skillCode] = 0
    self.jobSkillModifications[job.code][skillCode] += value

  # adds a + or - modifier to a jobs's  payment
  def modifyJobPayment( self, job, value ):
    if job.code not in self.jobPayModifications:
      self.jobPayModifications[job.code] = 0
    self.jobPayModifications[job.code] += value

  # adds a + or - modifier to a partners's  required skills
  def modifyPartnerSkill( self, partner, skillCode, value ):
    if partner.code not in self.partnerSkillModifications:
      self.partnerSkillModifications[partner.code] = {}
    if skillCode not in self.partnerSkillModifications[partner.code]:
      self.partnerSkillModifications[partner.code][skillCode] = 0
    self.partnerSkillModifications[partner.code][skillCode] += value

  # records that a player was fired from a job
  def logJobFired( self, job ):
    if job.code not in self.jobFiredCounts:
      self.jobFiredCounts[job.code] = 0
    self.jobFiredCounts[job.code] += 1 

  # records that a player passed a job check
  def logJobPassed( self, job ):
    if job.code not in self.jobPassedCounts:
      self.jobPassedCounts[job.code] = 0
    self.jobPassedCounts[job.code] += 1 

  # records that a player was dumped by a partner
  def logPartnerFired( self, partner ):
    if partner.code not in self.partnerFiredCounts:
      self.partnerFiredCounts[partner.code] = 0
    self.partnerFiredCounts[partner.code] += 1 

  # records that a player passed a relationship check
  def logPartnerPassed( self, partner ):
    if partner.code not in self.partnerPassedCounts:
      self.partnerPassedCounts[partner.code] = 0
    self.partnerPassedCounts[partner.code] += 1 

  # removes partner from player and resets that partner's modifiers
  def dropPartner( self, partner ):
    self.partners.remove(partner)
    if partner.code in self.partnerSkillModifications:
      self.partnerSkillModifications[partner.code] = {}

  # removes job from player and resets that job's modifiers
  def dropJob( self, job ):
    self.jobs.remove(job)
    if job.code in self.jobSkillModifications:
      self.jobSkillModifications[job.code] = {}
    if job.code in self.jobPayModifications:
      self.jobPayModifications[job.code] = 0

  # removes a hobby from player
  def dropHobby( self, hobby ):
    self.hobbies.remove(hobby)

  # gets players current need stats (after modifications)
  def needStats(self):
    stats = {}
    for need in self.playerCard.needs:
      val = need['Value']
      code = need['NeedCode']
      if code in self.playerNeedModifications:
        val += self.playerNeedModifications[code]
      stats[code] = val
    return stats

  # calculates how many points of each need player is currently fulfilling
  def needFulfillmentStats(self):
    stats = {}
    for job in self.jobs:
      for need in job.needs:
        if need['NeedCode'] not in stats:
          stats[need['NeedCode']] = 0
        stats[need['NeedCode']] += need['Value']

    for partner in self.partners:
      for need in partner.needs:
        if need['NeedCode'] not in stats:
          stats[need['NeedCode']] = 0
        stats[need['NeedCode']] += need['Value']

    for hobby in self.hobbies:
      for need in hobby.needs:
        if need['NeedCode'] not in stats:
          stats[need['NeedCode']] = 0
        stats[need['NeedCode']] += need['Value']

    for child in self.children:
      for need in child.needs:
        if need['NeedCode'] not in stats:
          stats[need['NeedCode']] = 0
        stats[need['NeedCode']] += need['Value']

    stats['Money'] = self.money

    return stats

  # calculates current # of points player has earned
  def points(self):
    needStats = self.needStats()
    needFulfillmentStats = self.needFulfillmentStats()
    points = 0
    for needStat in needStats:
      needVal = needStats[needStat]
      if needStat in needFulfillmentStats and needFulfillmentStats[needStat] >= needVal:
        if needStat == 'Money':
          points += 1
        else:
          points += needVal

    for job in self.jobs:
      jobRes = self.isJobCheckPass(job)
      if jobRes == 'exceed' or jobRes == 'pass':
        points += 1
      else:
        points -= 1
    
    for partner in self.partners:
      partnerRes = self.isPartnerCheckPass(partner)
      if partnerRes == 'exceed' or partnerRes == 'pass':
        points += 1
      else:
        points -= 1

    points -= self.bankruptcyCounter

    return points

  # gets players current stats (after modifications)
  def skillStats(self):
    stats = {}
    for skill in self.playerCard.skills:
      val = skill['Value']
      code = skill['SkillCode']
      val += self.playerSkillModifications[code]
      stats[code] =  val 
    for hobby in self.hobbies:
      for skill in hobby.skills:
        stats[skill['SkillCode']] += skill['Value']
    for child in self.children:
      for skill in child.skills:
        stats[skill['SkillCode']] += skill['Value']

    return stats

  # gets jobs required stats (after modifications)
  def jobSkillRequirements(self,job):
    reqs = {}
    for req in job.skillRequirements:
      val = req['Value']
      if job.code in self.jobSkillModifications and req['SkillCode'] in self.jobSkillModifications[job.code]:
        val += self.jobSkillModifications[job.code][req['SkillCode']]
      reqs[req['SkillCode']] = val 
    return reqs

  def partnerSkillRequirements(self,partner):
    reqs = {}
    for req in partner.skillRequirements:
      val = req['Value']
      if partner.code in self.partnerSkillModifications and req['SkillCode'] in self.partnerSkillModifications[partner.code]:
        val += self.partnerSkillModifications[partner.code][req['SkillCode']]
      reqs[req['SkillCode']] = val
    return reqs

  # checks if player passes a job check
  def isJobCheckPass(self,job):
    reqs = self.jobSkillRequirements(job)
    stats = self.skillStats()
    res = "pass"
    for req in reqs:
      if stats[req] > reqs[req]:
        res = "exceed"
      elif stats[req] < reqs[req]:
        res = "fail"
        break
    return res

  # checks if player passes a partner check
  def isPartnerCheckPass(self,partner):
    reqs = self.partnerSkillRequirements(partner)
    stats = self.skillStats()
    res = "pass"
    for req in reqs:
      if stats[req] > reqs[req]:
        res = "exceed"
      elif stats[req] < reqs[req]:
        res = "fail"
        break
    return res

  # checks if player passes a partner check
  def isNeedCheckPass(self,need):
    needs = self.needStats()
    res = "pass"
    for req in reqs:
      if stats[req] > reqs[req]:
        res = "exceed"
      elif stats[req] < reqs[req]:
        res = "fail"
        break
    return res

  # returns current level of time committed to cards
  def currentTime(self):
    time = 0
    if len(self.children):
      if GameManager.setting("isChildTimeFlat") == False:
        time = time * len(self.children)
      else:
        time = GameManager.setting("childTime")
    time += GameManager.setting("partnerTime") * len(self.partners)
    time += GameManager.setting("jobTime") * len(self.jobs)
    time += GameManager.setting("hobbyTime") * len(self.hobbies)
    return time

  # calculates how much a job pays you during night step
  def jobPayment(self,job):
    payment = job.pay
    if job.code in self.jobPayModifications:
      payment += self.jobPayModifications[job.code]
    return payment

  # calculates how your children cost you during night step
  def childrenExpenses(self):
    return len(self.children) * GameManager.setting("childExpense")

  # calculates how your hobbies cost you during night step
  def hobbyExpenses(self,hobby):
    return hobby.expense

  # calculates how your partners cost/provide you during night step
  def partnerFinances(self, partner):
    return partner.finances

  def jsonData(self):
    playerData = {}
    playerData['Code'] = self.playerCard.code

    playerData['TrustTokens'] = self.trustTokens
    playerData['Money'] = self.money
    playerData['CurrentTime'] = self.currentTime()

    playerData['Hobbies'] = []
    for hobby in self.hobbies:
      playerData['Hobbies'].append(hobby.jsonData())
    playerData['Partners'] = []
    for partner in self.partners:
      playerData['Partners'].append(partner.jsonData())
    playerData['Jobs'] = []
    for job in self.jobs:
      playerData['Jobs'].append(job.jsonData())
    playerData['Children'] = []
    for child in self.children:
      playerData['Children'].append(child.jsonData())

    playerData['PlayerCard'] = self.playerCard.jsonData()
    playerData['Points'] = self.points()
    playerData['PlayerSkillModifications'] = self.playerSkillModifications
    playerData['PlayerNeedModifications'] = self.playerNeedModifications
    playerData['BankruptcyCounter'] = self.bankruptcyCounter
    playerData['PartnerSkillModifications'] = self.partnerSkillModifications
    playerData['PartnerFiredCounts'] = self.partnerFiredCounts
    playerData['PartnerPassedCounts'] = self.partnerPassedCounts
    playerData['JobPayModifications'] = self.jobPayModifications
    playerData['JobSkillModifications'] = self.jobSkillModifications
    playerData['JobFiredCounts'] = self.jobFiredCounts
    playerData['JobPassedCounts'] = self.jobPassedCounts
    playerData['SkillKnowledge'] = self.skillKnowledge
    playerData['NeedKnowledge'] = self.needKnowledge

    return playerData

class Game(object):

  def __init__(self):

    self.decisionMaker = RandomDecisionMaker()

    self.playerCardDeck = []
    self.hobbyCardDeck = []
    self.partnerCardDeck = []
    self.childCardDeck = []
    self.jobCardDeck = []

    self.revealedHobbyCards = []
    self.revealedPartnerCards = []
    self.revealedJobCards = []

    self.players = []

    #Initialize and shuffle all decs
    playerCardRows = DataManager.getRows( "SELECT PlayerCode FROM Player" )
    for playerCard in playerCardRows:
      self.playerCardDeck.append( PlayerCard(playerCard['PlayerCode']) )

    hobbyCardRows = DataManager.getRows( "SELECT HobbyCode FROM Hobby" )
    for hobbyCard in hobbyCardRows:
      self.hobbyCardDeck.append( HobbyCard(hobbyCard['HobbyCode']) )

    partnerCardRows = DataManager.getRows( "SELECT PartnerCode FROM Partner" )
    for partnerCard in partnerCardRows:
      self.partnerCardDeck.append( PartnerCard(partnerCard['PartnerCode']) )

    childCardRows = DataManager.getRows( "SELECT ChildCode FROM Child" )
    for childCard in childCardRows:
      self.childCardDeck.append( ChildCard(childCard['ChildCode']) )

    jobCardRows = DataManager.getRows( "SELECT JobCode FROM Job" )
    for jobCard in jobCardRows:
      self.jobCardDeck.append( JobCard(jobCard['JobCode']) )

    self.resetGame()

  # returns game to start state and removes all players (must re-add players after you use this)
  def resetGame(self):

    for player in self.players:
      for child in player.children:
        self.childCardDeck.append(child)
      for job in player.jobs:
        self.jobCardDeck.append(job)
      for hobby in player.hobbies:
        self.hobbyCardDeck.append(hobby)
      for partner in player.partners:
        self.partnerCardDeck.append(partner)
      self.playerCardDeck.append(player.playerCard)

    random.shuffle( self.playerCardDeck )
    random.shuffle( self.hobbyCardDeck )
    random.shuffle( self.partnerCardDeck )
    random.shuffle( self.childCardDeck )
    random.shuffle( self.jobCardDeck )

    self.currentRound = 1
    self.currentPlayerIndex = 0
    self.totalRounds = GameManager.setting("totalRounds")
    self.steps = [ 'morning', 'evening', 'night' ]
    self.currentStep = 'morning'
    self.gameLog = []
    self.players = []
    self.revealedHobbyCards = []
    self.revealedPartnerCards = []
    self.revealedJobCards = []

  # Adds a player to the game by taking card out of player card dec
  # if playerCode is passed in, will search through deck instead of drawing the next card
  def addPlayer(self, playerCode=None, money=None):
    newPlayerCard = None
    if playerCode:
      for playerCard in self.playerCardDeck:
        if playerCard.code == playerCode:
          newPlayerCard = playerCard
          self.playerCardDeck.remove(playerCard)
          break
    else:
      newPlayerCard = self.playerCardDeck.pop()

    newPlayer = Player(newPlayerCard, GameManager.setting("startingMoney"), GameManager.setting("startingTrustTokens") )
    self.players.append( newPlayer )

    if self.currentPlayerIndex == None:
      self.currentPlayerIndex = 0

  def isNextStep( self ):
    return self.currentPlayerIndex != None

  def currentPlayer(self):
    if self.currentPlayerIndex != None:
      return self.players[self.currentPlayerIndex]

  # returns the available actions for the current player for the next step
  def nextStepAvailableActions( self ):
    ret = []
    if self.currentStep == 'morning':
      #for player in self.players:
      #  if player != self.currentPlayer() and self.currentPlayer().trustTokens > 0:
      #    ret.append( { 'action': 'hangOut', 'target': player.playerCard.code } )
      ret.append( { 'step': 'morning', 'action': 'hangOut' } )
      if self.currentPlayer().trustTokens > 0:
        ret.append( { 'step': 'morning', 'action': 'shareKnowledge', 'knowledgeType': 'skill' } )
        ret.append( { 'step': 'morning', 'action': 'shareKnowledge', 'knowledgeType': 'need' } )
      ret.append( { 'step': 'morning', 'action': 'pass' } )

    elif self.currentStep == 'evening':
      currentTime = self.currentPlayer().currentTime()
      if currentTime + GameManager.setting("jobTime") <= GameManager.setting("maxTime"):
        ret.append( { 'step': 'evening', 'action': 'jobSearch' } )
      if currentTime + GameManager.setting("hobbyTime") <= GameManager.setting("maxTime"):
        ret.append( { 'step': 'evening', 'action': 'hobbySearch' } )
      if currentTime + GameManager.setting("partnerTime") <= GameManager.setting("maxTime"):
        ret.append( { 'step': 'evening', 'action': 'partnerSearch' } )

      if GameManager.setting("isChildTimeFlat") and len(self.currentPlayer().children):
        ret.append( { 'step': 'evening', 'action': 'childAttempt' } )
      elif currentTime + GameManager.setting("childTime") <= GameManager.setting("maxTime"):
        ret.append( { 'step': 'evening', 'action': 'childAttempt' } )

      ret.append( { 'step': 'evening', 'action': 'pass' } )

    elif self.currentStep == 'night':
      ret.append( { 'step': 'night', 'action': 'pass' } )
      for job in self.currentPlayer().jobs:
        ret.append( {'step': 'night', 'action': 'quitJob', 'jobCard': job.code } )
      for hobby in self.currentPlayer().hobbies:
        ret.append( {'step': 'night', 'action': 'quitHobby', 'hobbyCard': hobby.code } )
      for partner in self.currentPlayer().partners:
        ret.append( {'step': 'night', 'action': 'quitPartner', 'partnerCard': partner.code } )

    elif self.currentStep == 'jobSearch':
      for i in self.revealedJobCards:
        ret.append( {'step': 'jobSearch', 'action':i.code} )
      ret.append( {'step': 'jobSearch', 'action': 'pass' } )

    elif self.currentStep == 'partnerSearch':
      for i in self.revealedPartnerCards:
        ret.append( {'step': 'partnerSearch', 'action':i.code} )
      ret.append( {'step': 'partnerSearch', 'action': 'pass' } )

    elif self.currentStep == 'hobbySearch':
      for i in self.revealedHobbyCards:
        ret.append( {'step': 'hobbySearch', 'action':i.code} )
      ret.append( {'step': 'hobbySearch', 'action': 'pass' } )

    return ret

  # performs the next step using the action specified
  # action= the index of the action returned from nextStepAvailableActions()
  def performNextStep( self, action=None ):

    #log players
    self.logPlayers()

    #init action log
    log = { "Round": self.currentRound, "Player": self.currentPlayer().playerCard.code, 'CurrentStep': self.currentStep }
    log['Type'] = 'Action'
    if action != None:
      action_ops = self.nextStepAvailableActions()
      action = action_ops[action]
      log["Decision"] = action
    else:
      raise ValueError( self.nextStepAvailableActions() )

    nextStep = None
    if self.currentStep == 'morning':
      nextStep = 'evening'
    elif self.currentStep == 'evening':
      nextStep = 'night'
    elif self.currentStep == 'jobSearch':
      nextStep = 'night'
    elif self.currentStep == 'partnerSearch':
      nextStep = 'night'
    elif self.currentStep == 'hobbySearch':
      nextStep = 'night'

    #perform action
    if action['action'] == 'hangOut' or \
        (self.currentStep == 'morning' and GameManager.setting('forceShareKnowledge') and self.currentPlayer().trustTokens < 1):
      self.currentPlayer().trustTokens += 1

    elif action['action'] == 'shareKnowledge' or \
        (self.currentStep == 'morning' and GameManager.setting('forceShareKnowledge') ):

      #figure out what skills and needs this player hasn't been told
      self.currentPlayer().trustTokens -= 1
      neededSkillInfo = [] 
      neededNeedInfo = []
      for skill in self.currentPlayer().playerCard.skills:
        if action['knowledgeType'] == 'skill' and skill['SkillCode'] not in self.currentPlayer().skillKnowledge.keys():
          neededSkillInfo.append( skill['SkillCode'] )
      for need in self.currentPlayer().playerCard.needs:
        if action['knowledgeType'] == 'need' and need['NeedCode'] not in self.currentPlayer().needKnowledge:
          neededNeedInfo.append( need['NeedCode'] )

      # randomly select either skill or need (if both still are needed)
      choices = []
      if len(neededSkillInfo):
        choices.append("skill")
      if len(neededNeedInfo):
        choices.append("need")
      choice = choices[random.randint(0,len(choices)-1)]

      # share skill info
      if choice == 'skill':
        skill = neededSkillInfo[random.randint(0,len(neededSkillInfo)-1)]

        playerSkills = self.currentPlayer().skillStats()
        if playerSkills[skill] > 3:
          self.currentPlayer().skillKnowledge[skill] = 'high'
        elif playerSkills[skill] > 1:
          self.currentPlayer().skillKnowledge[skill] = 'medium'
        else:
          self.currentPlayer().skillKnowledge[skill] = 'low'

      # share need info
      elif choice == 'need':
        need = neededNeedInfo[random.randint(0,len(neededNeedInfo)-1)]
        self.currentPlayer().needKnowledge.append(need)

    elif action['action'] == 'jobSearch':
      for i in range(GameManager.setting("jobSearchNumCards")):
        nextJobCard = self.jobCardDeck.pop()
        self.revealedJobCards.append(nextJobCard)
      nextStep = 'jobSearch'

    elif action['step'] == 'jobSearch':
      for i in self.revealedJobCards:
        if action['action'] <> 'pass' and i.code == action['action']:
          self.currentPlayer().jobs.append( i )
          i.onAdd()
        else:
          self.jobCardDeck.insert( 0,i )
      self.revealedJobCards = []

    elif action['action'] == 'partnerSearch':
      for i in range(GameManager.setting("partnerSearchNumCards")):
        nextPartnerCard = self.partnerCardDeck.pop()
        self.revealedPartnerCards.append(nextPartnerCard)
      nextStep = 'partnerSearch'

    elif action['step'] == 'partnerSearch':
      for i in self.revealedPartnerCards:
        if action['action'] <> 'pass' and i.code == action['action']:
          self.currentPlayer().partners.append( i )
        else:
          self.partnerCardDeck.insert( 0,i )
      self.revealedPartnerCards = []


    elif action['action'] == 'hobbySearch':
      for i in range(GameManager.setting("hobbySearchNumCards")):
        nextHobbyCard = self.hobbyCardDeck.pop()
        self.revealedHobbyCards.append(nextHobbyCard)
      nextStep = 'hobbySearch'

    elif action['step'] == 'hobbySearch':
      for i in self.revealedHobbyCards:
        if action['action'] <> 'pass' and i.code == action['action']:
          self.currentPlayer().hobbies.append( i )
        else:
          self.hobbyCardDeck.insert( 0,i )
      self.revealedHobbyCards = []

    elif action['action'] == 'childAttempt':
      roll = random.randint(1,GameManager.setting("childAttemptDiceSides"))
      if roll >= GameManager.setting("childAttemptMinSuccess"):
        nextChildCard = self.childCardDeck.pop()
        self.currentPlayer().children.append(nextChildCard)

    elif action['action'] == 'quitJob':
      for job in self.currentPlayer().jobs:
        if job.code == action['jobCard']:
          self.currentPlayer().dropJob(job)
          self.jobCardDeck.insert(0,job)

    elif action['action'] == 'quitHobby':
      for hobby in self.currentPlayer().hobbies:
        if hobby.code == action['hobbyCard']:
          self.currentPlayer().dropHobby(hobby)
          self.hobbyCardDeck.insert(0,hobby)

    elif action['action'] == 'quitPartner':
      for partner in self.currentPlayer().partners:
        if partner.code == action['partnerCard']:
          self.currentPlayer().dropPartner(partner)
          self.partnerCardDeck.insert(0,partner)

    # EVENT ROLL (if evening)
    if self.currentStep == 'evening':
      eventRoll = random.randint( 0, 20 )
      if eventRoll in GameManager.setting('eventRollPromotion'):
        log["eventRoll"] = "Promotion" 
        if len(self.currentPlayer().jobs):
          jobIndex = random.randint( 0,len(self.currentPlayer().jobs)-1 )
          job = self.currentPlayer().jobs[jobIndex]
          stat = random.choice( self.currentPlayer().skillStats().keys() )
          self.currentPlayer().modifySkill( stat, 1 )
          self.currentPlayer().modifyJobPayment( job, 1 )

      elif eventRoll in GameManager.setting('eventRollJobSkillIncrease'):
        log["eventRoll"] = "JobSkillIncrease" 
        if len(self.currentPlayer().jobs):
          jobIndex = random.randint( 0,len(self.currentPlayer().jobs)-1 )
          job = self.currentPlayer().jobs[jobIndex]
          jobStats = self.currentPlayer().jobSkillRequirements(job)
          stat = random.choice( jobStats.keys() )
          self.currentPlayer().modifyJobSkill( job, stat, 1 )

      elif eventRoll in GameManager.setting('eventRollPartnerSkillIncrease'):
        log["eventRoll"] = "PartnerSkillIncrease" 
        if len(self.currentPlayer().partners):
          partnerIndex = random.randint( 0,len(self.currentPlayer().partners)-1 )
          partner = self.currentPlayer().partners[partnerIndex]
          partnerStats = self.currentPlayer().partnerSkillRequirements(partner)
          stat = random.choice( partnerStats.keys() )
          self.currentPlayer().modifyPartnerSkill( partner, stat, 1 )

      elif eventRoll in GameManager.setting('eventRollJobCheckIn'):
        log["eventRoll"] = "JobCheckIn" 
        if len(self.currentPlayer().jobs):
          jobIndex = random.randint( 0,len(self.currentPlayer().jobs)-1 )
          job = self.currentPlayer().jobs[jobIndex]
          isPass = self.currentPlayer().isJobCheckPass(job)
          log[ "jobCheckRes"] = "%s - %s"%(job.code,isPass) 
          if isPass == 'pass':
            self.currentPlayer().logJobPassed(job)
          elif isPass == 'exceed':
            self.currentPlayer().modifyJobPayment( job, 1 )
            self.currentPlayer().logJobPassed(job)
            log["jobPayIncrease"] =  job.code 
          else:
            self.currentPlayer().dropJob(job)
            self.currentPlayer().logJobFired(job)
            self.jobCardDeck.insert(0,job)
            log["firedFromJob"] =  job.code 

      elif eventRoll in GameManager.setting('eventRollRelationshipCheckIn'):
        log["eventRoll"] = "RelationshipCheckIn" 
        if len(self.currentPlayer().partners):
          partnerIndex = random.randint( 0,len(self.currentPlayer().partners)-1 )
          partner = self.currentPlayer().partners[partnerIndex]
          isPass = self.currentPlayer().isPartnerCheckPass(partner)
          log[ "partnerCheckRes"] = "%s - %s"%(partner.code,isPass) 
          if isPass == 'pass':
            self.currentPlayer().logPartnerPassed(partner)
          elif isPass == 'exceed':
            self.currentPlayer().logPartnerPassed(partner)
          else:
            self.currentPlayer().logPartnerFired(partner)
            self.currentPlayer().dropPartner(partner)
            self.partnerCardDeck.insert(0,partner)
            log[ "firedFromPartner"] =  partner.code 

      elif eventRoll in GameManager.setting('eventRollFriendFight'):
        log["eventRoll"] = "FriendFight" 
        if self.currentPlayer().trustTokens > 0:
          self.currentPlayer().trustTokens -= 1

      elif eventRoll in GameManager.setting('eventRollRelativeDeath'):
        log["eventRoll"] = "RelativeDeath" 

      elif eventRoll in GameManager.setting('eventRollReferral'):
        log["eventRoll"] = "Referral" 
      elif eventRoll in GameManager.setting('eventRollLoan'):
        log["eventRoll"] = "RollLoan" 
      elif eventRoll in GameManager.setting('eventRollUnexpectedChild'):
        log["eventRoll"] = "UnexpectedChild" 
      elif eventRoll in GameManager.setting('eventRollAdopt'):
        log["eventRoll"] = "Adopt" 
      elif eventRoll in GameManager.setting('eventRollStatMinus'):
        log["eventRoll"] = "StatMinus" 
      elif eventRoll in GameManager.setting('eventRollStatPlus'):
        log["eventRoll"] = "StatPlus" 
      else:
        log["eventRoll"] = "Nothing" 


    # If night: Update players money based upon current jobs, children, partners, and hobbies 
    #   Also, update games player log
    if self.currentStep == 'night':

      nightStartMoney = self.currentPlayer().money

      # get paid
      for job in self.currentPlayer().jobs:
        self.currentPlayer().money += self.currentPlayer().jobPayment(job)

      # pay for children
      self.currentPlayer().money -= self.currentPlayer().childrenExpenses()

      # pay for life
      self.currentPlayer().money -= GameManager.setting("baseLifeExpense")

      # pay for hobbies 
      for hobby in self.currentPlayer().hobbies:
        self.currentPlayer().money -= self.currentPlayer().hobbyExpenses(hobby)

      # partner finances
      for partner in self.currentPlayer().partners:
        self.currentPlayer().money += self.currentPlayer().partnerFinances(partner)

      if self.currentPlayer().money < 0:
        self.currentPlayer().money = nightStartMoney 
        self.currentPlayer().bankruptcyCounter += 1

      # add on the 'round end points' to the game log 
      for gLog in reversed(self.gameLog):
        if gLog['Type'] == 'GameState':
          if 'EndPoints' in gLog:
            break
          else:
            for player in self.players:
              if player.playerCard.code == gLog['PlayerCode']:
                gLog['EndPoints'] = player.points()
                break;

    # record action
    self.gameLog.append(log)

    #move to next step
    if self.currentStep != 'night':
      self.currentStep = nextStep

    else:

      if self.currentPlayerIndex+1 < len(self.players):
        self.currentPlayerIndex += 1
      elif self.currentRound < self.totalRounds:
        self.currentPlayerIndex = 0
        self.currentRound += 1
      # END GAME
      else:
        self.currentPlayerIndex = None
        self.logPlayers()

      self.currentStep = 'morning'

  # adds all players current state to the game log
  def logPlayers( self ):
    for player in self.players:
      log = {}
      log["Type"] = "GameState"
      log["Points"] = player.points()
      log['PlayerCode']  = player.playerCard.code
      log['Time']  = player.currentTime()
      log['Round']  = self.currentRound
      log['Step']  = self.currentStep
      log["Money"] = player.money
      log["TrustTokens"] = player.trustTokens

      log["NeedMods"] = {}
      for needMod in player.playerNeedModifications:
        log["NeedMods"][needMod] = player.playerNeedModifications[needMod]

      log["Partners"] = []
      for partner in player.partners:
        log["Partners"].append( partner.code )

      log["PartnerSkillMods"] = {}
      for partnerCode in player.partnerSkillModifications:
        log["PartnerSkillMods"][partnerCode] = {}
        for skillCode in player.partnerSkillModifications[partnerCode]:
          log["PartnerSkillMods"][partnerCode][skillCode] = player.partnerSkillModifications[partnerCode][skillCode]

      log["PartnerFiredCounts"] = {}
      for partnerCode in player.partnerFiredCounts:
        log["PartnerFiredCounts"][partnerCode] = player.partnerFiredCounts[partnerCode]

      log["PartnerPassedCounts"] = {}
      for partnerCode in player.partnerPassedCounts:
        log["PartnerPassedCounts"][partnerCode] = player.partnerPassedCounts[partnerCode]

      log["Children"] = []
      for child in player.children:
        log["Children"].append( child.code )

      log["SkillMods"] = {}
      for skillMod in player.playerSkillModifications:
        log["SkillMods"][skillMod] = player.playerSkillModifications[skillMod]

      log["Hobbies"] = []
      for hobby in player.hobbies:
        log["Hobbies"].append( hobby.code )

      log["Jobs"] = []
      for job in player.jobs:
        log["Jobs"].append( {"JobCode": job.code, "Pay": job.pay } )

      log["JobPayMods"] = {}
      for jobCode in player.jobPayModifications:
        log["JobPayMods"][jobCode] = player.jobPayModifications[jobCode]

      log["JobSkillMods"] = {}
      for jobCode in player.jobSkillModifications:
        log["JobSkillMods"][jobCode] = {}
        for skillCode in player.jobSkillModifications[jobCode]:
          log["JobSkillMods"][jobCode][skillCode] = player.jobSkillModifications[jobCode][skillCode]

      log["JobFiredCounts"] = {}
      for jobCode in player.jobFiredCounts:
        log["JobFiredCounts"][jobCode] = player.jobFiredCounts[jobCode]

      log["JobPassedCounts"] = {}
      for jobCode in player.jobPassedCounts:
        log["JobPassedCounts"][jobCode] = player.jobPassedCounts[jobCode]

      log["SkillKnowledge"] = {}
      for skill in player.skillKnowledge:
        log["SkillKnowledge"][skill] = player.skillKnowledge[skill]

      log["NeedKnowledge"] = []
      for need in player.needKnowledge:
        log["NeedKnowledge"].append( need )

      self.gameLog.append( log )

  def jsonData(self):
    outData = {}
    outData['Players'] = []
    for player in self.players:
      outData['Players'].append(player.jsonData())

    outData['Round'] = self.currentRound
    outData['TotalRounds'] = GameManager.setting("totalRounds")
    outData['CurrentStep'] = self.currentStep
    outData['RevealedHobbyCards'] = []
    for card in self.revealedHobbyCards:
      outData['RevealedHobbyCards'].append( card.jsonData() )
    outData['RevealedJobCards'] = []
    for card in self.revealedJobCards:
      outData['RevealedJobCards'].append( card.jsonData() )
    outData['RevealedPartnerCards'] = []
    for card in self.revealedPartnerCards:
      outData['RevealedPartnerCards'].append( card.jsonData() )

    if self.isNextStep():
      outData['Actions'] = self.nextStepAvailableActions()
    else:
      outData['Actions'] = None

    return outData

class GameManager(object):
  settings = []
  settingFilePath = 'GameManager.json'

  #Manages class settings loaded from GameManager.json
  @staticmethod
  def setting(pSettingName):
    if len(GameManager.settings) == 0:
      jsonFile = open( gameManagerPath+"/"+GameManager.settingFilePath )
      try: 
        GameManager.settings = json.loads(jsonFile.read())
      except ValueError, e:
        print "INVALID JSON SETTINGS FILE - EXITING"
        exit()
    if pSettingName in GameManager.settings:
      return GameManager.settings[pSettingName]
    else:
      return None

  @staticmethod
  def playGames( pDecisionMaker=None, pPlayerCodes=[], pNumRounds=1000, pOutPath='.' ):

    outPath = pOutPath

    DataManager.initSettings()
    DataManager.settings['gameResultsDbPath'] = "%s/games.db"%(outPath)
    DataManager.createGameDb()

    game = Game()
    if pDecisionMaker != None:
      game.decisionMaker = pDecisionMaker

    playerCodes = pPlayerCodes
    if len(playerCodes) == 0:
      for card in game.playerCardDeck:
        playerCodes.append( card.code )

    playerCodes = sorted(playerCodes)

    scores = []
    playerScores = {}
    DataManager.clearGameLogDb()
    for code in playerCodes:
      playerScores[code] = []
      for j in range(pNumRounds):
        if j%10 == 0:
          print "%s: Round %d"%(code,j)
        game.resetGame()
        game.addPlayer( code )
        while game.isNextStep():
          game.performNextStep( game.decisionMaker.makeDecision( game, game.nextStepAvailableActions() ) )
        DataManager.insertGameLogIntoDb(game.gameLog)
        scores.append( game.players[0].points() )
        playerScores[code].append( game.players[0].points() )

    DataManager.closeConnection("gameConn")

    line = "Avg Score: %.2f"%( sum(scores) / float(len(scores) ) )
    fileOut  = open( "%s/results.txt"%(outPath), 'wb' )
    fileOut.write( line+'\n' );
    print line
    for player in sorted(playerScores):
      line = "%s Avg Score: %.2f"%(player, sum(playerScores[player]) / float(len(playerScores[player]))) 
      print line
      fileOut.write( line+'\n' )


class RandomDecisionMaker:
  def makeDecision( self, game, options ):
    choice = random.randint(0,len(options)-1)
    return choice


