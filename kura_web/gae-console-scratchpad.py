'''
Created on Jun 14, 2010

@author: mugo
'''
from google.appengine.ext import db
#import models

#const = db.GqlQuery("select * from Constcy where number = :1", "002")
plstn = db.GqlQuery("select * from PollStation where belongsTo = :1", "MAKADARA")
print plstn.count()
#print dir(plstn)

for p in plstn:
 print p.belongsTo