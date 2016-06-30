import re
import sqlite3
import csv
import json
import os.path
from shutil import copyfile

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def get_rows(q):
  rows = []
  for row in q:
    rows.append(row)
  return rows

def get_row(q):
  for row in q:
    return row

class DataManager(object):

  conn = {}
  settings = []
  settingFilePath = 'DataManager.json'

  #connection to DB
  @staticmethod
  def connection(conn=None):
    if conn == None:
      conn = 'defaultConn'
    if conn not in DataManager.conn or DataManager.conn[conn] == None:
      dbPathVar = DataManager.setting(conn)
      DataManager.conn[conn] = sqlite3.connect( DataManager.setting(dbPathVar) )
      DataManager.conn[conn].row_factory = dict_factory 
    return DataManager.conn[conn]

  #get rows from DB
  @staticmethod
  def getRows(q,ops=None,conn=None):
    return get_rows( DataManager.execute(q,ops,conn) )

  #get rows from DB
  @staticmethod
  def getRow(q,ops=None,conn=None):
    return get_row( DataManager.execute(q,ops,conn) )

  #get rows from DB
  @staticmethod
  def execute(q,ops=None,conn=None):
    conn = DataManager.connection(conn)
    if ops != None:
      return conn.cursor().execute(q,ops)
    else:
      return conn.cursor().execute(q)

  #close connection to DB
  @staticmethod
  def closeConnection(conn=None):
    if conn == None:
      conn = 'defaultConn'
    if conn in DataManager.conn:
      DataManager.conn[conn].commit()
      DataManager.conn[conn].close()
      DataManager.conn[conn] = None

  #Manages class settings loaded from DataManager.json
  @staticmethod
  def setting(pSettingName):
    if len(DataManager.settings) == 0:
      jsonFile = open( DataManager.settingFilePath )
      try: 
        DataManager.settings = json.loads(jsonFile.read())
      except ValueError, e:
        print "INVALID JSON SETTINGS FILE - EXITING"
        exit()
    if pSettingName in DataManager.settings:
      return DataManager.settings[pSettingName]
    else:
      return None

  #Converts a name to a code (ex: 'Help the World' => 'HelpTheWorld' )
  @staticmethod
  def nameToCode(pCode):
    code = pCode.title().replace( " ", "" )
    aliases = DataManager.setting("codeAliases")
    if code in aliases:
      code = aliases[code]
    return code

  #Parses a name-value cell (these are the cells in the CSV like "Empathy + 2") into its component parts ('name', 'code' and 'value' ) 
  @staticmethod
  def parseNameValueCell(pNameValue):
    parts = re.findall(r'([\w\s]+\w)[\s:]\s*([+-]?\s*\$?\s*\d+)', pNameValue)
    if len(parts) == 0 or len(parts[0]) == 0:
      errorStr = "INVALID value passed into parseNameValueCell: %s (res=%s)" % (pNameValue, parts)
      raise ValueError( errorStr )
    name = parts[0][0]
    name =  name.strip()
    code = DataManager.nameToCode( name )
    value = parts[0][1].replace(" ", "")
    value = value.replace("$", "")
    return { 'code': code, 'name': name, 'value': value }


  #Imports the data from CSV files into the SQLite DB
  @staticmethod
  def csvToDb():

    tables = [\
      "Need", \
      "Skill", \
      "Hobby", \
      "HobbySkill", \
      "HobbyNeed", \
      "Player", \
      "PlayerSkill", \
      "PlayerNeed", \
      "Child", \
      "ChildSkill", \
      "ChildNeed", \
      "Partner", \
      "PartnerSkillRequirement", \
      "PartnerNeed", \
      "Job", \
      "JobSkillRequirement", \
      "JobNeed", \
    ]
    for table in tables:
      DataManager.execute( "DELETE FROM %s"%table, None )
      DataManager.execute( "DELETE FROM sqlite_sequence where name = ?", [table] )

    DataManager.execute( "VACUUM", None )

    skillsInDb = []
    needsInDb = []

    #
    #########################     IMPORT FROM HOBBY FILE     ######################### 
    nameColumn =  0
    expenseColumn =  0
    skillColumns = []
    needColumns = []
    f = open( DataManager.setting('hobbyCardCsvPath') )
    hobbyFileCSV = csv.reader(f)
    for ri,row in enumerate(hobbyFileCSV):

      # header row: determine what each column is
      if ri == 0:
        for ci,cell in enumerate(row):
          cell = cell.strip()
          if re.findall( r'Hobby', cell ):
            nameColumn = ci
          elif re.findall( r'Skill', cell ):
            skillColumns.append(ci)
          elif re.findall( r'Need', cell ):
            needColumns.append(ci)
          elif re.findall( r'Expense', cell ):
            expenseColumn = ci

      # data row
      else:
        hobbyCode = ""
        for ci,cell in enumerate(row):
          cell = cell.strip()

          #Hobby name column
          if ci == nameColumn:
            hobbyCode = DataManager.nameToCode( cell )
            DataManager.execute( "INSERT INTO Hobby ( HobbyCode, Name, Expense ) VALUES ( ?, ?, ? )", [hobbyCode, cell, 0]  )

          #Skill columns
          elif ci in skillColumns and len(cell.replace(" ","")) > 0:
            cellParts = DataManager.parseNameValueCell( cell )
            if cellParts['code'] not in skillsInDb:
              skillsInDb.append(cellParts['code'])
              DataManager.execute("INSERT INTO Skill (SkillCode, Name) VALUES ( ?, ?)", [cellParts['code'], cellParts['name']])
            DataManager.execute("INSERT INTO HobbySkill (HobbyCode, SkillCode, Value) VALUES ( ?, ?, ?)", [hobbyCode, cellParts['code'], cellParts['value'] ])

          #Needs columns
          elif ci in needColumns and len(cell.replace(" ","")) > 0:
            cellParts = DataManager.parseNameValueCell( cell )
            if cellParts['code'] not in needsInDb:
              needsInDb.append(cellParts['code'])
              DataManager.execute("INSERT INTO Need (NeedCode, Name) VALUES ( ?, ?)", [cellParts['code'], cellParts['name']])
            DataManager.execute("INSERT INTO HobbyNeed (HobbyCode, NeedCode, Value) VALUES ( ?, ?, ?)", [hobbyCode, cellParts['code'], cellParts['value'] ])

          # Expense Column
          elif ci == expenseColumn and len(cell):
            DataManager.execute( "UPDATE Hobby SET Expense=? WHERE HobbyCode=?", [cell,hobbyCode] )

    #
    #########################     IMPORT FROM PLAYER FILE     ######################### 
    nameColumn =  0
    skillColumns = []
    skillColumnMap = {}
    needColumns = []
    f = open( DataManager.setting('playerCardCsvPath') )
    playerFileCSV = csv.reader(f)
    for ri,row in enumerate(playerFileCSV):

      # header row: determine what each column is
      if ri == 0:
        for ci,cell in enumerate(row):
          cell = cell.strip()
          if re.findall( r'Name', cell ):
            nameColumn = ci
          elif re.findall( r'Skill', cell ):
            skillColumns.append(ci)
            parts = re.findall(r'([\w\s]+\w)\s+Skill', cell)
            skillName = parts[0]
            skillCode = DataManager.nameToCode(skillName)
            skillColumnMap.update( {ci:skillName} )
            if skillCode not in skillsInDb:
              skillsInDb.append(skillCode)
              DataManager.execute("INSERT INTO Skill (SkillCode, Name) VALUES ( ?, ?)", [skillCode, skillName])
          elif re.findall( r'Need', cell ):
            needColumns.append(ci)

      # data row
      else:
        playerCode = ""
        for ci,cell in enumerate(row):
          cell = cell.strip()

          #Player name column
          if ci == nameColumn:
            playerCode = DataManager.nameToCode( cell )
            DataManager.execute( "INSERT INTO Player ( PlayerCode, Name ) VALUES ( ?, ? )", [playerCode, cell]  )

          #Skill columns
          if ci in skillColumns and len(cell) > 0:
            DataManager.execute("INSERT INTO PlayerSkill (PlayerCode, SkillCode, Value) VALUES ( ?, ?, ?)", [playerCode, skillColumnMap[ci], cell ])

          #Needs columns
          if ci in needColumns and len(cell) > 0:
            cellParts = DataManager.parseNameValueCell( cell )
            if cellParts['code'] not in needsInDb:
              needsInDb.append(cellParts['code'])
              DataManager.execute("INSERT INTO Need (NeedCode, Name) VALUES ( ?, ?)", [cellParts['code'], cellParts['name']])
            DataManager.execute("INSERT INTO PlayerNeed (PlayerCode, NeedCode, Value) VALUES ( ?, ?, ?)", [playerCode, cellParts['code'], cellParts['value'] ])



    #
    #########################     IMPORT FROM CHILD FILE     ######################### 
    nameColumn = -1
    costColumn = -1 
    skillColumns = []
    needColumns = []
    f = open( DataManager.setting('childCardCsvPath') )
    childFileCSV = csv.reader(f)
    for ri,row in enumerate(childFileCSV):

      # header row: determine what each column is
      if ri == 0:
        for ci,cell in enumerate(row):
          cell = cell.strip()
          if re.findall( r'Name', cell ):
            nameColumn = ci
          elif re.findall( r'Skill', cell ):
            skillColumns.append(ci)
          elif re.findall( r'Need', cell ):
            needColumns.append(ci)
          elif re.findall( r'Cost', cell ):
            costColumn = ci

        if nameColumn < 0:
          raise ValueError( "Could not find name column in childCsvFile" )
        if costColumn < 0:
          raise ValueError( "Could not find cost column in childCsvFile" )
        if len(skillColumns) == 0:
          raise ValueError( "Could not find skill column in childCsvFile" )
        if len(needColumns) == 0:
          raise ValueError( "Could not find need column in childCsvFile" )

      # data row
      else:
        childCode = ""
        for ci,cell in enumerate(row):
          cell = cell.strip()

          #Name column
          if ci == nameColumn:
            childCode = DataManager.nameToCode( cell )
            DataManager.execute( "INSERT INTO Child ( ChildCode, Name, Cost ) VALUES ( ?, ?, 0 )", [childCode, cell]  )

          #Skill columns
          if ci in skillColumns and len(cell) > 0:
            cellParts = DataManager.parseNameValueCell( cell )
            if cellParts['code'] not in skillsInDb:
              skillsInDb.append(cellParts['code'])
              DataManager.execute("INSERT INTO Skill (SkillCode, Name) VALUES ( ?, ?)", [cellParts['code'], cellParts['name']])
            DataManager.execute("INSERT INTO ChildSkill (ChildCode, SkillCode, Value) VALUES ( ?, ?, ?)", [childCode, cellParts['code'], cellParts['value'] ])

          #Needs columns
          if ci in needColumns and len(cell) > 0:
            cellParts = DataManager.parseNameValueCell( cell )
            if cellParts['code'] not in needsInDb:
              needsInDb.append(cellParts['code'])
              DataManager.execute("INSERT INTO Need (NeedCode, Name) VALUES ( ?, ?)", [cellParts['code'], cellParts['name']])
            DataManager.execute("INSERT INTO ChildNeed (ChildCode, NeedCode, Value) VALUES ( ?, ?, ?)", [childCode, cellParts['code'], cellParts['value'] ])

          #Cost column
          if ci == costColumn:
            cell = cell.replace( " ", "" )
            cell = cell.replace( "$", "" )
            DataManager.execute( "UPDATE Child SET Cost=? WHERE ChildCode=?", [cell, childCode]  )




    #########################     IMPORT FROM PARTNER FILE     ######################### 
    nameColumn = -1
    financesColumn = -1 
    skillRequirementColumns = []
    needColumns = []
    f = open( DataManager.setting('partnerCardCsvPath') )
    partnerFileCSV = csv.reader(f)
    partnerMaxRow = DataManager.setting('partnerCardCsvMaxRow');
    for ri,row in enumerate(partnerFileCSV):

      # header row: determine what each column is
      if ri == 0:
        for ci,cell in enumerate(row):
          cell = cell.strip()
          if re.findall( r'Name', cell ):
            nameColumn = ci
          elif re.findall( r'Support', cell ):
            needColumns.append(ci)
          elif re.findall( r'Need', cell ):
            skillRequirementColumns.append(ci)
          elif re.findall( r'Finances', cell ):
            financesColumn = ci

        if nameColumn < 0:
          raise ValueError( "Could not find name column in partnerCsvFile" )
        if financesColumn < 0:
          raise ValueError( "Could not find finances column in partnerCsvFile" )
        if len(skillRequirementColumns) == 0:
          raise ValueError( "Could not find skill requirement column in partnerCsvFile" )
        if len(needColumns) == 0:
          raise ValueError( "Could not find need column in partnerCsvFile" )

      # data row
      elif partnerMaxRow == None or ri < partnerMaxRow:
        partnerCode = ""
        for ci,cell in enumerate(row):
          cell = cell.strip()

          #Name column
          if ci == nameColumn:
            partnerCode = DataManager.nameToCode( cell )
            DataManager.execute( "INSERT INTO Partner ( PartnerCode, Name, Finances, MoneyRequirement ) VALUES ( ?, ?, 0, 0 )", [partnerCode, cell]  )

          #Skill columns
          if ci in skillRequirementColumns and len(cell) > 0:
            cellParts = DataManager.parseNameValueCell( cell )
            if cellParts['code'] == 'Savings':
              DataManager.execute( "UPDATE Partner SET MoneyRequirement=? WHERE PartnerCode=?", [cellParts['value'], partnerCode]  )
            else:
              if cellParts['code'] not in skillsInDb:
                skillsInDb.append(cellParts['code'])
                DataManager.execute("INSERT INTO Skill (SkillCode, Name) VALUES ( ?, ?)", [cellParts['code'], cellParts['name']])
              DataManager.execute("INSERT INTO PartnerSkillRequirement (PartnerCode, SkillCode, Value) VALUES ( ?, ?, ?)", [partnerCode, cellParts['code'], cellParts['value'] ])

          #Needs columns
          if ci in needColumns and len(cell) > 0:
            cellParts = DataManager.parseNameValueCell( cell )
            if cellParts['code'] not in needsInDb:
              needsInDb.append(cellParts['code'])
              DataManager.execute("INSERT INTO Need (NeedCode, Name) VALUES ( ?, ?)", [cellParts['code'], cellParts['name']])
            DataManager.execute("INSERT INTO PartnerNeed (PartnerCode, NeedCode, Value) VALUES ( ?, ?, ?)", [partnerCode, cellParts['code'], cellParts['value'] ])

          #Finances column
          if ci == financesColumn:
            cell = cell.replace( " ", "" )
            cell = cell.replace( "$", "" )
            DataManager.execute( "UPDATE Partner SET Finances=? WHERE PartnerCode=?", [cell, partnerCode]  )




    #########################     IMPORT FROM JOB FILE     ######################### 
    nameColumn = -1
    payColumn = -1 
    skillRequirementColumns = []
    needColumns = []
    f = open( DataManager.setting('jobCardCsvPath') )
    jobFileCSV = csv.reader(f)
    jobMaxRow = DataManager.setting('jobCardCsvMaxRow');
    for ri,row in enumerate(jobFileCSV):

      # header row: determine what each column is
      if ri == 0:
        for ci,cell in enumerate(row):
          cell = cell.strip()
          if re.findall( r'Position', cell ):
            nameColumn = ci
          elif re.findall( r'Skill', cell ):
            skillRequirementColumns.append(ci)
          elif re.findall( r'Benefit', cell ):
            needColumns.append(ci)
          elif re.findall( r'Pay', cell ):
            payColumn = ci

        if nameColumn < 0:
          raise ValueError( "Could not find name column in jobCsvFile" )
        if payColumn < 0:
          raise ValueError( "Could not find pay column in jobCsvFile" )
        if len(skillRequirementColumns) == 0:
          raise ValueError( "Could not find skill requirement column in jobCsvFile" )
        if len(needColumns) == 0:
          raise ValueError( "Could not find need column in jobCsvFile" )

      # data row
      elif jobMaxRow == None or ri < jobMaxRow:
        jobCode = ""
        for ci,cell in enumerate(row):
          cell = cell.strip()

          #Name column
          if ci == nameColumn:
            jobCode = DataManager.nameToCode( cell )
            DataManager.execute( "INSERT INTO Job ( JobCode, Name, Pay ) VALUES ( ?, ?, 0 )", [jobCode, cell]  )

          #Skill columns
          if ci in skillRequirementColumns and len(cell) > 0:
            cellParts = DataManager.parseNameValueCell( cell )
            if cellParts['code'] not in skillsInDb:
              skillsInDb.append(cellParts['code'])
              DataManager.execute("INSERT INTO Skill (SkillCode, Name) VALUES ( ?, ?)", [cellParts['code'], cellParts['name']])
            DataManager.execute("INSERT INTO JobSkillRequirement (JobCode, SkillCode, Value) VALUES ( ?, ?, ?)", [jobCode, cellParts['code'], cellParts['value'] ])

          #Needs columns
          if ci in needColumns and len(cell) > 0:
            cellParts = DataManager.parseNameValueCell( cell )
            if cellParts['code'] not in needsInDb:
              needsInDb.append(cellParts['code'])
              DataManager.execute("INSERT INTO Need (NeedCode, Name) VALUES ( ?, ?)", [cellParts['code'], cellParts['name']])
            DataManager.execute("INSERT INTO JobNeed (JobCode, NeedCode, Value) VALUES ( ?, ?, ?)", [jobCode, cellParts['code'], cellParts['value'] ])

          #Pay column
          if ci == payColumn:
            cell = cell.replace( " ", "" )
            cell = cell.replace( "$", "" )
            if len( re.findall( r'[^-0-9]', cell ) ) == 0:
              DataManager.execute( "UPDATE Job SET Pay=? WHERE JobCode=?", [cell, jobCode]  )

    DataManager.closeConnection()

  @staticmethod
  def createGameDb():
    if os.path.isfile( DataManager.setting("gameResultsDbPath") ) == False:
      copyfile( DataManager.setting("dbPath"), DataManager.setting("gameResultsDbPath") )

  @staticmethod
  def clearGameLogDb():
    DataManager.createGameDb()
    gameTables = [ \
      "Game" ,\
      "GameState" ,\
      "GameStateNeedMod" ,\
      "GameStatePartnerSkillMod" ,\
      "GameStatePartnerPassedCount" ,\
      "GameStatePartnerFiredCount" ,\
      "GameStateChild" ,\
      "GameStateSkillMod" ,\
      "GameStateHobby" ,\
      "GameStateJob" ,\
      "GameStateJobPayMod" ,\
      "GameStateJobSkillMod" ,\
      "GameStateJobFiredCount" ,\
      "GameStateJobPassedCount" ,\
      "GameStateAction" ,\
      "GameStatePartner" ,\
    ]
    for table in gameTables:
      DataManager.execute( "DELETE FROM %s"%table, None, "gameConn" )
      DataManager.execute( "DELETE FROM sqlite_sequence where name = ?", [table], "gameConn" )

    DataManager.execute( "VACUUM", None, "gameConn" )

    DataManager.closeConnection("gameConn")


  @staticmethod
  def insertGameLogIntoDb(gameLog):
    DataManager.createGameDb()
    res = DataManager.execute( "INSERT INTO Game DEFAULT VALUES", None, "gameConn" )
    gameId = res.lastrowid

    gameStateId = None
    lastRow = gameLog.pop()
    for row in gameLog:
      if row['Type'] == 'GameState':
        inputs = [ gameId, row['Points'], row['PlayerCode'], row['Time'], \
            row['Round'], row['Step'], row['Money'], row['TrustTokens'], row['EndPoints'] ]
        res = DataManager.execute( """
          INSERT INTO GameState 
            ( GameId, Points, PlayerCode, Time, Round, Step, Money, TrustTokens, RoundEndPoints )
          VALUES
            ( ?, ?, ?, ?, ?, ?, ?, ?, ? )
          """, inputs, "gameConn" )

        gameStateId = res.lastrowid

        for i,partner in enumerate(sorted(row['Partners'])):
          inputs  = [gameStateId, partner, i+1]
          res = DataManager.execute( """
            INSERT INTO GameStatePartner
              ( GameStateId, PartnerCode, Position )
            VALUES
              ( ?, ?, ? )
            """, inputs, "gameConn" )

        for i,partner in enumerate(sorted(row['PartnerPassedCounts'])):
          val = row['PartnerPassedCounts'][partner]
          if val > 0:
            inputs  = [ gameStateId, partner, val, i+1 ]
            res = DataManager.execute( """
              INSERT INTO GameStatePartnerPassedCount
                ( GameStateId, PartnerCode, Value, Position )
              VALUES
                ( ?, ?, ?, ? )
              """, inputs, "gameConn" )

        for i,partner in enumerate(sorted(row['PartnerFiredCounts'])):
          val = row['PartnerFiredCounts'][partner]
          if val > 0:
            inputs  = [gameStateId, partner, val, i+1]
            res = DataManager.execute( """
              INSERT INTO GameStatePartnerFiredCount
                ( GameStateId, PartnerCode, Value, Position )
              VALUES
                ( ?, ?, ?, ? )
              """, inputs, "gameConn" )

        for partner in row['PartnerSkillMods']:
          for skill in row['PartnerSkillMods'][partner]:
            val = row['PartnerSkillMods'][partner][skill]
            if val > 0:
              inputs  = [ gameStateId, partner, skill, val, 0 ]
              res = DataManager.execute( """
                INSERT INTO GameStatePartnerSkillMod
                  ( GameStateId, PartnerCode, SkillCode, Value, Position )
                VALUES
                  ( ?, ?, ?, ?, ? )
                """, inputs, "gameConn" )

        for i,job in enumerate(sorted(row['Jobs'])):
          inputs  = [gameStateId, job['JobCode'], job['Pay'], i+1 ]
          res = DataManager.execute( """
            INSERT INTO GameStateJob
              ( GameStateId, JobCode, Pay, Position )
            VALUES
              ( ?, ?, ?, ? )
            """, inputs, "gameConn" )

        for i,job in enumerate(sorted(row['JobPassedCounts'])):
          val = row['JobPassedCounts'][job]
          if val > 0:
            inputs  = [gameStateId, job, val, i+1]
            res = DataManager.execute( """
              INSERT INTO GameStateJobPassedCount
                ( GameStateId, JobCode, Value, Position )
              VALUES
                ( ?, ?, ?, ? )
              """, inputs, "gameConn" )

        for i,job in enumerate(sorted(row['JobFiredCounts'])):
          val = row['JobFiredCounts'][job]
          if val > 0:
            inputs  = [gameStateId, job, val, i+1]
            res = DataManager.execute( """
              INSERT INTO GameStateJobFiredCount
                ( GameStateId, JobCode, Value, Position )
              VALUES
                ( ?, ?, ?, ? )
              """, inputs, "gameConn" )

        for job in row['JobPayMods']:
          val = row['JobPayMods'][job]
          if val > 0:
            inputs  = [gameStateId, job, val, 0]
            res = DataManager.execute( """
              INSERT INTO GameStateJobPayMod
                ( GameStateId, JobCode, Value, Position )
              VALUES
                ( ?, ?, ?, ? )
              """, inputs, "gameConn" )

        for job in row['JobSkillMods']:
          for skill in row['JobSkillMods'][job]:
            val = row['JobSkillMods'][job][skill]
            if val > 0:
              inputs  = [ gameStateId, job, skill, val, 0 ]
              res = DataManager.execute( """
                INSERT INTO GameStateJobSkillMod
                  ( GameStateId, JobCode, SkillCode, Value, Position )
                VALUES
                  ( ?, ?, ?, ?, ? )
                """, inputs, "gameConn" )

        for skill in row['SkillMods']:
          val = row['SkillMods'][skill]
          if val > 0: 
            inputs  = [gameStateId, skill, val, 0]
            res = DataManager.execute( """
              INSERT INTO GameStateSkillMod
                ( GameStateId, SkillCode, Value, Position )
              VALUES
                ( ?, ?, ?, ? )
              """, inputs, "gameConn" )

        for need in row['NeedMods']:
          val = row['NeedMods'][need]
          if val > 0:
            inputs  = [gameStateId, need, val, 0]
            res = DataManager.execute( """
              INSERT INTO GameStateNeedMod
                ( GameStateId, NeedCode, Value, Position )
              VALUES
                ( ?, ?, ?, ? )
              """, inputs, "gameConn" )

        for i,hobby in enumerate(sorted(row['Hobbies'])):
          inputs  = [gameStateId, hobby, i+1 ]
          res = DataManager.execute( """
            INSERT INTO GameStateHobby
              ( GameStateId, HobbyCode, Position )
            VALUES
              ( ?, ?, ? )
            """, inputs, "gameConn" )

        for i,child in enumerate(sorted(row['Children'])):
          inputs  = [ gameStateId, child, i+1 ]
          res = DataManager.execute( """
            INSERT INTO GameStateChild
              ( GameStateId, ChildCode, Position )
            VALUES
              ( ?, ?, ? )
            """, inputs, "gameConn" )

      elif row['Type'] == 'Action':
        if row['CurrentStep'] == 'evening':

          inputs  = [ gameStateId, 'searchChoice', row['Decision']['action'] ]
          res = DataManager.execute( """
            INSERT INTO GameStateAction
              ( GameStateId, ActionType, Decision )
            VALUES
              ( ?, ?, ? )
            """, inputs, "gameConn" )

          if 'Decision2' in row:
            decision = row['Decision2']['action']
            if decision == 'addHobby':
              decision = row['Decision2']['hobbyCard'] 
            elif decision == 'addJob':
              decision = row['Decision2']['jobCard'] 
            elif decision == 'addPartner':
              decision = row['Decision2']['partnerCard'] 

            inputs  = [ gameStateId, row['Decision']['action'], decision ]
            res = DataManager.execute( """
              INSERT INTO GameStateAction
                ( GameStateId, ActionType, Decision )
              VALUES
                ( ?, ?, ? )
              """, inputs, "gameConn" )

        elif row['CurrentStep'] == 'night':

          decision = row['Decision']['action']
          if decision == 'quitHobby':
            decision = row['Decision']['hobbyCard']
          elif decision == 'quitJob':
            decision = row['Decision']['jobCard']
          elif decision == 'quitPartner':
            decision = row['Decision']['partnerCard']
          inputs  = [ gameStateId, 'dropChoice', decision ]
          res = DataManager.execute( """
            INSERT INTO GameStateAction
              ( GameStateId, ActionType, Decision )
            VALUES
              ( ?, ?, ? )
            """, inputs, "gameConn" )

    DataManager.execute( "UPDATE GameState SET FinalScore=? WHERE GameId=?", [lastRow['Points'],gameId], "gameConn" )
    DataManager.closeConnection("gameConn")

