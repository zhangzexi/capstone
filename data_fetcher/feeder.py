import os
import sys
import time

# import common package in parent directory
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'client'))

import zillow_web_scraper_client

from cloudAMQP_client import CloudAMQPClient

CLOUD_AMQP_URL = 'amqp://dginpavm:rF4k66V_6V7kH3hhzpe7epAALlukODjs@donkey.rmq.cloudamqp.com/dginpavm'
DATA_FETCHER_QUEUE_NAME = 'dataFetcherTaskQueue'
ZIPCODE_FILE = 'bay_area_zipcode_list.txt'
WAITING_TIME = 1

cloudAMQP_client = CloudAMQPClient(CLOUD_AMQP_URL, DATA_FETCHER_QUEUE_NAME)

zipcode_list = []

with open(ZIPCODE_FILE, 'r') as zipcode_file:
    for zipcode in zipcode_file:
        zipcode_list.append(str(zipcode))

for zipcode in zipcode_list:
    zpids = zillow_web_scraper_client.search_zillow_by_zip(zipcode)

    time.sleep(WAITING_TIME)
    if zpids is not None:
        for zpid in zpids:
            print zpid
            cloudAMQP_client.sendDataFetcherTask({'zpid': zpid})
    else:
        continue