# import extract_frame as ef
# import face_detection as fd
# import embedding as em
# import clustering as cluster
from pprint import pprint

from .extract_frame import extract_frame as ef
from .face_detection import face_detection as fd
from .face_detection import input_img_face_detection as in_fd
from .embedding import make_embedding_vetors as em
from .embedding import input_img_ev as in_em
from .clustering import make_clusters_and_index_table as cluster
from .clustering import predict_cluster as predict
from .speech_to_text import stt
from ..mongo_db_connect import get_database


def indexing(user, input_video): # 이 함수에서 video를 입력 받는다고 가정
    # 동영상에서 프레임 추출
    video, frame_list, video_uri = ef(user, input_video) # 입력 받은 동영상을 이 함수에 넣어줘야함

    # stt 실행
    # stt(video_uri, str(input_video)[:-4])

    # 프레임에서 crop 추출 후 face info -> em으로 전달 (초마다 face 몇 개 나오는지 체크)
    face_list, time_table = fd(frame_list)

    # embedding vector 추출 -> (초마다 ev 몇개 나오는지 저장)
    npz_url = em(user, input_video, face_list)

    # ev를 군집화
    cluster(user, npz_url, str(input_video)[:-4], face_list, time_table)
    # 끝나면 mongoDB에 video에 대한 군집별 index 정보가 저장됨
    video.complete = 1
    video.save()

def search_label(npz_key, input_image):

    face_list = in_fd(input_image)

    compare_image_vec = in_em(face_list)

    label = predict(npz_key, compare_image_vec)

    return label
