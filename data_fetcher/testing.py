import os
import sys
import time

# import common package in parent directory
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'client'))
import mongodb_client
import zillow_web_scraper_client

from cloudAMQP_client import CloudAMQPClient

ZIPCODE_FILE = 'bay_area_zipcode_list.txt'
WAITING_TIME = 3

zipcode_list = []
COUNT = 0
with open(ZIPCODE_FILE, 'r') as zipcode_file:
    for zipcode in zipcode_file:
        zipcode_list.append(str(zipcode))

for zipcode in zipcode_list:
    zpids = zillow_web_scraper_client.search_zillow_by_zip(zipcode)

    # time.sleep(WAITING_TIME)
    if zpids is not None:
        for zpid in zpids:
            COUNT = COUNT + 1
            print COUNT
            cloudAMQP_client.sendDataFetcherTask({'zpid': zpid})
    else:
        continue

for zip in zipcode_list:
    if zip is not None:
        for x in range(1,21):
            try:
                
            for i in  client.get_properties_by_zip(str(zip) + '/'+ str(x) +'_p/'):
                print count
                count = count + 1