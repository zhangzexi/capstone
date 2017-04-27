import pyjsonrpc

URL = "http://localhost:5050/"

client = pyjsonrpc.HttpClient(url=URL)

def predict(property_type, bedroom, bathroom, geohash, school_ratingE, school_ratingH, school_ratingM, size, zestimate, lotsize):
    predicted_value = client.call('predict', property_type, bedroom, bathroom, geohash, school_ratingE, school_ratingH, school_ratingM, size, zestimate, lotsize)
    # print "Predicted value: %f" % predicted_value[0]
    return predicted_value

def predictwoz(property_type, bedroom, bathroom, geohash, school_ratingE, school_ratingH, school_ratingM, size, lotsize):
    predicted_value = client.call('predictwoz', property_type, bedroom, bathroom, geohash, school_ratingE, school_ratingH, school_ratingM, size, lotsize)
    # print "Predicted value: %f" % predicted_value[0]
    return predicted_value
