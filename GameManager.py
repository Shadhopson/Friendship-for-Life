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
    hobby_row = DataManager.getRow( "SELECT * FROM Hobby WHERE HobbyCode=?", [code] )

    self.code = code
    self.expense = hobby_row['Expense']
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

  def onAdd(self):
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
    self.bankruptcyCounter = 0
    self.trustTokens = trustTokens
    self.hasBankruptcy = False
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
      if needStat in needFulfillmentStats:
        if needFulfillmentStats[needStat] >= needVal:
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
    time = GameManager.setting("childTime")
    if GameManager.setting("isChildTimeFlat") == False:
      time = time * len(self.children)
    time += GameManager.setting("partnerTime") * len(self.partners)
    time += GameManager.setting("jobTime") * len(self.jobs)
    time += GameManager.setting("hobbyTime") * len(self.hobbies)
    return time

  def jobPayment(self,job):
    payment = job.pay
    if job.code in self.jobPayModifications:
      payment += self.jobPayModifications[job.code]
    return payment

  def childrenExpenses(self):
    return len(self.children) * GameManager.setting("childExpense")

  def hobbyExpenses(self,hobby):
    return hobby.expense

  def partnerFinances(self, partner):
    return partner.finances


class Game(object):

  def __init__(self):

    self.decisionMaker = RandomDecisionMaker()

    self.playerCardDeck = []
    self.hobbyCardDeck = []
    self.partnerCardDeck = []
    self.childCardDeck = []
    self.jobCardDeck = []

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

      if GameManager.setting("isChildTimeFlat") and len(self.currentPlayer().children):
        ret.append( { 'action': 'childAttempt' } )
      elif self.currentPlayer().currentTime() + GameManager.setting("childTime") <= GameManager.setting("maxTime"):
        ret.append( { 'action': 'childAttempt' } )

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

    self.logPlayers()
    current_money = self.currentPlayer().money
    #create log
    log = { "Round": self.currentRound, "Player": self.currentPlayer().playerCard.code, 'CurrentStep': self.currentStep }
    log['Type'] = 'Action'
    if action != None:
      action_ops = self.nextStepAvailableActions()
      action = action_ops[action]
      log["Decision"] = action
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
        actions.append( {'action':'addJob','jobCard':nextJobCard.code} )
        revealedCards.append(nextJobCard)
      decision = self.decisionMaker.makeDecision( self, actions )
      actionResponse = actions[decision]
      log["Decision2"] = actionResponse
      for i in revealedCards:
        if actionResponse['action'] == 'addJob' and i.code == actionResponse['jobCard']:
          self.currentPlayer().jobs.append( i )
          i.onAdd()
        else:
          self.jobCardDeck.insert( 0,i )

    elif action['action'] == 'hobbySearch':
      actions = [{'action':'pass'}]
      revealedCards = []
      for i in range(GameManager.setting("hobbySearchNumCards")):
        nextHobbyCard = self.hobbyCardDeck.pop()
        actions.append( {'action':'addHobby','hobbyCard':nextHobbyCard.code} )
        revealedCards.append(nextHobbyCard)
      decision = self.decisionMaker.makeDecision( self, actions )
      actionResponse = actions[decision]
      log["Decision2"] = actionResponse
      for i in revealedCards:
        if actionResponse['action'] == 'addHobby' and i.code == actionResponse['hobbyCard']:
          self.currentPlayer().hobbies.append( i )
        else:
          self.hobbyCardDeck.insert( 0,i )

    elif action['action'] == 'partnerSearch':
      actions = [{'action':'pass'}]
      revealedCards = []
      for i in range(GameManager.setting("partnerSearchNumCards")):
        nextPartnerCard = self.partnerCardDeck.pop()
        revealedCards.append( nextPartnerCard )
        actions.append( {'action':'addPartner','partnerCard':nextPartnerCard.code} )
      decision = self.decisionMaker.makeDecision( self, actions )
      actionResponse = actions[decision]
      log["Decision2"] = actionResponse
      for i in revealedCards:
        if actionResponse['action'] == 'addPartner' and actionResponse['partnerCard'] == i.code:
          self.currentPlayer().partners.append( i )
        else:
          self.partnerCardDeck.insert( 0,i )

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


    if self.currentStep == 'night':

      # get paid
      for job in self.currentPlayer().jobs:
        self.currentPlayer().money += self.currentPlayer().jobPayment(job)

      # pay for children
      self.currentPlayer().money -= self.currentPlayer().childrenExpenses()

      # pay for life
      self.currentPlayer().money -= GameManager.setting("baseLifeExpense")

      # pay for hobbies 
      for hobby in self.currentPlayer().hobbies:
        self.currentPlayer().money += self.currentPlayer().hobbyExpenses(hobby)

      # partner finances
      for partner in self.currentPlayer().partners:
        self.currentPlayer().money += self.currentPlayer().partnerFinances(partner)

      if self.currentPlayer().money < 0:
        self.currentPlayer().money = current_money 
        self.currentPlayer().hasBankruptcy = True
        self.currentPlayer().bankruptcyCounter += 1
    self.gameLog.append(log)

    #move to next step
    if self.currentStep == 'morning':
      self.currentStep = 'evening'
    elif self.currentStep == 'evening':
      self.currentStep = 'night'
    elif self.currentStep == 'night':
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

      self.gameLog.append(log)

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

