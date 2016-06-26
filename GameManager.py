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
    self.hobbies = []
    self.jobs = []
    self.jobPayModifications = {}
    self.jobSkillModifications = {}

    for skill in self.playerCard.skills:
      self.playerSkillModifications.update( {skill['SkillCode']:0} )

  def modifyNeed( self, needCode, value ):
    if needCode not in self.playerNeedModifications:
      self.playerNeedModifications[needCode] = 0
    self.playerNeedModifications[needCode] += value

  def modifySkill( self, skillCode, value ):
    if skillCode not in self.playerSkillModifications:
      self.playerSkillModifications[skillCode] = 0
    self.playerSkillModifications[skillCode] += value


  # gets players current stats (after modifications)
  def needStats(self):
    stats = {}
    for need in self.playerCard.needs:
      val = need['Value']
      code = need['NeedCode']
      if code in self.playerNeedModifications:
        val += self.playerNeedModifications[code]
      stats.update({ code: val } )
    return stats

  # gets players current stats (after modifications)
  def skillStats(self):
    stats = {}
    for skill in self.playerCard.skills:
      val = skill['Value']
      code = skill['SkillCode']
      val += self.playerSkillModifications[code]
      stats.update({ code: val } )
    return stats

  # gets jobs required stats (after modifications)
  def jobSkillRequirements(self,job):
    reqs = {}
    for req in job.skillRequirements:
      val = req['Value']
      if job.code in self.jobSkillModifications and req['SkillCode'] in self.jobSkillModifications[job.code]:
        val += self.jobSkillModifications[job.code][req['SkillCode']]
      reqs.update({ req['SkillCode']: val } )
    return reqs

  def partnerSkillRequirements(self,partner):
    reqs = {}
    for req in partner.skillRequirements:
      val = req['Value']
      if partner.code in self.partnerSkillModifications and req['SkillCode'] in self.partnerSkillModifications[partner.code]:
        val += self.partnerSkillModifications[partner.code][req['SkillCode']]
      reqs.update({ req['SkillCode']: val } )
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

    #perform action
    elif action['action'] == 'hangOut':
      self.currentPlayer().trustTokens += 1
    if action['action'] == 'jobSearch':
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
          log.update( { "addedJob":i.code } )
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
          log.update( { "addedHobby":i.code } )
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
          log.update( { "addedPartner":i.code } )
        else:
          self.partnerCardDeck.insert( 0,i )

    elif action['action'] == 'quitJob':
      for job in self.currentPlayer().jobs:
        if job.code == action['jobCard']:
          self.currentPlayer().jobs.remove(job)
          self.jobCardDeck.insert(0,job)

    elif action['action'] == 'quitHobby':
      for hobby in self.currentPlayer().hobbies:
        if hobby.code == action['hobbyCard']:
          self.currentPlayer().hobbies.remove(hobby)
          self.hobbyCardDeck.insert(0,hobby)

    elif action['action'] == 'quitPartner':
      for partner in self.currentPlayer().partners:
        if partner.code == action['partnerCard']:
          self.currentPlayer().partners.remove(partner)
          self.partnerCardDeck.insert(0,partner)


    # EVENT ROLL (if evening)
    if self.currentStep == 'evening':
      eventRoll = random.randint( 0, 20 )
      if eventRoll in GameManager.setting('eventRollPromotion'):
        log.update( { "eventRoll":"Promotion" } )
        if len(self.currentPlayer().jobs):
          jobIndex = random.randint( 0,len(self.currentPlayer().jobs)-1 )
          job = self.currentPlayer().jobs[jobIndex]
          stat = random.choice( self.currentPlayer().skillStats().keys() )
          self.currentPlayer().modifySkill( stat, 1 )
          if job.code not in self.currentPlayer().jobPayModifications:
            self.currentPlayer().jobPayModifications.update( {job.code: 0} )
          self.currentPlayer().jobPayModifications[job.code] += 1
          log.update( { "playerSkillIncreased": stat } )
          log.update( { "jobPayIncrease": job.code } )

      elif eventRoll in GameManager.setting('eventRollJobSkillIncrease'):
        log.update( { "eventRoll":"JobSkillIncrease" } )
        if len(self.currentPlayer().jobs):
          jobIndex = random.randint( 0,len(self.currentPlayer().jobs)-1 )
          job = self.currentPlayer().jobs[jobIndex]
          jobStats = self.currentPlayer().jobSkillRequirements(job)
          stat = random.choice( jobStats.keys() )
          if job.code not in self.currentPlayer().jobSkillModifications:
            self.currentPlayer().jobSkillModifications.update({job.code:{}})
          if stat not in self.currentPlayer().jobSkillModifications[job.code]:
            self.currentPlayer().jobSkillModifications[job.code].update({stat:0})
          self.currentPlayer().jobSkillModifications[job.code][stat] += 1
          log.update( { "jobSkillIncreased": "%s - %s"%(job.code,stat) } )

      elif eventRoll in GameManager.setting('eventRollPartnerSkillIncrease'):
        log.update( { "eventRoll":"PartnerSkillIncrease" } )
        if len(self.currentPlayer().partners):
          partnerIndex = random.randint( 0,len(self.currentPlayer().partners)-1 )
          partner = self.currentPlayer().partners[partnerIndex]
          partnerStats = self.currentPlayer().partnerSkillRequirements(partner)
          stat = random.choice( partnerStats.keys() )
          if partner.code not in self.currentPlayer().partnerSkillModifications:
            self.currentPlayer().partnerSkillModifications.update({partner.code:{}})
          if stat not in self.currentPlayer().partnerSkillModifications[partner.code]:
            self.currentPlayer().partnerSkillModifications[partner.code].update({stat:0})
          self.currentPlayer().partnerSkillModifications[partner.code][stat] += 1
          log.update( { "partnerSkillIncreased": "%s - %s"%(partner.code,stat) } )

      elif eventRoll in GameManager.setting('eventRollJobCheckIn'):
        log.update( { "eventRoll":"JobCheckIn" } )
        if len(self.currentPlayer().jobs):
          jobIndex = random.randint( 0,len(self.currentPlayer().jobs)-1 )
          job = self.currentPlayer().jobs[jobIndex]
          isPass = self.currentPlayer().isJobCheckPass(job)
          log.update( { "jobCheckRes":"%s - %s"%(job.code,isPass) } )
          if isPass == 'pass':
            None
          elif isPass == 'exceed':
            if job.code not in self.currentPlayer().jobPayModifications:
              self.currentPlayer().jobPayModifications.update( {job.code: 0} )
            self.currentPlayer().jobPayModifications[job.code] += 1
            log.update( { "jobPayIncrease": job.code } )
          else:
            if job.code in self.currentPlayer().jobPayModifications:
              self.currentPlayer().jobPayModifications[job.code] = 0
            if job.code in self.currentPlayer().jobSkillModifications:
              self.currentPlayer().jobSkillModifications[job.code] = {}
            self.currentPlayer().jobs.remove(job)
            self.jobCardDeck.insert(0,job)
            log.update( { "firedFromJob": job.code } )

      elif eventRoll in GameManager.setting('eventRollRelationshipCheckIn'):
        log.update( { "eventRoll":"RelationshipCheckIn" } )
        if len(self.currentPlayer().partners):
          partnerIndex = random.randint( 0,len(self.currentPlayer().partners)-1 )
          partner = self.currentPlayer().partners[partnerIndex]
          isPass = self.currentPlayer().isPartnerCheckPass(partner)
          log.update( { "partnerCheckRes":"%s - %s"%(partner.code,isPass) } )
          if isPass == 'pass':
            None
          elif isPass == 'exceed':
            None
          else:
            if partner.code in self.currentPlayer().partnerSkillModifications:
              self.currentPlayer().partnerSkillModifications[partner.code] = {}
            self.currentPlayer().partners.remove(partner)
            self.partnerCardDeck.insert(0,partner)
            log.update( { "firedFromPartner": partner.code } )


      elif eventRoll in GameManager.setting('eventRollFriendFight'):
        log.update( { "eventRoll":"FriendFight" } )
        if self.currentPlayer().trustTokens > 0:
          self.currentPlayer().trustTokens -= 1

      elif eventRoll in GameManager.setting('eventRollRelativeDeath'):
        log.update( { "eventRoll":"RelativeDeath" } )

      elif eventRoll in GameManager.setting('eventRollReferral'):
        log.update( { "eventRoll":"Referral" } )
      elif eventRoll in GameManager.setting('eventRollLoan'):
        log.update( { "eventRoll":"RollLoan" } )
      elif eventRoll in GameManager.setting('eventRollUnexpectedChild'):
        log.update( { "eventRoll":"UnexpectedChild" } )
      elif eventRoll in GameManager.setting('eventRollAdopt'):
        log.update( { "eventRoll":"Adopt" } )
      elif eventRoll in GameManager.setting('eventRollStatMinus'):
        log.update( { "eventRoll":"StatMinus" } )
      elif eventRoll in GameManager.setting('eventRollStatPlus'):
        log.update( { "eventRoll":"StatPlus" } )
      else:
        log.update( { "eventRoll":"Nothing" } )


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

      self.currentStep = 'morning'

    self.gameLog.append(log)

  def logPlayers( self ):
    for player in self.players:
      log = {'playerCode': player.playerCard.code }
      skillsArr = []
      for skill in player.skillStats():
        skillsArr.append( "%s:%s"%(skill,player.skillStats()[skill]) )
      log.update({ "Player Skills": (", ".join(skillsArr) )})

      needsArr = []
      for need in player.needStats():
        needsArr.append( "%s:%s"%(need,player.needStats()[need]) )
      log.update({ "Player Needs": (", ".join(needsArr) )})

      jobsArr = []
      for job in player.jobs:
        jobsArr.append( '%s:%s'%(job.code,player.isJobCheckPass(job)) )
      log.update( {"Player Jobs":", ".join(jobsArr)} )

      log.update( {"Player Money":player.money} )

      log.update( {"Player Trust Tokens ":player.trustTokens} )

      partnersArr = []
      for partner in player.partners:
        partnersArr.append( '%s:%s'%(partner.code,player.isPartnerCheckPass(partner)) )
      log.update( {"Player Partners":", ".join(partnersArr)} )

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
