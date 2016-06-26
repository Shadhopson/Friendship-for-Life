import random
import json
import csv

from DataManager import DataManager

class PlayerCard(object):
  def __init__(self, code ):
    self.code = code
    self.skills = DataManager.getRows( "SELECT * FROM PlayerSkill WHERE PlayerCode=?", [code] )
    self.needs = DataManager.getRows( "SELECT * FROM PlayerNeed WHERE PlayerCode=?", [code] )


class HobbyCard(object):
  def __init__(self, code ):
    self.code = code
    self.skills = DataManager.getRows( "SELECT * FROM HobbySkill WHERE HobbyCode=?", [code] )
    self.needs = DataManager.getRows( "SELECT * FROM HobbyNeed WHERE HobbyCode=?", [code] )


class ChildCard(object):
  def __init__(self, code ):
    child_row = DataManager.getRow( "SELECT * FROM Child WHERE ChildCode=?", [code] )

    self.code = code
    self.cost = child_row['Cost']
    self.skills = DataManager.getRows( "SELECT * FROM ChildSkill WHERE ChildCode=?", [code] )
    self.needs = DataManager.getRows( "SELECT * FROM ChildNeed WHERE ChildCode=?", [code] )


class JobCard(object):
  def __init__(self, code ):
    job_row = DataManager.getRow( "SELECT * FROM Job WHERE JobCode=?", [code] )

    self.code = code
    self.pay = job_row['Pay']
    self.skillRequirements = DataManager.getRows( "SELECT * FROM JobSkillRequirement WHERE JobCode=?", [code] )
    self.needs = DataManager.getRows( "SELECT * FROM JobNeed WHERE JobCode=?", [code] )

    if self.code == 'Artist':
      self.pay = random.randint(1,6)
    elif self.code == 'SportPlayer':
      roll = random.randint(1,6)
      if roll == 6:
        self.pay = 8
      else:
        self.pay = 1

class PartnerCard(object):
  def __init__(self, code ):
    partner_row = DataManager.getRow( "SELECT * FROM Partner WHERE PartnerCode=?", [code] )

    self.code = code
    self.finances = partner_row['Finances']
    self.moneyRequirement = partner_row['MoneyRequirement']
    self.skillRequirements = DataManager.getRows( "SELECT * FROM PartnerSkillRequirement WHERE PartnerCode=?", [code] )
    self.needs = DataManager.getRows( "SELECT * FROM PartnerNeed WHERE PartnerCode=?", [code] )

