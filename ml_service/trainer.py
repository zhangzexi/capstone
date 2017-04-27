import numpy as np
import pandas
import sys
import tensorflow as tf
from sklearn.model_selection import train_test_split
from ml_common import *


# Training Parameter
LEARNING_RATE = 500
STEPS = 1000

# Enable logging
tf.logging.set_verbosity(tf.logging.INFO)

CSV_FILE_PATH = '''~/PycharmProjects/capstone/ml_service/cleaned2.csv'''
if len(sys.argv) > 1:
    CSV_FILE_PATH = sys.argv[1]

CSV_FILE_FORMAT = {
    'index': np.float32,
    'bathroom': np.float32,
    'bedroom': np.float32,
    'city': str,
    'geohash': str,
    'list_price': np.float32,
    'property_type': str,
    'school_ratingE': np.float32,
    'school_ratingH': np.float32,
    'school_ratingM': np.float32,
    'size': np.float32,
    'zestimate': np.float32,
    'lotsize': np.float32,
}

MODEL_OUTPUT_DIR = "./model/"
MODEL_OUTPUT_DIR_WO_Z = "./modelwz"


# Set the output display to have one digit for decimal places, for display readability only.
pandas.options.display.float_format = '{:.1f}'.format

# Load in the data from CSV files.
property_dataframe = pandas.read_csv(CSV_FILE_PATH, dtype=CSV_FILE_FORMAT)
property_dataframe_wo_z = pandas.read_csv(CSV_FILE_PATH, dtype=CSV_FILE_FORMAT)

# Randomize the index.
property_dataframe = property_dataframe.reindex(
    np.random.permutation(property_dataframe.index))
property_dataframe_wo_z = property_dataframe.reindex(
    np.random.permutation(property_dataframe.index))

# Pick out the columns we care about.
property_dataframe = property_dataframe[COLUMNS]
property_dataframe_wo_z = property_dataframe_wo_z[COLUMNS_WO_Z]

# Clean up data
# property_dataframe = property_dataframe[property_dataframe['is_for_sale'] == True]
property_dataframe = property_dataframe[property_dataframe['list_price'] != 0]
property_dataframe_wo_z = property_dataframe_wo_z[property_dataframe_wo_z['list_price'] != 0]
# Drop rows with any value NaN
property_dataframe = property_dataframe.dropna()
property_dataframe_wo_z = property_dataframe_wo_z.dropna()


# Split data into training and test
train_dataframe, test_dataframe = train_test_split(property_dataframe, test_size=0.2)
predict_dataframe = property_dataframe.sample(frac=0.005)
train_dataframe_woz, test_dataframe_woz = train_test_split(property_dataframe_wo_z, test_size=0.2)
predict_dataframe_woz = property_dataframe_wo_z.sample(frac=0.005)
# train_dataframe = property_dataframe.sample(frac=0.9)
# #test_dataframe = property_dataframe.drop(train_dataframe.index)
# test_dataframe = property_dataframe.head(1)

train_features_label = train_dataframe[FEATURE_COLUMNS]
test_features_label = test_dataframe[FEATURE_COLUMNS]
predict_features_label = predict_dataframe[FEATURE_COLUMNS]

train_features_label_woz = train_dataframe[FEATURE_COLUMNS_WO_Z]
test_features_label_woz = test_dataframe[FEATURE_COLUMNS_WO_Z]
predict_features_label_woz = predict_dataframe[FEATURE_COLUMNS_WO_Z]
# feature_columns = [zipcode, property_type, bedroom, bathroom, size_buckets, longitude, latitude]

linear_regressor = tf.contrib.learn.LinearRegressor(
    feature_columns=feature_columns,
    optimizer=tf.train.AdamOptimizer(learning_rate=LEARNING_RATE),
    model_dir=MODEL_OUTPUT_DIR)

linear_regressor_woz = tf.contrib.learn.LinearRegressor(
    feature_columns=feature_columns_wo_z,
    optimizer=tf.train.AdamOptimizer(learning_rate=LEARNING_RATE),
    model_dir=MODEL_OUTPUT_DIR_WO_Z)
print "Training model..."


def input_fn_train():
    return input_fn(train_features_label)
def input_fn_train_woz():
    return input_fn(train_features_label_woz)

linear_regressor.fit(input_fn=input_fn_train, steps=np.float32(STEPS))
linear_regressor_woz.fit(input_fn=input_fn_train_woz, steps=np.float32(STEPS))

print "Model training finished."

print "Evaluating model..."


def input_fn_test():
    return input_fn(test_features_label)
def input_fn_test_woz():
    return input_fn(test_features_label_woz)

print linear_regressor.evaluate(input_fn=input_fn_test, steps=np.float32(10))
print linear_regressor_woz.evaluate(input_fn=input_fn_test_woz, steps=np.float32(10))

print "Model evaluation finished."


# print "Predicting model..."
#
#
# def input_fn_predict():
#     return input_fn(predict_features_label)
#
# prediction = linear_regressor.predict(input_fn=input_fn_predict)
# for i, p in enumerate(prediction):
#     print 'Prediction %s: %s' % (i + 1, p)
#
# print "Model prediction finished."
#
# print predict_features_label

# tensorboard --logdir='logs/'
