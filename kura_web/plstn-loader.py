'''
Created on May 26, 2010

@author: mugo
 run in kura_web with 
 python2.5 ~/bin/appcfg.py upload_data --config=plstn-loader.py --filename=/home/mugo/apps/polling-stations/poll-stations.csv --kind=PollStation --url=http://localhost:8181/remote_api ../
'''
from google.appengine.ext import db
from google.appengine.tools import bulkloader
import models

class PlstnLoader(bulkloader.Loader):
    '''
    upload polling station data
    '''
    def __init__(self):
        '''
        Constructor
        '''
        bulkloader.Loader.__init__(self, 'PollStation', 
                                   [('belongsTo', str),
                                    ('number', str),
                                    ('name', str),
                                    ('year', int),
                                    ('nameStartsWith', str)
                                    ])
loaders = [PlstnLoader]