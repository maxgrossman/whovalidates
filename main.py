# coding: utf-8
# code: main
# purpose: build csv of validators and non-validators

from validator import validator
import requests
import pandas as pd

#%% GET LIST OF VALIDATORS

#get users from osm stats, reduce to list of users
usersJSON = requests.get("http://osmstats.redcross.org/users").json()

#%% GET LIST OF USERS' # EDITS, # VALIDATIONS, and EDITOR USED

# list to hold dictionaries for each to be used to make dataframe
usersInfoList = []

for user in usersJSON[352:len(usersJSON)]:
    # create validator object for current user, grab edits and stats
    user = validator(user['name'],user['id'])
    user.userStats()
    user.userChangesetsDays()
    # use badge pointer here (bit.ly/2nUQfaP) to guess rough # edits made
    numValidation = [item["level"] for item in user.osmStats['badges'] 
                    if item["name"] == "Scrutinizer"]
    if 3 in numValidation:
        numValidation = 100
    elif 2 in numValidation:
        numValidation = 50
    elif 1 in numValidation:
        numValidation = 25
    # append validator info of interest usersInfoList
    usersInfoList.append({
        "user_name": user.name,
        "user_id": user.uid,
        "build_count_add":user.osmStats['total_building_count_add'],
        "build_count_mod":user.osmStats['total_building_count_mod'],
        "poi_count_add":user.osmStats['total_poi_count_add'],
        "road_km_add":user.osmStats['total_road_km_add'],
        "road_km_mod":user.osmStats['total_road_km_mod'],
        "waterway_km_add":user.osmStats['total_waterway_count_add'],
        "validations": numValidation,
        "changesets": user.changesets,
        "acct_age": user.acctAge,
        "josm_edits": user.osmStats['total_josm_edit_count']
    })
    
#%% Make DATAFRAME FROM usersInfoList

validators= pd.DataFrame(usersInfoList)


