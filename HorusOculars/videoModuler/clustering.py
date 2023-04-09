import base64
import collections
import hashlib
import io
import pickle
from pprint import pprint

import PIL.Image

from HorusOculars.mongo_db_connect import get_database
import boto3
import numpy as np
import hdbscan
from django.shortcuts import get_object_or_404

from HorusOculars.settings import AWS_STORAGE_BUCKET_NAME, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, RESOURCE_URL
from horus.models import VInfo


# 동영상에 존재하는 모든 인물의 얼굴 임베딩 벡터를 클러스터링
# 군집 별로 time slice 만들어서 저장
# 벡터에는 각 분/초가 같이 매핑되어있음 -> approximate_predict()로 어느 군집에 속하는지 알아냄
def make_clusters_and_index_table(user, npz, vname, face_list, time_table):
    #/ user_email / npz / 동영상이름.npz 불러오기
    s3r = boto3.resource('s3', aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
    pickle_file = s3r.Bucket(AWS_STORAGE_BUCKET_NAME).Object(npz).get()['Body'].read()
    npz_file = np.load(io.BytesIO(pickle_file), allow_pickle=True)

    encodings = npz_file

    index_table = list()
    clusterer = hdbscan.HDBSCAN(min_cluster_size=5, cluster_selection_epsilon=0.1, metric='euclidean',
                                prediction_data=True)
    clusterer.fit(encodings)
    label_ids = np.unique(clusterer.labels_)
    num_unique_faces = len(np.where(label_ids > -1)[0])
    print("[INFO] # unique faces: {}".format(num_unique_faces))
    print("군집 별 개수: ", collections.Counter(clusterer.labels_))
    for label_id in label_ids:
        if label_id == -1:
            continue
        indexes = np.where(clusterer.labels_ == label_id)[0]
        print(indexes)
        times = list()
        for i in indexes:
            for t in time_table:
                if i + 1 <= t['index']:
                    times.append(t['time'])
                    break

        choose_face = face_list[indexes[0]]
        img = PIL.Image.fromarray(choose_face)
        ifile = io.BytesIO()
        img.save(ifile, format='JPEG')
        value = ifile.getvalue()
        md = hashlib.md5(value).digest()
        img_md5 = base64.b64encode(md).decode('utf-8')

        key = "%s" % (user.email) + "/resource"  # user_email/resource
        s3r.Bucket(AWS_STORAGE_BUCKET_NAME).put_object(ContentMD5=img_md5, Key=key + '/%s/%s' % (vname,(str(label_id)+'.jpg')), Body=ifile, ContentType='jpg')
        ########### 여기서 대표 이미지 s3에 저장해야함
        img_url = RESOURCE_URL + "%s/%s/%s" % (key,vname, str(label_id)) + '.jpg'
        index_table.append({'cluster': int(label_id), 'continuous_time': times, 'face': img_url})

    for i in index_table:
        time_list = i['continuous_time']
        index_time, tl, l = list(), list(), list()
        [tl.append(x) for x in time_list if x not in tl]
        while len(tl) > 1:
            if tl[0] + 1 == tl[1]:
                l.append(tl.pop(0))
                if len(tl) == 1:
                    index_time.append({'start': l[0] - 0.5, 'end': l[-1] + 0.5})
            elif tl[0] + 1 != tl[1]:
                if len(l) == 0:
                    t = tl.pop(0)
                    index_time.append({'start': t - 0.5, 'end': t + 0.5})
                    continue
                l.append(tl.pop(0))
                index_time.append({'start': l[0] - 0.5, 'end': l[-1] + 0.5})
                l.clear()

        if index_time[-1]['end'] - 0.5 + 1 == tl[0]:
            index_time[-1]['end'] += 1
        else:
            index_time.append({'start': tl[0] - 0.5, 'end': tl[0] + 0.5})
        i['continuous_time'] = index_time

    pprint(index_table)
    # index_table -> MongoDB에 저장
    dbname = get_database()
    collection_name = dbname["indexed_data"]
    vinfo = {"_id":npz, "data":index_table}
    collection_name.insert_one(vinfo)

def predict_cluster(npz_key, compare_image_vec):
    #/ user_email / npz / 동영상이름.npz 불러오기
    s3r = boto3.resource('s3', aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
    pickle_file = s3r.Bucket(AWS_STORAGE_BUCKET_NAME).Object(npz_key).get()['Body'].read()
    npz_file = np.load(io.BytesIO(pickle_file), allow_pickle=True)

    encodings = npz_file

    clusterer = hdbscan.HDBSCAN(min_cluster_size=5, cluster_selection_epsilon=0.1, metric='euclidean',
                                prediction_data=True)
    clusterer.fit(encodings)
    label, strengths = hdbscan.approximate_predict(clusterer, compare_image_vec)
    return int(label)

