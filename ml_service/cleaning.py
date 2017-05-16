import pandas as pd
from pymongo import MongoClient

pd.options.mode.chained_assignment = None


def _connect_mongo(host, port, username, password, db):
    """ A util for making a connection to mongo """

    if username and password:
        mongo_uri = 'mongodb://%s:%s@%s:%s/%s' % (username, password, host, port, db)
        conn = MongoClient(mongo_uri)
    else:
        conn = MongoClient(host, port)


    return conn[db]


def read_mongo(db, collection, query={}, host='localhost', port=27017, username=None, password=None, no_id=True):
    """ Read from Mongo and Store into DataFrame """

    # Connect to MongoDB
    db = _connect_mongo(host=host, port=port, username=username, password=password, db=db)

    # Make a query to the specific DB and Collection
    cursor = db[collection].find(query)

    # Expand the cursor and construct the DataFrame
    df =  pd.DataFrame(list(cursor))


    return df

def clean(df):

    mask = (
    (df.property_type != "Condo") & (df.property_type != "Single Family") & (df.property_type != "Multi Family") & (
    df.property_type != "Townhouse"))
    df = df[~mask]
    df = df[df.bedroom < 10]
    df = df[df.bathroom < 10]
    df = df[df.list_price > 0]
    df = df[df["size"] > 0]
    df = df[(df.bathroom != 0) & (df.bedroom != 0)]
    df.index = range(len(df))
    df["lotsize"] = getLot(df)
    df.drop(
        ["_id", "is_for_sale", "state", "street_address", "zipcode", "zpid", "description", "image_url", "last_update",
         "latitude", "longitude", "facts"], axis=1, inplace=True)
    return df

def getLot(df):
    lotsize = []
    for i in range(len(df["facts"])):
        count = 0
        for j in range(len(df["facts"][i])):
            if "Lot:" in df["facts"][i][j]:
                temp = df["facts"][i][j + 1].split()
                if temp[1] == "sqft":
                    res = temp[0].replace(",", "")
                    lotsize.append(int(res))
                if "acre" in temp[1]:
                    res = float(temp[0].replace(",", ""))
                    if res > 1000:
                        lotsize.append(res)
                    else:
                        lotsize.append(res * 43560)

                break
            count += 1
            if count + 1 == len(df["facts"][i]):
                lotsize.append(0)
    return lotsize

df = read_mongo(db="real_estate_smart_view_testing",collection="property_recently_sold")
df = clean(df)
df.to_csv(path_or_buf = "cleaned2.csv")