class Player(object):

  def __init__(self, playerCard, money, trustTokens ):
    self.playerCard = playerCard
    self.playerSkillModifications = {}
    self.playerNeedModifications = {}
    self.money = money
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

    for skill in self.playerCard.skills:
      self.playerSkillModifications[skill['SkillCode']] = 0

  def modifyNeed( self, needCode, value ):
    if needCode not in self.playerNeedModifications:
      self.playerNeedModifications[needCode] = 0
    self.playerNeedModifications[needCode] += value

  def modifySkill( self, skillCode, value ):
    if skillCode not in self.playerSkillModifications:
      self.playerSkillModifications[skillCode] = 0
    self.playerSkillModifications[skillCode] += value

  def modifyJobSkill( self, job, skillCode, value ):
    if job.code not in self.jobSkillModifications:
      self.jobSkillModifications[job.code] = {}
    if skillCode not in self.jobSkillModifications[job.code]:
      self.jobSkillModifications[job.code][skillCode] = 0
    self.jobSkillModifications[job.code][skillCode] += value

  def modifyJobPayment( self, job, value ):
    if job.code not in self.jobPayModifications:
      self.jobPayModifications[job.code] = 0
    self.jobPayModifications[job.code] += value

  def modifyPartnerSkill( self, partner, skillCode, value ):
    if partner.code not in self.partnerSkillModifications:
      self.partnerSkillModifications[partner.code] = {}
    if skillCode not in self.partnerSkillModifications[partner.code]:
      self.partnerSkillModifications[partner.code][skillCode] = 0
    self.partnerSkillModifications[partner.code][skillCode] += value

  def logJobFired( self, job ):
    if job.code not in self.jobFiredCounts:
      self.jobFiredCounts[job.code] = 0
    self.jobFiredCounts[job.code] += 1 

  def logJobPassed( self, job ):
    if job.code not in self.jobPassedCounts:
      self.jobPassedCounts[job.code] = 0
    self.jobPassedCounts[job.code] += 1 

  def logPartnerFired( self, partner ):
    if partner.code not in self.partnerFiredCounts:
      self.partnerFiredCounts[partner.code] = 0
    self.partnerFiredCounts[partner.code] += 1 

  def logPartnerPassed( self, partner ):
    if partner.code not in self.partnerPassedCounts:
      self.partnerPassedCounts[partner.code] = 0
    self.partnerPassedCounts[partner.code] += 1 

  def dropPartner( self, partner ):
    self.partners.remove(partner)
    if partner.code in self.partnerSkillModifications:
      self.partnerSkillModifications[partner.code] = {}

  def dropJob( self, job ):
    self.jobs.remove(job)
    if job.code in self.jobSkillModifications:
      self.jobSkillModifications[job.code] = {}
    if job.code in self.jobPayModifications:
      self.jobPayModifications[job.code] = 0

  def dropHobby( self, hobby ):
    self.hobbies.remove(hobby)

  # gets players current stats (after modifications)
  def needStats(self):
    stats = {}
    for need in self.playerCard.needs:
      val = need['Value']
      code = need['NeedCode']
      if code in self.playerNeedModifications:
        val += self.playerNeedModifications[code]
      stats[code] = val
    return stats

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

  def points(self):
    needStats = self.needStats()
    needFulfillmentStats = self.needFulfillmentStats()
    points = 0
    for needStat in needStats:
      needVal = needStats[needStat]
      if needStat in needFulfillmentStats:
        if needFulfillmentStats[needStat] >= needVal:
          points += 1 

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
    
    return points

  # gets players current stats (after modifications)
  def skillStats(self):
    stats = {}
    for skill in self.playerCard.skills:
      val = skill['Value']
      code = skill['SkillCode']
      val += self.playerSkillModifications[code]
      stats[code] =  val 
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
    time = GameManager.setting("childTime") * len(self.children)
    time += GameManager.setting("partnerTime") * len(self.partners)
    time += GameManager.setting("jobTime") * len(self.jobs)
    time += GameManager.setting("hobbyTime") * len(self.hobbies)
    return time

  def jobPayment(self,job):
    payment = job.pay
    if job.code in self.jobPayModifications:
      payment += self.jobPayModifications[job.code]
    return payment


