import re
import sqlite3
import csv

f = open('arctic-lemming/hobbyCards.csv')
fileCSV = csv.reader(f)
print fileCSV

conn = sqlite3.connect( "test.db" )

c = conn.cursor()

c.execute( "DELETE FROM Hobby" )
c.execute( "DELETE FROM HobbySkill" )
c.execute( "DELETE FROM HobbyNeed" )
c.execute( "DELETE FROM Need" )
c.execute( "DELETE FROM Skill" )

name_i = 0
skill_i = [ 1,2,3,4 ]
need_i = [ 5,6,7,8 ]

skills_in_db = []
needs_in_db = []

for ri,row in enumerate(fileCSV):
  if ri != 0:
    code = ""
    for ci,cell in enumerate(row):

      if ci == name_i:
        code = cell.title().replace( " ", "" )
        c.execute( "INSERT INTO Hobby ( HobbyCode, Name ) VALUES ( ?, ? )", [code, cell]  )


      if ci in skill_i and len(cell.replace(" ","")) > 0:
        skillParts = re.findall(r'([\w\s]+)([+-]\s*\d+)', cell)
        skillName = skillParts[0][0]
        skillName =  skillName.rstrip()
        skillCode = skillName.title().replace(" ", "")
        skillValue = skillParts[0][1].replace(" ", "")
        if skillName not in skills_in_db:
          skills_in_db.append(skillName)
          c.execute("INSERT INTO Skill (SkillCode, Name) VALUES ( ?, ?)", [skillCode, skillName])
        c.execute("INSERT INTO HobbySkill (HobbyCode, SkillCode, Value) VALUES ( ?, ?, ?)", [code, skillCode, skillValue ])

      if ci in need_i and len(cell.replace(" ","")) > 0:
        needParts = re.findall(r'([\w\s]+)([+-]\s*\$?\s*\d+)', cell)
        needName = needParts[0][0]
        needName =  needName.rstrip()
        needCode = needName.title().replace(" ", "")
        needValue = needParts[0][1].replace(" ", "")
        needValue = needValue.replace("$", "")
        print "%s __ %s __ %s __ %s __ %s" % (code,needCode,needValue, needName, cell)
        if needName not in needs_in_db:
          needs_in_db.append(needName)
          c.execute("INSERT INTO Need (NeedCode, Name) VALUES ( ?, ?)", [needCode, needName])
        c.execute("INSERT INTO HobbyNeed (HobbyCode, NeedCode, Value) VALUES ( ?, ?, ?)", [code, needCode, needValue ])

conn.commit()
conn.close()

