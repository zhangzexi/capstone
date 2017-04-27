import numpy as np
import pandas
import tensorflow as tf


# Feature, Label, Column
COLUMNS = ['index', 'bathroom', 'bedroom', 'city', 'geohash', 'list_price', 'property_type', 'school_ratingE', 'school_ratingH', 'school_ratingM', 'size', 'zestimate', 'lotsize']
CATEGORICAL_COLUMNS = ['geohash', 'property_type']
CONTINUOUS_COLUMNS = ['bedroom', 'bathroom', 'size', 'school_ratingE', 'school_ratingH', 'school_ratingM', 'zestimate', 'lotsize']
LABEL_COLUMN = 'list_price'
FEATURE_COLUMNS = ['geohash', 'property_type', 'bedroom', 'bathroom', 'size', 'school_ratingE', 'school_ratingH', 'school_ratingM', 'zestimate','list_price', 'lotsize']
CONTINUOUS_COLUMNS_WO_Z = ['bedroom', 'bathroom', 'size', 'school_ratingE', 'school_ratingH', 'school_ratingM', 'zestimate', 'lotsize']
FEATURE_COLUMNS_WO_Z = ['geohash', 'property_type', 'bedroom', 'bathroom', 'size', 'school_ratingE', 'school_ratingH', 'school_ratingM', 'zestimate','list_price', 'lotsize']
COLUMNS_WO_Z = ['index', 'bathroom', 'bedroom', 'city', 'geohash', 'list_price', 'property_type', 'school_ratingE', 'school_ratingH', 'school_ratingM', 'size', 'lotsize']

# input_fn return format: (feature_columns, label)
# feature_columns: {column_name : tf.constant}
# label: tf.constant
# def input_fn(df):
#     continuous_cols = {k: tf.constant(df[k].values, shape=[df[k].size, 1]) for k in CONTINUOUS_COLUMNS}
#     categorical_cols = {k: tf.SparseTensor(
#         indices=[[i, 0] for i in range(df[k].size)],
#         values=df[k].values,
#         dense_shape=[df[k].size, 1])
#             for k in CATEGORICAL_COLUMNS}
#     feature_columns = dict(continuous_cols.items() + categorical_cols.items())
#     label = tf.constant(df[LABEL_COLUMN].values)
#     return feature_columns, label

def input_fn(df):
    continuous_cols = {k: tf.constant(df[k].values) for k in CONTINUOUS_COLUMNS}
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
feature_columns_wo_z = [geohash, property_type, bedroom, bathroom, size_buckets, school_ratingE, school_ratingH, school_ratingM, lot_size_buckets]

