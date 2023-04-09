import os, time, cv2
import boto3
from HorusOculars.settings import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, RESOURCE_URL, AWS_STORAGE_BUCKET_NAME, \
    S3_URI
from horus.models import Video


def extract_frame(user, input_video):
    ######## 전달 받은 동영상 /user_email/video/ 하위에 저장
    vname = input_video
    s3r = boto3.resource('s3', aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
    key = "%s" % (user.email) + "/video" # user_email/video

    s3r.Bucket(AWS_STORAGE_BUCKET_NAME).put_object(Key=key + '/%s' % (vname), Body=input_video, ContentType='mp4')
    save_video = Video.objects.create(
        owner=user,
        vname=vname,
        video_url=RESOURCE_URL+"%s/%s"%(key, vname)
    )
    video = RESOURCE_URL+"%s/%s"%(key, vname)
    # video = 'https://horusocular.s3.ap-northeast-2.amazonaws.com/email%40email.com/video/western.mp4'
    video_uri = S3_URI + key + "/%s"%(vname)

    dirpath = "C:\\Users\\ojyse\\PycharmProjects\\HorusOculars\\resource\\video\\"
    frame_path = "/resource/frame\\"
    filepath = dirpath+'western.mp4'

    video = cv2.VideoCapture(video) #'' 사이에 사용할 비디오 파일의 경로 및 이름을 넣어주도록 함

    if not video.isOpened():
        print("Could not Open :", video)
        exit(0)

    #불러온 비디오 파일의 정보 출력
    length = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(round(video.get(cv2.CAP_PROP_FPS)))

    print("length :", length)
    print("width :", width)
    print("height :", height)
    print("fps :", fps)

    count = 1
    frame_list = list()
    while(video.isOpened()):
        ret, frame = video.read()

        # if count > 60:
        if (video.get(cv2.CAP_PROP_POS_FRAMES) == video.get(cv2.CAP_PROP_FRAME_COUNT)):
          break

        frame_num = int(video.get(cv2.CAP_PROP_POS_FRAMES))

        if(frame_num % fps == 0): #동영상 1초마다 1프레임 추출
            t = int(video.get(cv2.CAP_PROP_POS_FRAMES) // int(fps))
            frame_list.append({'time': t, 'frame': frame})
            count += 1
    video.release()
    return save_video, frame_list, video_uri