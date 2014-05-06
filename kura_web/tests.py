'''
Created on Jul 18, 2010

@author: mugo
'''
import unittest
from models import Constcy, PollStation,Directions, DirectionsForm
import views
import logging
from google.appengine.ext import db
from google.appengine.api import memcache
from google.appengine.api.users import User
from django.test.client import Client

logger = logging.getLogger('tests')

class BaseTest(unittest.TestCase):

    def setUp(self):
        #const
        self.const = self.create_consty()
        #polymodel
        self.station = self.create_station() 
        
    def create_consty(self):
        return Constcy(name = "EMBA", year = 2010, number = "999", nameStartsWith="E")
    
    def create_station(self):
        return PollStation(name = "Caltex", year = 2007, belongsTo = "EMBA", number = "007", nameStartsWith="C")
    
    def store_entity(self,  how_many, create_function):
        """ create how_many constcy objects using create_function and store them """
        for x in range(how_many):
            entity = create_function()
            entity.put()
        
    def tearDown(self):
        pass
            
    def model_const_props_test(self, const):
        self.assertEqual("999", const.number)
        self.assertEqual(2010, const.year)
        self.assertEqual("EMBA", const.name)
    
    def model_poll_props(self, station):
        self.assertEqual("007", station.number)
        self.assertEqual(2007, station.year)
        self.assertEqual("Caltex", station.name)
        self.assertEqual("EMBA", station.belongsTo)
        
    def model_dirn_props(self, dirn):
        self.assertEquals("by the still waters\n I will walk", dirn.text)
        self.assertEquals(User(email='test@example.com'), dirn.author)


class ViewTests(BaseTest):

#    def setup(self):
#        self.BaseTest.setup()
#        #create dummy constcy's
#        self.store_constcy(11)
        
    def test_retrieve_station_in_db(self):
        self.station.put()
        self.model_poll_props(views.retrieve_station_from_memcache_or_db("EMBA", "Caltex"))
        
    def test_retrieve_station_in_memcache(self):
        memcache.add("poll-station-%s-%s" % ("Caltex", "EMBA"),self.station)
        self.model_poll_props(views.retrieve_station_from_memcache_or_db("EMBA", "Caltex"))
        
    def test_retrieve_station_with_none(self):
        self.assertEqual(None, views.retrieve_station_from_memcache_or_db(None, None))
        
    def test_constics_starting_with(self):
        #check that there are no prior constcy entities in the datastore
        qc = Constcy.all()
        rc = qc.fetch(1000)
        self.assertEquals(0, len(rc))
        #store some test entities
        self.store_entity(16, self.create_consty)
        #create a client to run tests with
        client = Client()
        response = client.get('/constituencies/alphabetical/E/page/1/')
        self.failUnlessEqual(response.status_code, 200)
        #logger.info(len(response.context['cn_list']))
        self.assertEquals('E', response.context['letter'])
        #logger.info(response.context)
        self.assertEquals(15, len(response.context['page'].object_list))
        response = client.get('/constituencies/alphabetical/E/page/2/')
        self.assertEquals(1, len(response.context['page'].object_list))
        response = client.get('/constituencies/alphabetical/E/page/1.7/')
        self.assertEquals(404, response.status_code)
    
    def test_poll_stations_for(self):
        #create test poll station entities
        self.store_entity(31, self.create_station)
        #add extra poll station to test for jump to
        stn = self.create_station()
        stn.nameStartsWith = "X"
        stn.put()
        #create a client to run tests with
        client = Client()
        response = client.get('/constituencies/Emba/page/1/')
        self.failUnlessEqual(response.status_code, 200)
        self.assertEquals('EMBA', response.context['const_name'])
        self.assertEquals(15, len(response.context['page'].object_list))
        self.assertEquals(("X"), response.context['jump_to'][3][0])
        response = client.get('/constituencies/Emba/page/3/')
        self.assertEquals(2, len(response.context['page'].object_list))
        self.assertEquals(2, len(response.context['jump_to']))
        
    def test_view_pollstation(self):
        client = Client()
        response = client.get('/constituencies/Emba/Caltex/')
        self.failUnlessEqual(response.status_code, 200)
        self.assertNotEquals(None, response.context['error_message'])
        
    def test_add_pollstation_direction(self):
        client = Client()
        response = client.post('/constituencies/Emba/Caltex/add-directions/')
        #logger.info(response.context)
        self.failUnlessEqual(response.status_code, 200)#show form ok
        response = client.post('/constituencies/Emba/Caltex/add-directions/',{'text':"Some Directions"})
        self.failUnlessEqual(response.status_code, 302)#redirect to directions
        
class ModelTests(BaseTest):

    def tearDown(self):
        pass
        
    def test_local_consty(self):
        self.model_const_props_test(self.const)
        
    def test_local_poll(self):
        self.model_poll_props(self.station)
        
    def test_put_gae_store(self):
#        key = self.const.put()
#        logger.info("create constcy with constcy_key %s" % key)
        #does not work for polymorphic classes
        #allConst = db.GqlQuery("select __key__ from Constcy where number = :1", "999")
        #allConst = Constcy.gql("where number = :1", "999")
        #self.assertEqual(1, allConst.count()) doesn't work
        #list = allConst.fetch(limit=1)
        #logger.debug(dir(list[0]))
        #self.model_const_props_test(allConst.get())
        
        #gae store
        constcy_key = self.const.put()
        logger.info("put constcy with key %s" % constcy_key)
        stn_key = self.station.put()
        logger.info("put station with key %s" % stn_key)
        #directions
        self.direction = Directions(text="by the still waters\n I will walk", author=User(email='test@example.com'),
                                     forStation=self.station)
        dirn_key = self.direction.put()
        logger.info("put direction with key %s" % dirn_key)
        #test retrieved values
        self.model_const_props_test(db.get(constcy_key))
        self.model_poll_props(db.get(stn_key))
        self.model_dirn_props(db.get(dirn_key))
        self.model_poll_props(db.get(dirn_key).forStation)#test model - station - referred to
        #tear down since db is maintained till the end of all test cases
        self.const.delete()
        self.station.delete()
        #test for polymorphic retrieval
#        query = KuraModel.all()
#        res = query.fetch(10)
#        self.assertEquals(2, len(res))
    def test_directions_form(self):
        form = DirectionsForm()
        self.assertNotEqual(None, form)

#def suite():
#    """return tests in a suitable order since the test database is only destroyed at the end of all tests"""
#    suite = unittest.TestLoader().loadTestsFromTestCase(ViewTests)
#    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(ModelTests))
#    return suite


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()