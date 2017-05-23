import random
import re
import requests
import Geohash
from decimal import Decimal
from lxml import html
from re import sub
from urllib import pathname2url
import pandas as pd
URL = '''http://www.zillow.com'''
SEARCH_FOR_SALE_PATH = '''homes/for_sale'''
GET_PROPERTY_BY_ZPID_PATH = '''homes'''
GET_SIMILAR_HOMES_FOR_SALE_PATH = '''homedetails'''
IMAGE_URL_REGEX_PATTERN = '"z_listing_image_url":"([^"]+)",'
SIMILAR_HOMES_ZPID_REGEX_PATTERN ='\/(\d+)_zpid'

SEARCH_XPATH_FOR_ZPID = '''//div[@id='list-results']/div[@id='search-results']/ul[@class='photo-cards']/li/article/@id'''
GET_INFO_XPATH_FOR_STREET_ADDR = '''//header[@class='zsg-content-header addr']/h1[@class='notranslate']/text()'''
GET_INFO_XPATH_FOR_CITY_STATE_ZIP = '''//header[@class='zsg-content-header addr']/h1[@class='notranslate']/span/text()'''
GET_INFO_XPATH_FOR_TYPE = '''//div[@class='loan-calculator-container']/div/@data-type'''
GET_INFO_XPATH_FOR_BEDROOM = '''//header[@class='zsg-content-header addr']/h3/span[@class='addr_bbs'][1]/text()'''
GET_INFO_XPATH_FOR_BATHROOM = '''//header[@class='zsg-content-header addr']/h3/span[@class='addr_bbs'][2]/text()'''
GET_INFO_XPATH_FOR_SIZE = '''//header[@class='zsg-content-header addr']/h3/span[@class='addr_bbs'][3]/text()'''
GET_INFO_XPATH_FOR_SALE = '''//div[@id='home-value-wrapper']/div[@class='estimates']/div/text()'''
GET_INFO_XPATH_LIST_FOR_PRICE = '''//div[@id='home-value-wrapper']/div[@class='estimates']/div[@class='main-row  home-summary-row']/span/text()'''
GET_INFO_XPATH_FOR_LATITUDE = '''//div[@class='zsg-layout-top']/p/span/span[@itemprop='geo']/meta[@itemprop='latitude']/@content'''
GET_INFO_XPATH_FOR_LONGITUDE = '''//div[@class='zsg-layout-top']/p/span/span[@itemprop='geo']/meta[@itemprop='longitude']/@content'''
GET_INFO_XPATH_DESCRIPTION = '''//div[@class='zsg-lg-2-3 zsg-md-1-1 hdp-header-description']/div[@class='zsg-content-component']/div/text()'''
GET_INFO_XPATH_FOR_FACTS = '''//div[@class='fact-group-container zsg-content-component top-facts']/ul/li/text()'''
GET_INFO_XPATH_FOR_ADDITIONAL_FACTS = '''//div[@class='fact-group-container zsg-content-component z-moreless-content hide']/ul/li/text()'''
GET_SIMILAR_HOMES_FOR_SALE_XPATH = '''//ol[@id='fscomps']/li/div[@class='zsg-media-img']/a/@href'''
GET_K5_SCHOOLRATING_XPATH = '''//*[@id="nearbySchools"]/div/div[3]/ul/li[2]/div[1]/span/text()'''
GET_6TO8_SCHOOLRATING_XPATH = '''//*[@id="nearbySchools"]/div/div[3]/ul/li[3]/div[1]/span/text()'''
GET_9TO12_SCHOOLRATING_XPATH ='''//*[@id="nearbySchools"]/div/div[3]/ul/li[4]/div[1]/span/text()'''
GET_INFO_XPATH_FOR_ZESTIMATE = '''//*[@id="home-value-wrapper"]/div[1]/div[3]/span[2]/text()'''

GET_INFO_XPATH_FOR_FACTS_NEW = '''//*[@class="zsg-sm-1-1 hdp-fact-list"]/li/span/text()'''
# Load user agents
USER_AGENTS_FILE = '../client/user_agents.txt'
USER_AGENTS = []

with open(USER_AGENTS_FILE, 'rb') as uaf:
    for ua in uaf.readlines():
        if ua:
            USER_AGENTS.append(ua.strip())
random.shuffle(USER_AGENTS)

def build_url(url, path):
    if url[-1] == '/':
        url = url[:-1]
    return '%s/%s' % (url, path)

def getHeaders():
    ua = random.choice(USER_AGENTS)  # select a random user agent
    headers = {
        "Connection" : "close",
        "User-Agent" : ua
    }
    return headers

