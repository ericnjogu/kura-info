from google.appengine.ext import db
from django.forms import ModelForm
from appengine_django.models import BaseModel
#from google.appengine.ext.db import polymodel - bulkloading this did not work

class KuraModel(db.Model):
    name = db.StringProperty(required=True) #e.g KAMUKUNJI
    number = db.StringProperty(required=True) #e.g 002
    #pollStations = db.StringListProperty()
    year = db.IntegerProperty(required=True) #e.g. 2008
    nameStartsWith = db.StringProperty(required=True) # e.g K
    
    def __unicode__(self):
        return "Name:%s Number:%s Year:%s" % (self.name, self.number, self.year)

class Constcy(KuraModel):
    #name = db.StringProperty #e.g KAMUKUNJI
    #number = db.StringProperty #e.g 002
    #pollStations = db.StringListProperty()
    #year = db.IntegerProperty
    def __unicode__(self):
        return "Constituency %s" % (KuraModel.__unicode__(self))

class PollStation(KuraModel):
    #name = db.StringProperty #e.g. UPPER HILL SEC.
    #number = db.StringProperty
    belongsTo = db.StringProperty(required=True)
    #year = db.IntegerProperty
    def __unicode__(self):
        return "PollStation %s belongsTo:%s" % (KuraModel.__unicode__(self), self.belongsTo)

class Directions(BaseModel):#db.Model):
    text = db.StringProperty(required=True,multiline=True)
    #could refer to a model that stores a user profile
    #author = db.StringProperty(required=True)
    author = db.UserProperty(required=True)#, auto_current_user=True)
    #TODO rating = db.RatingPropert
    forStation = db.ReferenceProperty(reference_class=PollStation, required=True)

#TODO unit testauto_current_user
class Vote(db.Model):
    """a base model for vote objects"""
    #user who voted
    #TODO consider auto_current_user for user property
    user = db.UserProperty(required=True)
    time = db.DateTimeProperty(auto_now=True)

#TODO test
class DirectionVote(Vote):
    """a vote for a direction. the vote holds the value"""
    direction = db.ReferenceProperty(reference_class=Directions, required=True)
    value = db.StringProperty(choices=('up','down'), required=True)

class DirectionsForm(ModelForm):
    """
    get directions from user. author and forStation properties will be populated in the view after
    presentation to the user
    """
    class Meta:
        model = Directions
        fields = ('text',)#fields to show include