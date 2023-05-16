from django.shortcuts import render, redirect
from django.core.paginator import Paginator
import requests
from requests.exceptions import ConnectTimeout
from datetime import datetime

url = 'http://192.168.0.19:9000/safetyaccident/'
API_HOST2 = 'http://192.168.0.19:9000/SessionData/'
DATE_FORMAT = '%Y년 %m월 %d일 %H시 %M분'


def is_date_format(date_string):  # 데이터 형식 확인
    try:
        datetime.strptime(date_string, DATE_FORMAT)
        return True
    except ValueError:
        return False


def change(url):  # 시간 형식 수정하고 시간의 순서에 따라 정렬
    try:
        response = requests.get(url).json()
        sorted_data = []
        for item in response:
            date_string = item['safetyaccident_datetime']
            if date_string and not is_date_format(date_string):
                date_obj = datetime.fromisoformat(date_string)
                date_string = date_obj.strftime(DATE_FORMAT)
                item['safetyaccident_datetime'] = date_string
        if response:
            sorted_data = sorted(response, key=lambda x: x['safetyaccident_datetime'], reverse=True)
        return sorted_data
    except ConnectTimeout:
        return []


def warnings(request):
    if request.method == 'GET':
        response = change(url)

        page = request.GET.get('page', '1')
        kw = request.GET.get('kw', '')
        paginator = Paginator(response, 10)
        page_obj = paginator.get_page(page)

        if 'session' in request.COOKIES:
            session = {'session': request.COOKIES['session']}
            response = requests.post(API_HOST2, data=session).json()
            username = response.get('username', '')
            context = {
                'warning_list': page_obj,
                'page': page,
                'kw': kw,
                'username': username
            }
            return render(request, 'warning/warning.html', context)
        else:
            return redirect('common:login')