class Game(object):

  def __init__(self):
    self.currentRound = 1
    self.currentPlayerIndex = 0
    self.totalRounds = GameManager.setting("totalRounds")
    self.steps = [ 'morning', 'evening', 'night' ]
    self.currentStep = 'morning'
    self.decisionMaker = RandomDecisionMaker()
    self.gameLog = []
    self.players = []

    self.playerCardDeck = []
    self.hobbyCardDeck = []
    self.partnerCardDeck = []
    self.childCardDeck = []
    self.jobCardDeck = []

    #Initialize and shuffle all decs
    playerCardRows = DataManager.getRows( "SELECT PlayerCode FROM Player" )
    for playerCard in playerCardRows:
      self.playerCardDeck.append( PlayerCard(playerCard['PlayerCode']) )
    random.shuffle( self.playerCardDeck )

    hobbyCardRows = DataManager.getRows( "SELECT HobbyCode FROM Hobby" )
    for hobbyCard in hobbyCardRows:
      self.hobbyCardDeck.append( HobbyCard(hobbyCard['HobbyCode']) )
    random.shuffle( self.hobbyCardDeck )

    partnerCardRows = DataManager.getRows( "SELECT PartnerCode FROM Partner" )
    for partnerCard in partnerCardRows:
      self.partnerCardDeck.append( PartnerCard(partnerCard['PartnerCode']) )
    random.shuffle( self.partnerCardDeck )

    childCardRows = DataManager.getRows( "SELECT ChildCode FROM Child" )
    for childCard in childCardRows:
      self.childCardDeck.append( ChildCard(childCard['ChildCode']) )
    random.shuffle( self.childCardDeck )

    jobCardRows = DataManager.getRows( "SELECT JobCode FROM Job" )
    for jobCard in jobCardRows:
      self.jobCardDeck.append( JobCard(jobCard['JobCode']) )
    random.shuffle( self.jobCardDeck )


  #Adds a player to the game by taking card out of player card dec
  #if playerCode is passed in, will search through deck instead of drawing the next card
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
    if self.isNextStep():
      return self.players[self.currentPlayerIndex]

  # returns the available actions for the current player for the next step
  def nextStepAvailableActions( self ):
    ret = []
    if self.currentStep == 'morning':
      for player in self.players:
        if player != self.currentPlayer():
          ret.append( { 'action': 'hangOut', 'target': player.playerCard.code } )
      ret.append( { 'action': 'pass' } )

    elif self.currentStep == 'evening':
      if self.currentPlayer().currentTime() + GameManager.setting("jobTime") <= GameManager.setting("maxTime"):
        ret.append( { 'action': 'jobSearch' } )
      if self.currentPlayer().currentTime() + GameManager.setting("hobbyTime") <= GameManager.setting("maxTime"):
        ret.append( { 'action': 'hobbySearch' } )
      if self.currentPlayer().currentTime() + GameManager.setting("partnerTime") <= GameManager.setting("maxTime"):
        ret.append( { 'action': 'partnerSearch' } )
      ret.append( { 'action': 'pass' } )

    elif self.currentStep == 'night':
      ret.append( { 'action': 'pass' } )
      for job in self.currentPlayer().jobs:
        ret.append( {'action': 'quitJob', 'jobCard': job.code } )
      for hobby in self.currentPlayer().hobbies:
        ret.append( {'action': 'quitHobby', 'hobbyCard': hobby.code } )
      for partner in self.currentPlayer().partners:
        ret.append( {'action': 'quitPartner', 'partnerCard': partner.code } )

    return ret

  # performs the next step using the action specified
  # action= the index of the action returned from nextStepAvailableActions()
  def performNextStep( self, action=None ):

    #create log
    log = { "round": self.currentRound, "player": self.currentPlayer().playerCard.code, 'currentStep': self.currentStep }
    if action != None:
      action_ops = self.nextStepAvailableActions()
      action = action_ops[action]
      log.update(action)
    else:
      raise ValueError( self.nextStepAvailableActions() )

    #perform action
    if action['action'] == 'hangOut':
      self.currentPlayer().trustTokens += 1
    elif action['action'] == 'jobSearch':
      actions = [{'action':'pass'}]
      revealedCards = []
      for i in range(GameManager.setting("jobSearchNumCards")):
        nextJobCard = self.jobCardDeck.pop()
        actions.append( {'action':'addJob','jobCard':nextJobCard} )
        revealedCards.append(nextJobCard)
      decision = self.decisionMaker.makeDecision( self, actions )
      actionResponse = actions[decision]
      for i in revealedCards:
        if actionResponse['action'] == 'addJob' and i == actionResponse['jobCard']:
          self.currentPlayer().jobs.append( i )
          log[ "addedJob"] = i.code 
        else:
          self.jobCardDeck.insert( 0,i )

    elif action['action'] == 'hobbySearch':
      actions = [{'action':'pass'}]
      revealedCards = []
      for i in range(GameManager.setting("hobbySearchNumCards")):
        nextHobbyCard = self.hobbyCardDeck.pop()
        actions.append( {'action':'addHobby','hobbyCard':nextHobbyCard} )
        revealedCards.append(nextHobbyCard)
      decision = self.decisionMaker.makeDecision( self, actions )
      actionResponse = actions[decision]
      for i in revealedCards:
        if actionResponse['action'] == 'addHobby' and i == actionResponse['hobbyCard']:
          self.currentPlayer().hobbies.append( i )
          log[ "addedHobby"] = i.code 
        else:
          self.hobbyCardDeck.insert( 0,i )

    elif action['action'] == 'partnerSearch':
      actions = [{'action':'pass'}]
      revealedCards = []
      for i in range(GameManager.setting("partnerSearchNumCards")):
        nextPartnerCard = self.partnerCardDeck.pop()
        revealedCards.append( nextPartnerCard )
        actions.append( {'action':'addPartner','partnerCard':nextPartnerCard} )
      decision = self.decisionMaker.makeDecision( self, actions )
      actionResponse = actions[decision]
      for i in revealedCards:
        if actionResponse['action'] == 'addPartner' and actionResponse['partnerCard'] == i:
          self.currentPlayer().partners.append( i )
          log[ "addedPartner"] = i.code 
        else:
          self.partnerCardDeck.insert( 0,i )

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


    if self.currentStep == 'night':
      # get paid
      for job in self.currentPlayer().jobs:
        self.currentPlayer().money += self.currentPlayer().jobPayment(job)

    #move to next step
    if self.currentStep == 'morning':
      self.currentStep = 'evening'
    elif self.currentStep == 'evening':
      self.currentStep = 'night'
    elif self.currentStep == 'night':
      if self.currentPlayerIndex+1 < len(self.players):
        self.currentPlayerIndex += 1
      elif self.currentRound < self.totalRounds:
        self.logPlayers()
        self.currentPlayerIndex = 0
        self.currentRound += 1
      # END GAME
      else:
        self.currentPlayerIndex = None
        self.logPlayers()

      self.currentStep = 'morning'

    self.gameLog.append(log)

  def logPlayers( self ):
    for player in self.players:
      log = {}
      log["Points"] = player.points()
      log['PlayerCode']  = player.playerCard.code
      log['Time']  = player.currentTime()
      log['Round']  = self.currentRound
      log['Step']  = self.currentStep
      log["Money"] = player.money
      log["TrustTokens"] = player.trustTokens

      skillStats = player.skillStats()
      for skill in skillStats:
        log["Skill_%s"%skill] = skillStats[skill]

      needStats = player.needStats()
      for need in needStats:
        log["Need_%s"%need] = needStats[need]

      for needMod in player.playerNeedModifications:
        log["NeedMod_%s"%needMod] = player.playerNeedModifications[needMod]

      fulfillmentStats = player.needFulfillmentStats()
      for need in fulfillmentStats:
        log["NeedFulfillment_%s"%need] = fulfillmentStats[need]

      for partner in player.partners:
        log["Partner_%s"%partner.code] = 1

      for partnerCode in player.partnerSkillModifications:
        for skillCode in player.partnerSkillModifications[partnerCode]:
          log["PartnerSkillMod_%s_%s"%(partnerCode,skillCode)] = player.partnerSkillModifications[partnerCode][skillCode]

      for partnerCode in player.partnerFiredCounts:
        log["PartnerFireCount_%s"%partnerCode] = player.partnerFiredCounts[partnerCode]

      for partnerCode in player.partnerPassedCounts:
        log["PartnerPassCount_%s"%partnerCode] = player.partnerPassedCounts[partnerCode]

      for child in player.children:
        log["Child_%s"%child.code] = 1

      for skillMod in player.playerSkillModifications:
        log["SkillMod_%s"%skillMod] = player.playerSkillModifications[skillMod]

      for hobby in player.hobbies:
        log["Hobby_%s"%hobby.code] = 1

      for job in player.jobs:
        log["Job_%s"%job.code] = 1

      for jobCode in player.jobPayModifications:
        log["JobPayMod_%s"%jobCode] = player.jobPayModifications[jobCode]

      for jobCode in player.jobSkillModifications:
        for skillCode in player.jobSkillModifications[jobCode]:
          log["JobSkillMod_%s_%s"%(jobCode,skillCode)] = player.jobSkillModifications[jobCode][skillCode]

      for jobCode in player.jobFiredCounts:
        log["JobFireCount_%s"%jobCode] = player.jobFiredCounts[jobCode]

      for jobCode in player.jobPassedCounts:
        log["JobPassCount_%s"%jobCode] = player.jobPassedCounts[jobCode]

      game.gameLog.append(log)

class GameManager(object):
  settings = []
  settingFilePath = 'GameManager.json'

  #Manages class settings loaded from GameManager.json
  @staticmethod
  def setting(pSettingName):
    if len(GameManager.settings) == 0:
      jsonFile = open( GameManager.settingFilePath )
      try: 
        GameManager.settings = json.loads(jsonFile.read())
      except ValueError, e:
        print "INVALID JSON SETTINGS FILE - EXITING"
        exit()
    if pSettingName in GameManager.settings:
      return GameManager.settings[pSettingName]
    else:
      return None

class RandomDecisionMaker:
  def makeDecision( self, game, options ):
    choice = random.randint(0,len(options)-1)
    return choice


game = Game()
game.addPlayer()

while game.isNextStep():
  game.performNextStep( game.decisionMaker.makeDecision( game, game.nextStepAvailableActions() ) )

csvOutFile = open( GameManager.setting('gameLogOutCsvPath'), 'wb' )
wr = csv.writer( csvOutFile, quoting=csv.QUOTE_ALL )
for row in game.gameLog:
  out_row = []
  for k in row:
    out_row.append( "%s: %s"%(k,row[k]) )
  wr.writerow(out_row)
csvOutFile.close()
