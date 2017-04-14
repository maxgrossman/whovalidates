#!/usr/bin/python
# encoding: utf-8
# code: validator
# purpose: module to make and describe validators

import requests
import xml.etree.ElementTree as ET
from datetime import datetime

# validator - includes name and uid, osm-stats info
class validator:

    def __init__(self, name, uid):
        self.name = str(name)
        self.uid = str(uid)

    # get validator info from osm-stats api and set it to info obj
    def userStats(self):
        osmStats = "http://osmstats.redcross.org/users/" + self.uid
        # catch when osmstats is not available, when no response just throw error
        try:
            osmstatsResponse = requests.get(osmStats)
            osmstatsResponse.raise_for_status()
        except requests.exceptions.HTTPError as httpErr:
            print("osmstats seems to not be responding")
            print(httpErr)
        else:
            # get user info from osm stats
            self.osmStats = osmstatsResponse.json()


    # get validator # Changesets and age of osm account
    def userChangesetsAge(self):
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
        else:
            # get xml of user profile
            osmUserXML = ET.fromstring(apiResponse.text)
            # get number of changesets and edits
            cs = osmUserXML[0][4].attrib['count']
            # get account age
            accountCreated = osmUserXML[0].attrib['account_created'].split('T')[0]
            today = datetime.now()
            acctAge = today - datetime.strptime(accountCreated,'%Y-%m-%d')
            acctAge = acctAge.days
            # set validator's cs,days attribute
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
