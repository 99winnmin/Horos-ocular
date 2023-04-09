import io
import os
import pickle

import boto3
import numpy as np
from django.shortcuts import get_object_or_404
from tensorflow import keras
from HorusOculars.settings import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_STORAGE_BUCKET_NAME, RESOURCE_URL
from horus.models import Video, VInfo


def make_embedding_vetors(user, input_video, face_list):
    FACENET = keras.models.load_model('C:\\Users\\ojyse\\PycharmProjects\\HorusOculars\\HorusOculars\\videoModuler\\facenet_keras.h5')
    em_vec_list = list()
    for i in face_list:
        face_pixels = i.astype('float32')
        mean, std = face_pixels.mean(), face_pixels.std()

        face_pixels = (face_pixels - mean) / std
        samples = np.expand_dims(face_pixels, axis=0)

        em_vec = FACENET.predict(samples)[0]
        em_vec_list.append(em_vec)

    npz_data = io.BytesIO()
    pickle.dump(em_vec_list, npz_data)
    npz_data.seek(0)

    s3r = boto3.resource('s3', aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
    key = "%s" % (user.email) + "/resource"
    s3r.Bucket(AWS_STORAGE_BUCKET_NAME).put_object(Key=key + '/%s/%s' % ((str(input_video)[:-4]),(str(input_video)[:-4])+'.npz'), Body=npz_data)
    npz_url = RESOURCE_URL + "%s" % (key) + "/%s"%str(input_video)[:-4]+'.npz'

    video = get_object_or_404(Video, vname=input_video)
    video.npz_url = key + "/%s/%s" % ((str(input_video)[:-4]),(str(input_video)[:-4])+'.npz')
    video.save()

    VInfo.objects.create(
        video=video,
        video_info_id=key + "/%s/%s" % ((str(input_video)[:-4]),(str(input_video)[:-4])+'.npz')
    )
    return key + "/%s/%s" % ((str(input_video)[:-4]),(str(input_video)[:-4])+'.npz')

def input_img_ev(face_list):
    FACENET = keras.models.load_model('C:\\Users\\ojyse\\PycharmProjects\\HorusOculars\\HorusOculars\\videoModuler\\facenet_keras.h5')
    em_vec_list = list()
    for i in face_list:
        face_pixels = i.astype('float32')
        mean, std = face_pixels.mean(), face_pixels.std()

        face_pixels = (face_pixels - mean) / std
        samples = np.expand_dims(face_pixels, axis=0)

        em_vec = FACENET.predict(samples)[0]
        em_vec_list.append(em_vec)

    return em_vec_list
