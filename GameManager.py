import re
import sqlite3
import csv
import json

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

class PartnerCard(object):
  def __init__(self, code ):

    job_row = DataManager.getRow( "SELECT * FROM Partner WHERE PartnerCode=?", [code] )

    self.code = code
    self.finances = job_row['Finances']
    self.moneyRequirement = job_row['MoneyRequirement']
    self.skillRequirements = DataManager.getRows( "SELECT * FROM PartnerSkillRequirement WHERE PartnerCode=?", [code] )
    self.needs = DataManager.getRows( "SELECT * FROM PartnerNeed WHERE PartnerCode=?", [code] )

class Player(object):
  def __init__(self, playerCardCode, money ):
    self.playerCard = PlayerCard(playerCardCode)
    self.money = money

class Game():
  players = []

class GameManager(object):
  myVar = None


game = Game()
player = Player('Player1', 3 )

print player.playerCard.code
