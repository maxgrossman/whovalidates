#!/usr/bin/python
# encoding: utf-8
# code: validator
# purpose: module to make and describe validators

## libraries ##

# make http requests
import requests
# make sense of xml api responses
import xml.etree.ElementTree as ET
# convert date strings to datetime objects to do math with
from datetime import datetime

# validator object - object representing an osm user including name and uid, osm-stats info
class validator:
    
    # initalize the object and its parameters
    def __init__(self, name, uid):
        self.name = str(name)
        self.uid = str(uid)

    # method to get oms user info from osm-stats api and set it to the validator obj's info obj
    def userStats(self):
        # api endpoint for specific user
        osmStats = "http://osmstats.redcross.org/users/" + self.uid
        # try to reach osm-stats. when non-responsive, throw error (the except statement)
        # when responsive, go to else and set osmStatsResponse and the osmStats object
        try:
            # try to retrieve data at user endpoint of osm stats
            osmstatsResponse = requests.get(osmStats)
            # get status of response 
            osmstatsResponse.raise_for_status()
        # if status of response is an error, break
        except requests.exceptions.HTTPError as httpErr:
            print("osmstats seems to not be responding")
            print(httpErr)
        # if no error, save response as described
        else:
            self.osmStats = osmstatsResponse.json()

    # get number of validator changesets and account age
    def userChangesetsAge(self):
        # api endpoint for specific user
        osm = "http://api.openstreetmap.org/api/0.6/user/" + self.uid
        # catch when user's osm account is not there.
        # when the case, return None for change-sets and account age
        try:
            apiResponse = requests.get(osm)
            apiResponse.raise_for_status()
        except requests.exceptions.HTTPError:
            print("User account not active.")
            self.changesets = None
            self.acctAge = None
        # when responsive
        else:
            # get xml of user profile
            osmUserXML = ET.fromstring(apiResponse.text)
            # get number of changesets and edits from the xml
            cs = osmUserXML[0][4].attrib['count']
            # get account age from the xml
            accountCreated = osmUserXML[0].attrib['account_created'].split('T')[0]
            # make a date-time object of today 
            today = datetime.now()
            # calculate delta of day account was generated to today 
            acctAge = today - datetime.strptime(accountCreated,'%Y-%m-%d')
            # get that detla in days, and set that as account age
            acctAge = acctAge.days
            # set validator's number of changesets and says the validator changests and acctAge objects
            self.changesets = cs
            self.acctAge = acctAge
            
    # get user's mapping frequency
    def userMapFreq(self):
        # get edit times
        editTimes = [datetime.strptime(i.split('.')[0],"%Y-%m-%dT%H:%M:%S")
                     for i in self.osmStats['edit_times']]
        # get edit deltas
        editDeltas = [(j-i).seconds for i,j in
                     zip(editTimes[:-1], editTimes[1:])]
        # return the mean of edit editDetlas
        if len(editDeltas) < 0 :
            return sum(editDeltas)/len(editDeltas)
        else:
            return 0
