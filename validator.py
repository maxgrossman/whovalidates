
# coding: utf-8

# In[11]:

# code: validator
# purpose: module to make and describe validators 

import requests

# validator - includes name and uid, osm-stats info 
class validator:
        
    def __init__(self, name, uid):
        self.name = str(name)
        self.uid = str(uid)
    
    # get validator info from osm-stats api and set it to info obj
    def userInfo(self):
        OSMstats = "http://osmstats.redcross.org/"
        # catch when osmstats is not available
        try:
            OSMstatsStatus = requests.get(OSMstats).raise_for_status()
        except requests.exceptions.HTTPError as httpErr:
            print(httpErr)
        # get user info from osm stats
        OSMstatsEP = OSMstats + '/user/' + self.uid
        OSMstatsResponse = requests.get(OSMstatsEP)
        self.info = OSMstatsResponse.json()