def search_zillow(request_url, xpath):
    session_requests = requests.session()
    try:
        response = session_requests.get(request_url, headers=getHeaders())
    except Exception:
        print "feeder error"
        return None
    tree = html.fromstring(response.content)
    return tree.xpath(xpath)

""" Search properties by zip code """
def search_zillow_by_zip(zipcode):
    request_url = '%s/%s' % (build_url(URL, SEARCH_FOR_SALE_PATH), str(zipcode))
    raw_result = search_zillow(request_url, SEARCH_XPATH_FOR_ZPID)
    if raw_result is not None:
        return [x.replace('zpid_', '') for x in raw_result]
    else:
        return None
""" Search properties by city and state """
def search_zillow_by_city_state(city, state):
    city_state = pathname2url('%s %s' % (city, state))
    request_url = '%s/%s' % (build_url(URL, SEARCH_FOR_SALE_PATH), city_state)
    raw_result =  search_zillow(request_url, SEARCH_XPATH_FOR_ZPID)
    if raw_result is not None:
        return [x.replace('zpid_', '') for x in raw_result]
    else:
        return None
""" Get Similar homes for sale """
def get_similar_homes_for_sale_by_id(zpid):
    request_url = '%s/%s_zpid' % (build_url(URL, GET_SIMILAR_HOMES_FOR_SALE_PATH), str(zpid))
    raw_result = search_zillow(request_url, GET_SIMILAR_HOMES_FOR_SALE_XPATH)
    if raw_result is not None:
        return [re.search(SIMILAR_HOMES_ZPID_REGEX_PATTERN, x).group(1) for x in raw_result]
    else:
        return None

##handle lotsize in facts

def lotsize_fact(facts):
    lot_size = 0
    for i in range(len(facts)):
        if "Lot:" in facts[i]:
            lot_index = facts[i].index("Lot:")
            lot_count = 0
            lot_length = 0
            for char in facts[i][lot_index:]:
                if char != "'":
                    lot_count += 1
                else:
                    lot_length = lot_count + lot_index
                    break

            lot = facts[i][lot_index:lot_length]
            if "sqft" in lot:
                if "," in lot:
                    lot_split = lot.split()[-2].split(",")
                    lot_value = ""
                    for n in lot_split:
                        lot_value += n
                else:
                    lot_value = lot.split()[-2]
                lot_size = float(lot_value)
                return lot_size
            if "acre" in lot:
                if "," in lot:
                    lot_split = lot.split()[-2].split(",")
                    lot_value = ""
                    for n in lot_split:
                        lot_value += n
                    lot_value = float(lot_value)
                    if lot_value > 1000:
                        lot_size = float(lot_value)
                        return lot_size
                    else:
                        lot_value = lot_value * 43560
                        lot_size = float(lot_value)
                        return lot_size
                else:
                    lot_value = float(lot.split()[-2]) * 43560
                    lot_size = float(lot_value)
                    return lot_size

        else:
            return lot_size

