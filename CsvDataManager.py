import re
import sqlite3
import csv
import json

class CsvDataManager(object):

  settings = []
  settingFilePath = 'CsvDataManager.json'

  #Manages class settings loaded from CsvDataManager.json
  @staticmethod
  def setting(pSettingName):
    if len(CsvDataManager.settings) == 0:
      jsonFile = open( CsvDataManager.settingFilePath )
      try: 
        CsvDataManager.settings = json.loads(jsonFile.read())
      except ValueError, e:
        print "INVALID JSON SETTINGS FILE - EXITING"
        exit()
    if pSettingName in CsvDataManager.settings:
      return CsvDataManager.settings[pSettingName]
    else:
      return None

  #Converts a name to a code (ex: 'Help the World' => 'HelpTheWorld' )
  @staticmethod
  def nameToCode(pCode):
    code = pCode.title().replace( " ", "" )
    aliases = CsvDataManager.setting("codeAliases")
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
    code = CsvDataManager.nameToCode( name )
    value = parts[0][1].replace(" ", "")
    value = value.replace("$", "")
    return { 'code': code, 'name': name, 'value': value }


  #Imports the data from CSV files into the SQLite DB
  @staticmethod
  def csvToDb():

    conn = sqlite3.connect( CsvDataManager.setting('dbPath') )

    c = conn.cursor()

    c.execute( "DELETE FROM Need" )
    c.execute( "DELETE FROM Skill" )

    c.execute( "DELETE FROM Hobby" )
    c.execute( "DELETE FROM HobbySkill" )
    c.execute( "DELETE FROM HobbyNeed" )

    c.execute( "DELETE FROM Player" )
    c.execute( "DELETE FROM PlayerSkill" )
    c.execute( "DELETE FROM PlayerNeed" )

    c.execute( "DELETE FROM Child" )
    c.execute( "DELETE FROM ChildSkill" )
    c.execute( "DELETE FROM ChildNeed" )

    c.execute( "DELETE FROM Partner" )
    c.execute( "DELETE FROM PartnerSkillRequirement" )
    c.execute( "DELETE FROM PartnerNeed" )

    skillsInDb = []
    needsInDb = []

    #
    #########################     IMPORT FROM HOBBY FILE     ######################### 
    nameColumn =  0
    skillColumns = []
    needColumns = []
    f = open( CsvDataManager.setting('hobbyCardCsvPath') )
    hobbyFileCSV = csv.reader(f)
    for ri,row in enumerate(hobbyFileCSV):

      # header row: determine what each column is
      if ri == 0:
        for ci,cell in enumerate(row):
          if re.findall( r'Hobby', cell ):
            nameColumn = ci
          elif re.findall( r'Skill', cell ):
            skillColumns.append(ci)
          elif re.findall( r'Need', cell ):
            needColumns.append(ci)

      # data row
      else:
        hobbyCode = ""
        for ci,cell in enumerate(row):

          #Hobby name column
          if ci == nameColumn:
            hobbyCode = CsvDataManager.nameToCode( cell )
            c.execute( "INSERT INTO Hobby ( HobbyCode, Name ) VALUES ( ?, ? )", [hobbyCode, cell]  )

          #Skill columns
          if ci in skillColumns and len(cell.replace(" ","")) > 0:
            cellParts = CsvDataManager.parseNameValueCell( cell )
            if cellParts['code'] not in skillsInDb:
              skillsInDb.append(cellParts['code'])
              c.execute("INSERT INTO Skill (SkillCode, Name) VALUES ( ?, ?)", [cellParts['code'], cellParts['name']])
            c.execute("INSERT INTO HobbySkill (HobbyCode, SkillCode, Value) VALUES ( ?, ?, ?)", [hobbyCode, cellParts['code'], cellParts['value'] ])

          #Needs columns
          if ci in needColumns and len(cell.replace(" ","")) > 0:
            cellParts = CsvDataManager.parseNameValueCell( cell )
            if cellParts['code'] not in needsInDb:
              needsInDb.append(cellParts['code'])
              c.execute("INSERT INTO Need (NeedCode, Name) VALUES ( ?, ?)", [cellParts['code'], cellParts['name']])
            c.execute("INSERT INTO HobbyNeed (HobbyCode, NeedCode, Value) VALUES ( ?, ?, ?)", [hobbyCode, cellParts['code'], cellParts['value'] ])


    #
    #########################     IMPORT FROM PLAYER FILE     ######################### 
    nameColumn =  0
    skillColumns = []
    skillColumnMap = {}
    needColumns = []
    f = open( CsvDataManager.setting('playerCardCsvPath') )
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
            skillCode = CsvDataManager.nameToCode(skillName)
            skillColumnMap.update( {ci:skillName} )
            if skillCode not in skillsInDb:
              skillsInDb.append(skillCode)
              c.execute("INSERT INTO Skill (SkillCode, Name) VALUES ( ?, ?)", [skillCode, skillName])
          elif re.findall( r'Need', cell ):
            needColumns.append(ci)

      # data row
      else:
        playerCode = ""
        for ci,cell in enumerate(row):
          cell = cell.strip()

          #Player name column
          if ci == nameColumn:
            playerCode = CsvDataManager.nameToCode( cell )
            c.execute( "INSERT INTO Player ( PlayerCode, Name ) VALUES ( ?, ? )", [playerCode, cell]  )

          #Skill columns
          if ci in skillColumns and len(cell) > 0:
            c.execute("INSERT INTO PlayerSkill (PlayerCode, SkillCode, Value) VALUES ( ?, ?, ?)", [playerCode, skillColumnMap[ci], cell ])

          #Needs columns
          if ci in needColumns and len(cell) > 0:
            cellParts = CsvDataManager.parseNameValueCell( cell )
            if cellParts['code'] not in needsInDb:
              needsInDb.append(cellParts['code'])
              c.execute("INSERT INTO Need (NeedCode, Name) VALUES ( ?, ?)", [cellParts['code'], cellParts['name']])
            c.execute("INSERT INTO PlayerNeed (PlayerCode, NeedCode, Value) VALUES ( ?, ?, ?)", [playerCode, cellParts['code'], cellParts['value'] ])



    #
    #########################     IMPORT FROM CHILD FILE     ######################### 
    nameColumn = -1
    costColumn = -1 
    skillColumns = []
    needColumns = []
    f = open( CsvDataManager.setting('childCardCsvPath') )
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
            childCode = CsvDataManager.nameToCode( cell )
            c.execute( "INSERT INTO Child ( ChildCode, Name, Cost ) VALUES ( ?, ?, 0 )", [childCode, cell]  )

          #Skill columns
          if ci in skillColumns and len(cell) > 0:
            cellParts = CsvDataManager.parseNameValueCell( cell )
            if cellParts['code'] not in skillsInDb:
              skillsInDb.append(cellParts['code'])
              c.execute("INSERT INTO Skill (SkillCode, Name) VALUES ( ?, ?)", [cellParts['code'], cellParts['name']])
            c.execute("INSERT INTO ChildSkill (ChildCode, SkillCode, Value) VALUES ( ?, ?, ?)", [childCode, cellParts['code'], cellParts['value'] ])

          #Needs columns
          if ci in needColumns and len(cell) > 0:
            cellParts = CsvDataManager.parseNameValueCell( cell )
            if cellParts['code'] not in needsInDb:
              needsInDb.append(cellParts['code'])
              c.execute("INSERT INTO Need (NeedCode, Name) VALUES ( ?, ?)", [cellParts['code'], cellParts['name']])
            c.execute("INSERT INTO ChildNeed (ChildCode, NeedCode, Value) VALUES ( ?, ?, ?)", [childCode, cellParts['code'], cellParts['value'] ])

          #Cost column
          if ci == costColumn:
            cell = cell.replace( " ", "" )
            cell = cell.replace( "$", "" )
            c.execute( "UPDATE Child SET Cost=? WHERE ChildCode=?", [cell, childCode]  )




    #########################     IMPORT FROM PARTNER FILE     ######################### 
    nameColumn = -1
    financesColumn = -1 
    skillRequirementColumns = []
    needColumns = []
    f = open( CsvDataManager.setting('partnerCardCsvPath') )
    partnerFileCSV = csv.reader(f)
    partnerMaxRow = CsvDataManager.setting('partnerCardCsvMaxRow');
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
            partnerCode = CsvDataManager.nameToCode( cell )
            c.execute( "INSERT INTO Partner ( PartnerCode, Name, Finances, MoneyRequirement ) VALUES ( ?, ?, 0, 0 )", [partnerCode, cell]  )

          #Skill columns
          if ci in skillRequirementColumns and len(cell) > 0:
            cellParts = CsvDataManager.parseNameValueCell( cell )
            if cellParts['code'] == 'Savings':
              c.execute( "UPDATE Partner SET MoneyRequirement=? WHERE PartnerCode=?", [cellParts['value'], partnerCode]  )
            else:
              if cellParts['code'] not in skillsInDb:
                skillsInDb.append(cellParts['code'])
                c.execute("INSERT INTO Skill (SkillCode, Name) VALUES ( ?, ?)", [cellParts['code'], cellParts['name']])
              c.execute("INSERT INTO PartnerSkillRequirement (PartnerCode, SkillCode, Value) VALUES ( ?, ?, ?)", [partnerCode, cellParts['code'], cellParts['value'] ])

          #Needs columns
          if ci in needColumns and len(cell) > 0:
            cellParts = CsvDataManager.parseNameValueCell( cell )
            if cellParts['code'] not in needsInDb:
              needsInDb.append(cellParts['code'])
              c.execute("INSERT INTO Need (NeedCode, Name) VALUES ( ?, ?)", [cellParts['code'], cellParts['name']])
            c.execute("INSERT INTO PartnerNeed (PartnerCode, NeedCode, Value) VALUES ( ?, ?, ?)", [partnerCode, cellParts['code'], cellParts['value'] ])

          #Finances column
          if ci == financesColumn:
            cell = cell.replace( " ", "" )
            cell = cell.replace( "$", "" )
            c.execute( "UPDATE Partner SET Finances=? WHERE PartnerCode=?", [cell, partnerCode]  )




    #########################     IMPORT FROM JOB FILE     ######################### 
    nameColumn = -1
    payColumn = -1 
    skillRequirementColumns = []
    needColumns = []
    f = open( CsvDataManager.setting('jobCardCsvPath') )
    jobFileCSV = csv.reader(f)
    jobMaxRow = CsvDataManager.setting('jobCardCsvMaxRow');
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
            jobCode = CsvDataManager.nameToCode( cell )
            c.execute( "INSERT INTO Job ( JobCode, Name, Pay ) VALUES ( ?, ?, 0 )", [jobCode, cell]  )

          #Skill columns
          if ci in skillRequirementColumns and len(cell) > 0:
            cellParts = CsvDataManager.parseNameValueCell( cell )
            if cellParts['code'] not in skillsInDb:
              skillsInDb.append(cellParts['code'])
              c.execute("INSERT INTO Skill (SkillCode, Name) VALUES ( ?, ?)", [cellParts['code'], cellParts['name']])
            c.execute("INSERT INTO JobSkillRequirement (JobCode, SkillCode, Value) VALUES ( ?, ?, ?)", [jobCode, cellParts['code'], cellParts['value'] ])

          #Needs columns
          if ci in needColumns and len(cell) > 0:
            cellParts = CsvDataManager.parseNameValueCell( cell )
            if cellParts['code'] not in needsInDb:
              needsInDb.append(cellParts['code'])
              c.execute("INSERT INTO Need (NeedCode, Name) VALUES ( ?, ?)", [cellParts['code'], cellParts['name']])
            c.execute("INSERT INTO JobNeed (JobCode, NeedCode, Value) VALUES ( ?, ?, ?)", [jobCode, cellParts['code'], cellParts['value'] ])

          #Pay column
          if ci == payColumn:
            cell = cell.replace( " ", "" )
            cell = cell.replace( "$", "" )
            if len( re.findall( r'[^-0-9]', cell ) ) == 0:
              c.execute( "UPDATE Job SET Pay=? WHERE JobCode=?", [cell, jobCode]  )

    conn.commit()
    conn.close()


