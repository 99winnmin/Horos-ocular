import io
import json
import pickle
from pprint import pprint
from struct import unpack

import boto3
import numpy

from HorusOculars.settings import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_STORAGE_BUCKET_NAME

npz = 'email@email.com/npz/western.npz'

s3r = boto3.resource('s3', aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
pickle_file = s3r.Bucket(AWS_STORAGE_BUCKET_NAME).Object(npz).get()['Body'].read()
l = numpy.load(io.BytesIO(pickle_file),allow_pickle=True)
pprint(len(l))