""" Get property information by Zillow Property ID (zpid) """
def get_property_by_zpid(zpid):
    request_url = '%s/%s_zpid' % (build_url(URL, GET_PROPERTY_BY_ZPID_PATH), str(zpid))
    session_requests = requests.session()
    try:
        response = session_requests.get(request_url, headers=getHeaders())
    except Exception:
        print "get_p_by_zpid error"
        return {}

    tree = html.fromstring(response.content)
    # Street address
    street_address = None
    try:
        street_address = tree.xpath(GET_INFO_XPATH_FOR_STREET_ADDR)[0].strip(', ')
    except Exception:
        pass

    # City, state and zipcode
    city_state_zip = None
    city = None
    state = None
    zipcode = None
    try:
        city_state_zip = tree.xpath(GET_INFO_XPATH_FOR_CITY_STATE_ZIP)[0]
        city = city_state_zip.split(',')[0].strip(', ')
        state = city_state_zip.split(',')[1].split(' ')[1].strip(', ')
        zipcode = city_state_zip.split(',')[1].split(' ')[2].strip(', ')
    except Exception:
        pass

    # Type: Condo, Town hourse, Single family etc.
    property_type = None
    try:
        property_type = tree.xpath(GET_INFO_XPATH_FOR_TYPE)[0]
    except Exception:
        pass

    # Bedroom
    bedroom = None
    try:
        bedroom = float(tree.xpath(GET_INFO_XPATH_FOR_BEDROOM)[0].split(' ')[0])
    except Exception:
        bedroom = 0

    # Bathroom (float since bathroom can be .5)
    bathroom = None
    try:
        bathroom = float(tree.xpath(GET_INFO_XPATH_FOR_BATHROOM)[0].split(' ')[0])
    except Exception:
        bathroom = 0

    # Square feet
    size = None
    try:
        size = int(tree.xpath(GET_INFO_XPATH_FOR_SIZE)[0].split(' ')[0].replace(',', ''))
    except Exception:
        size = 0

    # Is for sale
    for_sale_text = tree.xpath(GET_INFO_XPATH_FOR_SALE)
    r = re.compile('.+For Sale.+')
    is_for_sale = len(filter(r.match, for_sale_text)) > 0

    # Listed price
    list_price = None
    try:
        list_price_raw = tree.xpath(GET_INFO_XPATH_LIST_FOR_PRICE)
        if len(list_price_raw) > 0:
            list_price = float(list_price_raw[0].replace(',', '').strip(' $'))
    except Exception:
        if SEARCH_FOR_SALE_PATH == '''homes/for_sale''':
            list_price = -1

    # geo + geohash
    latitude = None
    longitude = None
    geohash = None
    try:
        latitude = float(tree.xpath(GET_INFO_XPATH_FOR_LATITUDE)[0])
        longitude = float(tree.xpath(GET_INFO_XPATH_FOR_LONGITUDE)[0])
        geohash = Geohash.encode(latitude,longitude,precision=6)
    except Exception:
        pass

    # Image
    image_url = None
    try:
        r = re.compile(IMAGE_URL_REGEX_PATTERN)
        result = r.search(response.content)
        image_url = result.group(1)
    except Exception:
        pass

    # Description
    description = None
    try:
        description = tree.xpath(GET_INFO_XPATH_DESCRIPTION)
    except Exception:
        pass

    # Basic facts
    facts = None

    try:
        facts = tree.xpath(GET_INFO_XPATH_FOR_FACTS)
        if len(facts) == 0:
            facts = ["Not Provided"]
    except Exception:
        facts = ["Not Provided"]

    # Additional facts
    additional_facts = None
    try:
        additional_facts = tree.xpath(GET_INFO_XPATH_FOR_ADDITIONAL_FACTS)
    except Exception:
        pass

    # School rating
    schoolratingE = None
    schoolratingM = None
    schoolratingH = None
    try:
        schoolratingE = float(tree.xpath(GET_K5_SCHOOLRATING_XPATH)[0])
        schoolratingM = float(tree.xpath(GET_6TO8_SCHOOLRATING_XPATH)[0])
        schoolratingH = float(tree.xpath(GET_9TO12_SCHOOLRATING_XPATH)[0])
    except Exception:
        pass

    #similar zpids
    szpids = []
    try:
        szpids = get_similar_homes_for_sale_by_id(zpid)
        if len(szpids) == 0:
            szpids = ["123465789"]

    except Exception:
        szpids = ["123465789"]

    #zEstimate
    zestimate = None
    try:
        zestimate_raw = tree.xpath(GET_INFO_XPATH_FOR_ZESTIMATE)
        if len(zestimate_raw) > 0:
            zestimate = float(zestimate_raw[0].replace(',', '').strip(' $'))
            if SEARCH_FOR_SALE_PATH == '''homes/for_sale''':
                if zestimate == 0:
                    zestimate = list_price
    except Exception:
        if SEARCH_FOR_SALE_PATH == '''homes/for_sale''':
            zestimate = list_price

    #facts
    facts = None
    try :
        facts = tree.xpath(GET_INFO_XPATH_FOR_FACTS_NEW)
    except Exception:
        pass

    return {
            'zpid' : zpid,
            'street_address' : street_address,
            'city' : city,
            'state' : state,
            'zipcode' : zipcode,
            'property_type' : property_type,
            'bedroom' : bedroom,
            'bathroom' : bathroom,
            'size' : size,
            'latitude' : latitude,
            'longitude' : longitude,
            'geohash' : geohash,
            'is_for_sale' : is_for_sale,
            'list_price' : list_price,
            'image_url' : image_url,
            'description' : description,
            # 'facts' : facts,
            # 'additional_facts' : additional_facts,
            'school_ratingE' : schoolratingE,
            'school_ratingM': schoolratingM,
            'school_ratingH': schoolratingH,
            'facts': facts,
            'zestimate': zestimate,
            'szpids' : szpids
            }

"""Get properties' information by zipcode"""
def get_properties_by_zip(zipcode):
    zpids = search_zillow_by_zip(zipcode)
    if zpids is not None:
        return [get_property_by_zpid(zpid) for zpid in zpids]
    else:
        return None
"""Get properties' information by city and state"""
def get_properties_by_city_state(city, state):
    zpids = search_zillow_by_city_state(city, state)
    return [get_property_by_zpid(zpid) for zpid in zpids]

