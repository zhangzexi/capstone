import numpy as np
import pandas
import pyjsonrpc
import tensorflow as tf
import time
from ml_common import *
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import simplejson as json
##from bson.json_util import dumps

SERVER_HOST = 'localhost'
SERVER_PORT = 5050

MODEL_DIR = './model'
MODEL_DIR_WO_Z = './modelwz'
MODEL_UPDATE_LAG = 5

linear_regressor = tf.contrib.learn.LinearRegressor(
    feature_columns=feature_columns,
    model_dir=MODEL_DIR)

linear_regressor_woz = tf.contrib.learn.LinearRegressor(
    feature_columns=feature_columns_wo_z,
    model_dir=MODEL_DIR_WO_Z)

print "Model loaded"

class ReloadModelHandler(FileSystemEventHandler):
    def on_any_event(self, event):
        # Reload model
        print "Model update detected. Loading new model."
        time.sleep(MODEL_UPDATE_LAG)
        linear_regressor = tf.contrib.learn.LinearRegressor(
            feature_columns=feature_columns,
            model_dir=MODEL_DIR)
        linear_regressor_woz = tf.contrib.learn.LinearRegressor(
            feature_columns=feature_columns_wo_z,
            model_dir=MODEL_DIR_WO_Z)
        print "Model updated."

class RequestHandler(pyjsonrpc.HttpRequestHandler):
    """Test method"""
    @pyjsonrpc.rpcmethod
    def predict(self, property_type, bedroom, bathroom, geohash, school_ratingE, school_ratingH, school_ratingM, size, zestimate, lotsize):
        if(zestimate == None or size == None):
            return -1
        sample = pandas.DataFrame({
            'property_type': property_type,
            'bedroom': bedroom,
            'bathroom': bathroom,
            'geohash': geohash,
            'school_ratingE': school_ratingE,
            'school_ratingH': school_ratingH,
            'school_ratingM': school_ratingM,
            'size': size,
            'zestimate': zestimate,
            'lotsize': lotsize,
            'list_price': 0
            }, index=[0])
        def input_fn_predict():
            return input_fn(sample)
        prediction = linear_regressor.predict(input_fn=input_fn_predict)
        prediction_value = str(list(prediction)[0])

        print prediction_value
        return prediction_value

    """Test method"""

    @pyjsonrpc.rpcmethod
    def predictwoz(self, property_type, bedroom, bathroom, geohash, school_ratingE, school_ratingH, school_ratingM, size,
                 lotsize):
        sample = pandas.DataFrame({
            'property_type': property_type,
            'bedroom': bedroom,
            'bathroom': bathroom,
            'geohash': geohash,
            'school_ratingE': school_ratingE,
            'school_ratingH': school_ratingH,
            'school_ratingM': school_ratingM,
            'size': size,
            'lotsize': lotsize,
            'zestimate' : 0,
            'list_price': 0
        }, index=[0])

        def input_fn_predict():
            return input_fn(sample)

        prediction = linear_regressor_woz.predict(input_fn=input_fn_predict)
        prediction_value = str(list(prediction)[0])

        print prediction_value
        return prediction_value



# Setup watchdog
observer = Observer()
observer.schedule(ReloadModelHandler(), path=MODEL_DIR, recursive=False)
observer.schedule(ReloadModelHandler(), path=MODEL_DIR_WO_Z, recursive=False)
observer.start()

# Threading HTTP-Server
http_server = pyjsonrpc.ThreadingHttpServer(
    server_address = (SERVER_HOST, SERVER_PORT),
    RequestHandlerClass = RequestHandler
)

print "Starting predicting server ..."
print "URL: http://" + str(SERVER_HOST) + ":" + str(SERVER_PORT)

http_server.serve_forever()
