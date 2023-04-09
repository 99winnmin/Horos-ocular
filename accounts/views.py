# Create your views here.
from pprint import pprint

from django.shortcuts import get_object_or_404
import json, jwt
from .models import User
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from HorusOculars.settings import SECRET_KEY, ALGORITHM


@csrf_exempt
def register(request):
    pprint('method : '+request.method)
    if request.method == 'POST':
        data = json.loads(request.body)
        pprint(data)

        try:
            if User.objects.filter(email=data['email']).exists():
                return JsonResponse({"message": "EXISTS_EMAIL"}, status=400)
            if data['password1'] != data['password2']:
                return HttpResponse(status=400)
            User.objects.create(
                email=data['email'],
                password=data['password1'],
                name=data['name']
            )
            return HttpResponse(status=200)

        except KeyError:
            return JsonResponse({"message": "INVALID_KEYS"}, status=400)


@csrf_exempt
def login(request):
    pprint('method : '+request.method)
    if request.method == 'POST':
        data = json.loads(request.body)
        pprint(data)
        user = get_object_or_404(User, email=data["email"])
        jwt_source = {'email': user.email}
        try:
            if User.objects.filter(email=data["email"]).exists():
                token = jwt.encode(jwt_source, SECRET_KEY, ALGORITHM)
                print(token)
                user.access_token = token
                user.save()
                response = JsonResponse({"access_token": token}, status=200)
                return response
            return JsonResponse({"msg": "invalid pw"}, status=400)
        except KeyError:
            return JsonResponse({'message': "INVALID_KEYS"}, status=400)


@csrf_exempt
def find_password(request):
    pprint('method : '+request.method)
    if request.method == 'GET':
        pprint(request.GET)
        email = request.GET['email']
        user = get_object_or_404(User, email=email)
        data = {
            'username': user.name,
            'password': user.password
        }
        return HttpResponse(json.dumps(data), status=200)
    else:
        return HttpResponse(status=400)


@csrf_exempt
def logout(request):
    pprint(request)
    if request.method == 'POST':
        data = json.loads(request.body)
        user = get_object_or_404(User, email=data["email"])
        try:
            if User.objects.filter(email=data["email"]).exists():
                user.access_token = ""
                user.save()
                return HttpResponse(status=200)
            return JsonResponse({"msg": "invalid pw"}, status=400)
        except KeyError:
            return JsonResponse({'message': "INVALID_KEYS"}, status=400)


@csrf_exempt
def user_info(request):

    pprint(request)
    print(request.headers['Authorization'][7:])
    if 'Authorization' not in request.headers:
        return HttpResponse(status=401)
    if request.method == 'GET':
        payload = jwt.decode(request.headers['Authorization'][7:], SECRET_KEY, ALGORITHM)
        print(payload)
        user = get_object_or_404(User, email=payload['email'])
        res = {
            'user_name': user.name
        }
        return HttpResponse(json.dumps(res), status=200)
    else:
        return JsonResponse({'message': '사용자 정보를 찾을 수 없음'}, status=400)
