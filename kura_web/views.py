'''
Created on Jun 17, 2010

@author: mugo
'''
#TODO could load static files via an appropriate urlconf entry e.g. static/*.html
#TODO use a common method to retrieve both constituencies and poll stations - with appropriate parameters
from django.shortcuts import render_to_response,redirect
from google.appengine.api import memcache
from kura_web.models import Constcy, PollStation, Directions, DirectionsForm
import logging
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from google.appengine.api.users import User

#TODO items per page will be a user preference
items_per_page = 15
logger = logging.getLogger('kura_web.views')
logger.setLevel(logging.DEBUG)

def index(request):
    return render_to_response('kura_web/index.html')

def about(request):
    return render_to_response('kura_web/about.html')

#show constituency alphabetical listing
def constics(request, page_num):
    logger.info("showing constituency grouping page %s" % page_num)
    return render_to_response("kura_web/constituency-alphabet-count%s.html" % page_num)

def constics_starting_with(request, letter, page_num):
    letter = letter.upper()
    key = "constcy-list-starts-with-%s" % letter
    list = memcache.get(key)
    if list is None:
        logger.info("constituencies starting with '%s' not found in memcache." % letter)
        list = []
        res = Constcy.gql("where nameStartsWith = :1 order by name  ASC", letter)
        for cn in res:
            list.append(cn)
        memcache.add(key, list)
    if len(list) == 0:#not found
        err_msg = "No constituencies were found beginning with '%s'" % letter
        return render_to_response('kura_web/constituency-alphabet-view.html', {'error_message': err_msg, 'letter': letter})
    else:#list found in memcache or retrieved from datastore
        return render_to_response('kura_web/constituency-alphabet-view.html', 
                                  {'letter': letter, 'page':page_object_list(list, page_num)})
    
def page_object_list(list, page_num):
    """get a page from a long list of results"""
    paginator = Paginator(list, items_per_page)#show ten per page, could be based on a user pref
    #deliver first page if not an int
    try:
        page = int(page_num)
    except ValueError:
        page = 1
    # check that page is within range, if not give last page
    try:
        paged_list = paginator.page(page)
    except (EmptyPage, InvalidPage):
        paged_list = paginator.page(paginator.num_pages)
    return paged_list

def poll_stations_for(request, const_name, page_num):
    const_name = const_name.upper()
    key = "%s-stations-info" % const_name
    #stn_info is a dict contains the list of stations and the jump to alphabetical dict 
    stn_info = memcache.get(key)
    if stn_info is None:
        logger.info("poll station list for '%s' not found in memcache." % const_name)
        list = []
        res = PollStation.gql("where belongsTo = :1 order by name ASC", const_name)
        #create a map that will hold a "jump to" page number alphabetically
        jump_to = {}
        #loop counter, start at items per page so that page number starts at 1
        counter = items_per_page
        #hold letters already seen
        letter_set = []
        for stn in res:
            counter = counter + 1
            list.append(stn)
            #populate map if first letter not present
            #find out if key exists, record only first occurrence
            if stn.nameStartsWith not in letter_set:
                letter_set.append(stn.nameStartsWith)
                page_to = counter / items_per_page
                if page_to not in jump_to:
                    #create a list that holds all letters starting on same page
                    jump_to[page_to] = [stn.nameStartsWith]
                else:#add to existing letter starting on this page
                    jump_to[page_to].append(stn.nameStartsWith)
        #logger.info(jump_to)
        memcache.add(key, {'stations':list, 'jump_to':jump_to})
    else:#retrieve from memcache dict
        list = stn_info['stations']
        jump_to = stn_info['jump_to']
    if len(list) == 0:#not found
        err_msg = "No Poll stations were found for '%s'" % const_name
        return render_to_response('kura_web/constituency-stations-view.html', {'error_message': err_msg, 'const_name': const_name})
    else:
        #poll station list found in memcache of db
        return render_to_response('kura_web/constituency-stations-view.html', 
                                  {'const_name': const_name, 'page':page_object_list(list, page_num), 'jump_to':jump_to})
    
def view_pollstation(request, const_name, stn_name):
    const_name = const_name.upper()
    stn_name = stn_name.upper()
    key = "directions-%s-%s" % (stn_name, const_name)
    list = memcache.get(key)
    if list is None:
        logger.info("directions for station '%s' in constcy %s not found in memcache." % (stn_name,const_name))
        list = [] #initialize empty list
        #retrieve station from memcache or datastore
        stn = retrieve_station_from_memcache_or_db(const_name, stn_name)
        if stn is None:#polling station not found
            err_msg = "No poll station named '%s' was found. for constituency '%s'" % (stn_name,const_name)
            return render_to_response('kura_web/station-view.html', {'error_message': err_msg, 'const_name': const_name, 'stn_name': stn_name,})
        #retrieve directions and loop
        res = stn.directions_set
        for dirn in res:
            list.append(dirn)
    if len(list) == 0:#no directions found
        err_msg = "No directions were found for '%s'." % stn_name
        return render_to_response('kura_web/station-view.html', {'error_message': err_msg, 'const_name': const_name, 'stn_name': stn_name,})
    else:
        memcache.add(key, list) #save direction list to memcache
        return render_to_response('kura_web/station-view.html', {'const_name': const_name, 'dirn_list':list, 'stn_name': stn_name,})
    
def add_pollstation_direction(request, const_name, stn_name):
    """
        Handles a form POST to add a direction to a polling station
    """ 
    logger.debug("entered add_pollstation_direction")
    if request.method == 'POST':
        form = DirectionsForm(request.POST)
        if form.is_valid():
            stn =  retrieve_station_from_memcache_or_db(const_name, stn_name)
            if stn is not None:#stn was found
                logger.debug("stn %s was found" % stn_name)
                #TODO logged on user should be used here
                dirn = Directions(text=form.cleaned_data['text'] ,forStation=stn, author=User(email='bubujika@yahoo.com'))
                dirn.put()
                key = "directions-%s-%s" % (stn_name, const_name)
                #TODO add direction to memcache list if available - is that wise?
                memcache.set(key, None) #clear contents to refresh
                return redirect("kura_web.views.view_pollstation", const_name=const_name, stn_name=stn_name,)
        else:
            logger.debug("form is not valid")
    else:
        form = DirectionsForm()#set to unbound form
    return render_to_response("kura_web/add-poll-station-direction.html",
                               {'form':form,'const_name':const_name, 'stn_name':stn_name,}) 
    

def retrieve_station_from_memcache_or_db(const_name, stn_name):
    """ Retrieve polling station from memcache  if it exists. If not, try the datastore """
    #check if any arg is none and return none TODO - is that the best way
    if const_name is None or stn_name is None:
        logger.error("const_name or stn_name is None. Return None")
        return None 
    #check if poll station had been fetched into memcache
    stn_key = "poll-station-%s-%s" % (stn_name, const_name)
    stn = memcache.get(stn_key)
    if (stn is None): #not in memcache, fetch from db
        logger.info("key %s not found in memcache" % stn_key),
        #expects one result TODO, more that one result should not break the app
        stn_res = PollStation.gql("where belongsTo=:cn and name=:nm", cn=const_name, nm=stn_name).fetch(1)
        if (len(stn_res)) == 0:#polling station, const combi not found
            logger.info("%s-%s not found" % (stn_name, const_name))
            return None
        else:
            #retrieve first poll station from result list
            memcache.set(stn_key, stn_res[0])
            return stn_res[0]
    else:
        return stn#from memcache
