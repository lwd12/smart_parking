from django.shortcuts import render, redirect
from django.views.decorators import gzip
from django.http import StreamingHttpResponse
import cv2
import threading
import requests

API_HOST2 = 'http://3.34.74.107:8000/SessionData/'


def camera(request):
    if 'session' in request.COOKIES:  # 세션 여부 확인
        session = {}
        session['session'] = request.COOKIES['session']
        responses = requests.post(API_HOST2, data=session)
        data = responses.json()
        context = {
            'username': data['username'],
        }
        return render(request, 'camera/camera.html', context)
    else:
        return redirect('common:login')


def page_not_found(request, exception):
    return render(request, 'common/404.html', {})
