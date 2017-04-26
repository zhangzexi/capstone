import numpy as np
import sys
import pandas
import tensorflow as tf
from sklearn.model_selection import train_test_split


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

# Feature, Label, Column
COLUMNS = ['index', 'bathroom', 'bedroom', 'city', 'geohash', 'list_price', 'property_type', 'school_ratingE', 'school_ratingH', 'school_ratingM', 'size', 'zestimate', 'lotsize']
CATEGORICAL_COLUMNS = ['geohash', 'property_type']
CONTINUOUS_COLUMNS = ['bedroom', 'bathroom', 'size', 'school_ratingE', 'school_ratingH', 'school_ratingM', 'zestimate', 'lotsize']
LABEL_COLUMN = 'list_price'

FEATURE_COLUMNS = ['geohash', 'property_type', 'bedroom', 'bathroom', 'size', 'school_ratingE', 'school_ratingH', 'school_ratingM', 'list_price', 'zestimate', 'lotsize']


def input_fn(df):
    continuous_cols = {k: tf.constant(df[k].values, shape=[df[k].size, 1]) for k in CONTINUOUS_COLUMNS}
    categorical_cols = {k: tf.SparseTensor(
        indices=[[i, 0] for i in range(df[k].size)],
        values=df[k].values,
        dense_shape=[df[k].size, 1])
            for k in CATEGORICAL_COLUMNS}
    feature_columns = dict(continuous_cols.items() + categorical_cols.items())
    label = tf.constant(df[LABEL_COLUMN].values)
    return feature_columns, label

# Hanlding columns
geohash = tf.contrib.layers.sparse_column_with_hash_bucket("geohash", hash_bucket_size=10000)
# zipcode = tf.contrib.layers.sparse_column_with_hash_bucket("zipcode", hash_bucket_size=1000)
property_type = tf.contrib.layers.sparse_column_with_hash_bucket("property_type", hash_bucket_size=10)
bedroom = tf.contrib.layers.real_valued_column("bedroom")
bathroom = tf.contrib.layers.real_valued_column("bathroom")
size = tf.contrib.layers.real_valued_column("size")
size_buckets = tf.contrib.layers.bucketized_column(size, boundaries=np.arange(6000, step=200).tolist())
# longitude = tf.contrib.layers.real_valued_column("longitude")
# latitude = tf.contrib.layers.real_valued_column("latitude")
school_ratingE = tf.contrib.layers.real_valued_column("school_ratingE")
school_ratingH = tf.contrib.layers.real_valued_column("school_ratingH")
school_ratingM = tf.contrib.layers.real_valued_column("school_ratingM")
zestimate = tf.contrib.layers.real_valued_column("zestimate")
lot_size = tf.contrib.layers.real_valued_column("lotsize")
lot_size_buckets = tf.contrib.layers.bucketized_column(lot_size, boundaries=np.arange(6000, step=200).tolist())

feature_columns = [geohash, property_type, bedroom, bathroom, size_buckets, school_ratingE, school_ratingH, school_ratingM, zestimate, lot_size_buckets]

MODEL_OUTPUT_DIR = "./model/"


# Set the output display to have one digit for decimal places, for display readability only.
pandas.options.display.float_format = '{:.1f}'.format

# Load in the data from CSV files.
property_dataframe = pandas.read_csv(CSV_FILE_PATH, dtype=CSV_FILE_FORMAT)


# Randomize the index.
property_dataframe = property_dataframe.reindex(
    np.random.permutation(property_dataframe.index))


# Pick out the columns we care about.
property_dataframe = property_dataframe[COLUMNS]

# Clean up data
# property_dataframe = property_dataframe[property_dataframe['is_for_sale'] == True]
property_dataframe = property_dataframe[property_dataframe['list_price'] != 0]
# Drop rows with any value NaN
property_dataframe = property_dataframe.dropna()


# Split data into training and test
train_dataframe, test_dataframe = train_test_split(property_dataframe, test_size=0.2)
predict_dataframe = property_dataframe.sample(frac=0.005)
# train_dataframe = property_dataframe.sample(frac=0.9)
# #test_dataframe = property_dataframe.drop(train_dataframe.index)
# test_dataframe = property_dataframe.head(1)

train_features_label = train_dataframe[FEATURE_COLUMNS]
test_features_label = test_dataframe[FEATURE_COLUMNS]
predict_features_label = predict_dataframe[FEATURE_COLUMNS]
# feature_columns = [zipcode, property_type, bedroom, bathroom, size_buckets, longitude, latitude]

linear_regressor = tf.contrib.learn.LinearRegressor(
    feature_columns=feature_columns,
    optimizer=tf.train.AdamOptimizer(learning_rate=LEARNING_RATE),
    model_dir=MODEL_OUTPUT_DIR)

print "Training model..."


def input_fn_train():
    return input_fn(train_features_label)


linear_regressor.fit(input_fn=input_fn_train, steps=np.float32(STEPS))

print "Model training finished."

print "Evaluating model..."


def input_fn_test():
    return input_fn(test_features_label)

print linear_regressor.evaluate(input_fn=input_fn_test, steps=np.float32(10))

print "Model evaluation finished."


print "Predicting model..."


def input_fn_predict():
    return input_fn(predict_features_label)

prediction = linear_regressor.predict(input_fn=input_fn_predict)
for i, p in enumerate(prediction):
    print 'Prediction %s: %s' % (i + 1, p)

print "Model prediction finished."

print predict_features_label

# tensorboard --logdir='logs/'