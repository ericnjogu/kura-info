'''
Created on May 26, 2010

@author: mugo
'''
import unittest
from kura_web.models import Constcy, PollStation,Directions
import logging
from google.appengine.ext import db

class Test(unittest.TestCase):

    def setUp(self):
        #const
        self.const = Constcy(name = "Emba", year = 2010, number = "999", nameStartsWith="E")
        #polymodel
        self.station = PollStation(name = "Caltex", year = 2007, belongsTo = "Emba", number = "007", nameStartsWith="C")

    def tearDown(self):
        pass
    
    def test_local_consty(self):
        self.model_const_props_test(self.const)
        
    def test_local_poll(self):
        self.model_poll_props(self.station)
        
    def model_local_dirn(self):
        self.model_dirn_props(self.direction)

    def model_const_props_test(self, const):
        self.assertEqual("999", const.number)
        self.assertEqual(2010, const.year)
        self.assertEqual("Emba", const.name)
    
    def model_poll_props(self, station):
        self.assertEqual("007", station.number)
        self.assertEqual(2007, station.year)
        self.assertEqual("Caltex", station.name)
        self.assertEqual("Emba", station.belongsTo)
        
    def model_dirn_props(self, dirn):
        self.assertEquals("by the still waters\n I will walk", dirn.text)
        self.assertEquals("mimi", dirn.author)
        
    def test_put_gae_store(self):
#        key = self.const.put()
#        logging.info("create constcy with constcy_key %s" % key)
        #does not work for polymorphic classes
        #allConst = db.GqlQuery("select __key__ from Constcy where number = :1", "999")
        #allConst = Constcy.gql("where number = :1", "999")
        #self.assertEqual(1, allConst.count()) doesn't work
        #list = allConst.fetch(limit=1)
        #logging.debug(dir(list[0]))
        #self.model_const_props_test(allConst.get())
        
        #gae store
        constcy_key = self.const.put()
        logging.info("put constcy with key %s" % constcy_key)
        stn_key = self.station.put()
        logging.info("put station with key %s" % stn_key)
        #directions
        from google.appengine.api.users import User
        self.direction = Directions(text="by the still waters\n I will walk", author=User(email='test@example.com'),
                                     forStation=self.station)
        dirn_key = self.direction.put()
        logging.info("put direction with key %s" % dirn_key)
        #test retrieved values
        self.model_const_props_test(db.get(constcy_key))
        self.model_poll_props(db.get(stn_key))
        self.model_dirn_props(db.get(dirn_key))
        self.model_poll_props(db.get(dirn_key).forStation)#test model - station - referred to
        
        
        #test for polymorphic retrieval
#        query = KuraModel.all()
#        res = query.fetch(10)
#        self.assertEquals(2, len(res))


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()