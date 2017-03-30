import mongodb_client
import pandas as pd

db = mongodb_client.getDB()
# db.test.insert({"test123" : "123"})
df = pd.DataFrame(list(db.property.find()))
print list(db.property.find())
print df
# print list(db.test.find({"test123": "123"}))