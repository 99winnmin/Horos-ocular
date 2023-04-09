import numpy as np
import PIL, time, glob, re, cv2
from mtcnn import mtcnn

def face_detection(frame_list):
    frames = frame_list
    det = mtcnn.MTCNN()
    face_list, time_faces_list, time_table = list(), list(), list()
    count = 0

    for frame in frames:
        img = PIL.Image.fromarray(cv2.cvtColor(frame['frame'], cv2.COLOR_BGR2RGB))
        pixels = np.asarray(img)
        results = det.detect_faces(pixels)
        if not results:
            time_faces_list.append({'time': frame['time'], 'face_list': [], 'faces': 0})
            print("탐지된 얼굴이 없습니다 >>> ", frame['time'])
            continue

        for i in range(len(results)):
            x, y, w, h = results[i]['box']
            x, y = abs(x), abs(y)
            face = pixels[y:y + h, x:x + w]
            face_image = PIL.Image.fromarray(face)
            face_image_resize = face_image.resize((160, 160))
            face_list.append(np.asarray(face_image_resize))

        time_faces_list.append({'time': frame['time'], 'face_list': face_list, 'faces': len(results)})
        count += len(results)

    index_cnt = 0
    for i in time_faces_list:
        index_cnt += i['faces']
        time_table.append({'time': i['time'], 'index': index_cnt})

    return face_list, time_table


def input_img_face_detection(input_image):
    size = (160, 160)
    det = mtcnn.MTCNN()
    face_list = list()

    img = PIL.Image.open(input_image).convert('RGB')
    pixels = np.asarray(img)
    results = det.detect_faces(pixels)
    if not results:
        print("탐지된 얼굴이 없습니다 >>> ", str(img))
        return face_list

    for i in range(len(results)):
        x, y, w, h = results[i]['box']
        x, y = abs(x), abs(y)
        face = pixels[y:y + h, x:x + w]
        face_image = PIL.Image.fromarray(face)
        face_image_resize = face_image.resize(size)
        face_list.append(np.asarray(face_image_resize))

    return face_list