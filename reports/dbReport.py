import re
import sqlite3
import csv
import json

from DataManager import DataManager

csvOut = []

#SKILL TITLE ROW
csvOut.append( [ 'SKILLS'  ] )

#SKILL TABLE HEADER ROW
csvOut.append( [ 'Name', '# player points', '# jobs required for', 'job names', \
    'Total job point requirement', '# partners required for', 'Total partner point requirement' ] )

skill_rows = DataManager.getRows( "SELECT * FROM Skill ORDER BY Name" )
for skill in skill_rows:
  row = []
  row.append(skill['Name'])

  skill_code = skill['SkillCode']

  player_usage = DataManager.getRow( "SELECT SUM(Value) AS ValSum FROM PlayerSkill WHERE SkillCode=?", [skill_code] )
  row.append(player_usage['ValSum'])


  job_usage = DataManager.getRow( "SELECT COUNT(*) AS Cnt, SUM(Value) AS ValSum FROM JobSkillRequirement WHERE SkillCode=?", [skill_code] )
  jobs = DataManager.getRows( """
    SELECT 
      Job.Name 
    FROM 
      JOB 
      INNER JOIN JobSkillRequirement ON JobSkillRequirement.JobCode = Job.JobCode 
    WHERE 
      JobSkillRequirement.SkillCode=?
  """, [skill_code] )
  job_names = []
  for j in jobs:
    job_names.append(j['Name'])
  row.append( len(job_names) )
  row.append( ", ".join(job_names) )
  row.append( job_usage['ValSum'] )

  partner_usage = DataManager.getRow( "SELECT COUNT(*) AS Cnt, SUM(Value) AS ValSum FROM PartnerSkillRequirement WHERE SkillCode=?", [skill_code] )
  partners = DataManager.getRows( """
    SELECT 
      Partner.Name 
    FROM 
      Partner
      INNER JOIN PartnerSkillRequirement ON PartnerSkillRequirement.PartnerCode = Partner.PartnerCode 
    WHERE 
      PartnerSkillRequirement.SkillCode=?
  """, [skill_code] )
  row.append(job_usage['Cnt'])
  row.append(job_usage['ValSum'])

  csvOut.append(row)

print csvOut
csvOutFile = open( DataManager.setting('dbReportOutCsvPath'), 'wb' )
wr = csv.writer( csvOutFile, quoting=csv.QUOTE_ALL )
for row in csvOut:
  wr.writerow(row)
csvOutFile.close()
