import json
from pprint import pprint

from django.shortcuts import get_object_or_404
import jwt

from HorusOculars.mongo_db_connect import get_database
from accounts.models import User
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from HorusOculars.settings import SECRET_KEY, ALGORITHM
from HorusOculars.videoModuler import indexing as id
from HorusOculars.videoModuler import download_video as download
from horus.models import Video

# 개인 워크 스페이스 동영상 return all api 필요
@csrf_exempt
def get_videos(request):
    if 'Authorization' not in request.headers:
        return HttpResponse(status=401)
    if request.method == 'GET':
        payload = jwt.decode(request.headers['Authorization'][7:], SECRET_KEY, ALGORITHM)
        user = get_object_or_404(User, email=payload['email'])
        response = [
            {
                'id':v.id,
                'name':v.vname,
                'url':v.video_url,
                'date':v.date.strftime('%Y-%m-%d'),
                'complete':v.complete
            }for v in Video.objects.filter(owner=user.id)
        ]
        return HttpResponse(json.dumps(response), status=200)
    else:
        return JsonResponse({'message': 'failed'}, status=400)

@csrf_exempt
def get_indexed_data(request):
    if 'Authorization' not in request.headers:
        return HttpResponse(status=401)
    if request.method == 'GET':
        video_id = request.GET['vid']
        payload = jwt.decode(request.headers['Authorization'][7:], SECRET_KEY, ALGORITHM)
        user = get_object_or_404(User, email=payload['email'])
        video = get_object_or_404(Video, id=video_id)
        dbname = get_database()
        info = dbname["indexed_data"].find_one({"_id": video.npz_url})
        result = json.dumps(info)
        return HttpResponse(result, status=200)
    else:
        return JsonResponse({'message': 'failed'}, status=400)


@csrf_exempt
def input_video(request):
    if 'Authorization' not in request.headers:
        return HttpResponse(status=401)
    if request.method == 'POST':
        input_video = request.FILES['video']
        payload = jwt.decode(request.headers['Authorization'][7:], SECRET_KEY, ALGORITHM)
        user = get_object_or_404(User, email=payload['email'])
        # video 입력 받아서 indexing 과정까지 처리하고 mongoDB에 내용 저장
        id.indexing(user, input_video)
        return HttpResponse(status=200)
    else:
        return JsonResponse({'message': 'failed'}, status=400)

@csrf_exempt
def input_youtube(request):
    if 'Authorization' not in request.headers:
        return HttpResponse(status=401)
    if request.method == 'POST':
        youtube_url = request.GET['youtube'] # youtube url
        payload = jwt.decode(request.headers['Authorization'][7:], SECRET_KEY, ALGORITHM)
        user = get_object_or_404(User, email=payload['email'])

        download.download(user, youtube_url)

        input_video = 'pytube 실행 함수'

        # video 입력 받아서 indexing 과정까지 처리하고 mongoDB에 내용 저장
        id.indexing(user, input_video)
        return HttpResponse(status=200)
    else:
        return JsonResponse({'message': 'failed'}, status=400)

@csrf_exempt
def search_person(request):
    if 'Authorization' not in request.headers:
        return HttpResponse(status=401)
    if request.method == 'POST':
        video_id = request.GET['vid']
        input_image = request.FILES['image']
        payload = jwt.decode(request.headers['Authorization'][7:], SECRET_KEY, ALGORITHM)
        user = get_object_or_404(User, email=payload['email'])

        video = get_object_or_404(Video, id=video_id)

        # video 입력 받아서 indexing 과정까지 처리하고 mongoDB에 내용 저장
        label = id.search_label(video.npz_url, input_image)
        print('predict : ' , label)

        if label == -1:
            return HttpResponse([], status=200)

        dbname = get_database()
        info = dbname["indexed_data"].find_one({"_id":video.npz_url})
        response = {}
        for i in info['data']:
            if i['cluster'] == label:
                response = {
                    'image': i['face'],
                    'time': i['continuous_time']
                }

        result = json.dumps(response)
        return HttpResponse(result, status=200)
    else:
        return JsonResponse({'message': 'failed'}, status=400)


@csrf_exempt
def get_video_info(request):
    if 'Authorization' not in request.headers:
        return HttpResponse(status=401)
    if request.method == 'GET':
        video_id = request.GET['vid']
        payload = jwt.decode(request.headers['Authorization'][7:], SECRET_KEY, ALGORITHM)
        user = get_object_or_404(User, email=payload['email'])
        video = get_object_or_404(Video, id=video_id)
        response = {
            'vname': video.vname,
            'url': video.video_url,
            'complete': video.complete
        }
        result = json.dumps(response)
        return HttpResponse(result, status=200)
    else:
        return JsonResponse({'message': 'failed'}, status=400)


@csrf_exempt
def get_stt_data(request):
    if 'Authorization' not in request.headers:
        return HttpResponse(status=401)
    if request.method == 'GET':
        video_id = request.GET['vid']
        payload = jwt.decode(request.headers['Authorization'][7:], SECRET_KEY, ALGORITHM)
        user = get_object_or_404(User, email=payload['email'])
        video = get_object_or_404(Video, id=video_id)
        dbname = get_database()
        info = dbname["speech_indexed_data"].find_one({"_id": video.vname})
        result = json.dumps(info)
        return HttpResponse(result, status=200)
    else:
        return JsonResponse({'message': 'failed'}, status=400)