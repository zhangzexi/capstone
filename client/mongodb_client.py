from pymongo import MongoClient

MONGO_DB_HOST = 'localhost'
MONGO_DB_PORT = '27017'
DB_NAME = 'real-estate-smart-view'


client = MongoClient('%s:%s' % (MONGO_DB_HOST, MONGO_DB_PORT))

# db = client[DB_NAME]
# db.test.insert({"test123" : "123"})
def getDB(name=DB_NAME):
    db = client[name]
    return db














