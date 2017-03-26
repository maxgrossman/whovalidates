# coding: utf-8
# code: validator
# purpose: module to make and describe validators 

import requests
#from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
import datetime

# validator - includes name and uid, osm-stats info 
class validator:
        
    def __init__(self, name, uid):
        self.name = str(name)
        self.uid = str(uid)
    
    # get validator info from osm-stats api and set it to info obj
    def userStats(self):
        osmStats = "http://osmstats.redcross.org/users/" + self.uid 
        # catch when osmstats is not available
        try:
            osmstatsResponse = requests.get(osmStats)
            osmstatsResponse.raise_for_status()
            # get user info from osm stats
            OSMstatsResponse = requests.get(osmStats)
            self.osmStats = OSMstatsResponse.json()
        except requests.exceptions.HTTPError as httpErr:
            print("osmstats seems to not be responding")
            print(httpErr)
        

    # get validator # Changesets and age of osm account
    def userChangesetsDays(self):
        osm = "http://api.openstreetmap.org/api/0.6/user/" + self.uid
        # catch when openstreetmap is not available
        try:
            apiResponse = requests.get(osm)
            apiResponse.raise_for_status()
            # get xml of user profile
            osmUserXML = ET.fromstring(requests.get(osm + self.uid).text)
            # get number of changesets and edits
            cs = osmUserXML[0][4].attrib['count']
            # get account age
            accountCreated = osmUserXML[0].attrib['account_created'].split('T')[0]
            today = datetime.datetime.now()
            acctAge = today - datetime.datetime.strptime(accountCreated,'%Y-%m-%d')
            acctAge = acctAge.days
            # set validator's cs,days attribute
            self.changesets = cs
            self.acctAge = acctAge
        except requests.exceptions.HTTPError:
            # when user profile does not exist, 
            self.changesets = None
            self.acctAge = None        
        
        
        
        
