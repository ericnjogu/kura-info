'''
Created on May 26, 2010

@author: mugo
** Will only populate data successfully if all properties are required=True
run with
local - in src/kura_web
python2.5 ~/bin/appcfg.py upload_data --config=constcy-loader.py --filename=/home/mugo/apps/polling-stations/constituencies.csv --kind=Constcy --url=http://localhost:8181/remote_api --has_header ../
appspot
appcfg.py upload_data --config=constcy-loader.py --filename=/home/mugo/apps/polling-stations/constituencies.csv --kind=Constcy --url=http://www.kura-info.appspot.com/remote_api ../
'''
from google.appengine.ext import db
#from google.appengine.ext.db import polymodel 
from google.appengine.tools import bulkloader
import models

class ConstyLoader(bulkloader.Loader):
    '''
    upload constituency data
    '''
    def __init__(self):
        '''
        Constructor
        '''
        bulkloader.Loader.__init__(self, 'Constcy', 
                                   [('name', str),
                                    ('number', str),
                                    ('year', int),
                                    ('nameStartsWith', str)
                                    ])
loaders = [ConstyLoader]