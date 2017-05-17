import json
import operations
import os
import pyjsonrpc
import sys
import time

from bson.json_util import dumps

# import client package in parent directory
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'client'))

import ml_prediction_client
import mongodb_client
import zillow_api_client
import zillow_web_scraper_client

SERVER_HOST = 'localhost'
SERVER_PORT = 4040

# DATA_FETCHER_QUEUE_NAME = 'dataFetcherTaskQueue'
PROPERTY_TABLE_NAME = 'property_for_sale'
PROPERTY_TABLE_NAME_FOR_LIKES = 'userlikes'

"""Search a property with specific address and citystatezip"""
def searchByAddress(address, citystatezip):
    res = zillow_api_client.getSearchResults(address, citystatezip)
    print res
    return res

"""Search properties by zip code"""
def searchAreaByZip(zipcode):
    properties = findProperyByZipcode(zipcode)
    if len(properties) == 0:
        properties = zillow_web_scraper_client.search_zillow_by_zip(zipcode)
    print properties
    return properties

"""Search properties by city and state"""
def searchAreaByCityState(city, state):
    res = zillow_web_scraper_client.search_zillow_by_city_state(city, state)
    print res
    return res

"""Search properties in an area"""
def searchArea(text):
    zpids = []
    if text.isdigit():
        zpids = searchAreaByZip(text)
    else:
        city = text.split(',')[0].strip()
        state = text.split(', ')[1].strip()
        zpids = searchAreaByCityState(city, state)
    print zpids
    res = []
    update_list = []
    db = mongodb_client.getDB()
    for zpid in zpids:
        record = db[PROPERTY_TABLE_NAME].find_one({'zpid': zpid})
        if record != None:
            res.append(record)
        else:
            property_detail = getDetailsByZpid(zpid, False)
            res.append(property_detail)
            update_list.append(property_detail)

    storeUpdates(update_list)

    # Trick: use bson.dumps then re-construct json because of ObjectId.
    return json.loads(dumps(res))

"""
Retrieve details by zillow property ID (zpid)
If get_predction is True, get value prediction from ml_prediction_service
"""
def getDetailsByZpid(zpid, get_prediction=False):
    db = mongodb_client.getDB()
    prop = json.loads(dumps(db[PROPERTY_TABLE_NAME].find_one({'zpid': zpid})))
    if prop == None or prop['zestimate'] == None:
        prop = zillow_web_scraper_client.get_property_by_zpid(zpid)

    ##Get prediction
    if get_prediction:
        prop['lotsize'] = getLot(prop)
        print getLot(prop)
        predicted_value = ml_prediction_client.predict(
            prop['property_type'],
            prop['bedroom'],
            prop['bathroom'],
            prop['geohash'],
            prop['school_ratingE'],
            prop['school_ratingH'],
            prop['school_ratingM'],
            prop['size'],
            prop['zestimate'],
            prop['lotsize']
        )

        prop['predicted_value'] = float(predicted_value)
        prop['zpid'] = zpid
    return prop

"""Update doc in db"""
def storeUpdates(properties):
    db = mongodb_client.getDB()

    for property_detail in properties:
        print property_detail
        zpid = property_detail['zpid']
        property_detail['last_update'] = time.time()
        db[PROPERTY_TABLE_NAME].replace_one({'zpid': zpid}, property_detail, upsert=True)


"""Search property by zipcode"""
def findProperyByZipcode(zipcode):
    db = mongodb_client.getDB()
    properties = list(db[PROPERTY_TABLE_NAME].find({'zipcode': zipcode, 'is_for_sale': True}))
    # res = []
    # for x in properties:
    #     res.append(x['zpid'])
    # print res
    return [x['zpid'] for x in properties]


"""getEstimation based on factors"""
def getEstimation(query):
    estimations = []
    current_predicted_value = ml_prediction_client.predictwoz(
        query["ptype"],
        float(query["bedr"]),
        float(query["bathr"]),
        query["geohash"],
        float(query["es"]),
        float(query["ms"]),
        float(query["hs"]),
        float(query["floor_size"]),
        float(query["lot_size"]),)
    new_predicted_value = ml_prediction_client.predictwoz(
        query["ptype"],
        float(query["new_bedr"]),
        float(query["new_bathr"]),
        query["geohash"],
        float(query["new_es"]),
        float(query["new_ms"]),
        float(query["new_hs"]),
        float(query["new_floor_size"]),
        float(query["new_lot_size"]),
        )

    estimations.append(float(current_predicted_value))
    estimations.append(float(new_predicted_value))
    return json.loads(dumps(estimations))

'''find lot size in facts'''
def getLot(prop):
    lotsize = 0
    for i in range(len(prop["facts"])):
        count = 0
        if "Lot:" in prop["facts"][i]:
            temp = prop["facts"][i+1].split()
            if temp[1] == "sqft":
                res = temp[0].replace(",", "")
                lotsize=(int(res))
            if "acre" in temp[1]:
                res = float(temp[0].replace(",", ""))
                if res > 1000:
                    lotsize=res
                else:
                    lotsize=(res * 43560)

            break
        count += 1
        if count + 1 == len(prop["facts"]):
            return 0
    return lotsize

"""get user likes"""
def getUserLikes(query):
    res = []
    db = mongodb_client.getDB()
    records = list(db[PROPERTY_TABLE_NAME_FOR_LIKES].find({'email' : query}))

    for record in records:
        detail = getDetailsByZpid(record['zpid'],False)
        # temp = {}
        # temp['img'] = detail['image_url']
        # temp['zpid'] = record['zpid']
        # temp['address'] = detail['street_address']
        # temp['']
        res.append(detail)

    return json.loads(dumps(res))



    # return [record['zpid'] for record in records]

# def findProperyByZipcode(zipcode):
#     db = mongodb_client.getDB()
#     properties = list(db[PROPERTY_TABLE_NAME].find({'zipcode': zipcode, 'is_for_sale': True}))
#     res = []
#     for x in properties:
#         res.append(x['zpid'])
#     print res
#     return [x['zpid'] for x in properties]
#
# def main():
#     getUserLikes([25965528, 25965524, 26083043, 25965209, 25965178])
#     #getDetailsByZpid(112094946,False)
#
# if __name__ == "__main__": main()