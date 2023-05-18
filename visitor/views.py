from django.shortcuts import render, redirect
from django.core.paginator import Paginator
import requests
from datetime import datetime
from requests.exceptions import ConnectTimeout
import base64
import os
from .SendApi import send_api
from dateutil import parser

base_url = 'http://3.34.74.107:8000'

headers = {
    # "Authorization": "ToKen 750b311fec4b7c0a2a023bd557a149fb1f3a5085",  # 토큰값
    "Content-Type": "application/json",
    "charset": "UTF-8",
    "Accept": "*/*",
}
body = {}


def visitchange():  # 방문자 정보 가져오기
    try:
        response = requests.get(base_url + '/visitor_information/').json()
    except ConnectTimeout:
        response = []

    for record in response:  # ISO 시간 형태를 년.월.일로 수정
        car_in = record['visitor_information_datetime']
        if car_in and not is_date_format(car_in):
            car_in_dt = parser.parse(car_in)
            record['visitor_information_datetime'] = car_in_dt.strftime("%Y년 %m월 %d일")

        request_date = record['visitor_information_date']
        if request_date and not is_date_format(request_date):
            request_date_dt = parser.parse(request_date)
            record['visitor_information_date'] = request_date_dt.strftime("%Y년 %m월 %d일")

    return sorted(response, key=lambda x: x['visitor_information_number'], reverse=True)


def unauthchange():  # 비인가 차량 정보
    try:
        req = requests.get(base_url + '/unauthorized_parking/')
        response = req.json()
    except ConnectTimeout:
        response = []

    for data in response:
        entry_datetime = data.get('entrydatetime')
        if entry_datetime and not is_date_format(entry_datetime):
            dt = parser.parse(entry_datetime)
            data['entrydatetime'] = dt.strftime('%Y년 %m월 %d일')

        exit_datetime = data.get('exitdatetime', '')
        if exit_datetime and not is_date_format(exit_datetime):
            dt = parser.parse(exit_datetime)
            data['exitdatetime'] = dt.strftime('%Y년 %m월 %d일')

        unauthorized_carnumber = data.get('unauthorized_carnumber')
        if unauthorized_carnumber:  # 차량 사진 데이터 불러오고 static 파일에 차량 번호로 저장하기
            base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../static/images')
            os.makedirs(base_dir, exist_ok=True)
            image_path = os.path.join(base_dir, f'{data["unauthorized_carnumbers"]}.png')
            with open(image_path, 'wb') as f:
                f.write(base64.b64decode(unauthorized_carnumber))

    return sorted(response, key=lambda x: x['parking_log_number'], reverse=True)


def is_date_format(string):  # ISO 시간 형태 맞는지 확인
    try:
        datetime.strptime(string, "%Y년 %m월 %d일 %H시 %M분")
        return True
    except ValueError:
        return False


def remove_png_files(folder_path):  # 사진 데이터 쌓이지 않게 불러올 때 삭제 하기
    for file_name in os.listdir(folder_path):
        if file_name.endswith('.png'):
            file_path = os.path.join(folder_path, file_name)
            os.remove(file_path)


def filter_by_keyword(data, keyword):  # 검색 시 정보 찾기
    filtered_data = []
    for x in data:
        new_dict = {k: v for k, v in x.items() if k != 'visitor_information_number'}
        if keyword in str(new_dict.values()):
            filtered_data.append(x)
    return filtered_data if keyword else [new_dict | x for x in data]


def get_context_data(request):
    remove_png_files(
        os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static", "images")))

    unauthorized = unauthchange()
    visit = visitchange()

    unauthorized_kw = request.GET.get('kw2', '')
    unauthorized_data = filter_by_keyword(unauthorized, unauthorized_kw)
    unauthorized_paginator = Paginator(unauthorized_data, 5)
    unauthorized_page_obj = unauthorized_paginator.get_page(request.GET.get('page2', '1'))

    visit_kw = request.GET.get('kw1', '')
    visit_data = filter_by_keyword(visit, visit_kw)
    visit_paginator = Paginator(visit_data, 5)
    visit_page_obj = visit_paginator.get_page(request.GET.get('page1', '1'))

    if 'session' in request.COOKIES:
        session = {'session': request.COOKIES['session']}
        responses = requests.post(base_url + '/SessionData/', data=session)
        data = responses.json()
        return {
            'visitor_list': visit_page_obj,
            'page1': request.GET.get('page1', '1'),
            'kw1': visit_kw,

            'unauthorized_list': unauthorized_page_obj,
            'page2': request.GET.get('page2', '1'),
            'kw2': unauthorized_kw,

            'username': data['username'],
        }


def visitor(request):
    if 'session' in request.COOKIES:
        context = get_context_data(request)
        return render(request, 'visitor/visitor.html', context)
    else:
        return redirect('common:login')


def delete(request, visitor_information_number):  # 방문자 정보 삭제
    if 'session' in request.COOKIES:

        send_api(base_url, f"visitor_information/{visitor_information_number}", "DELETE", headers, body)
        return redirect('visitor:visitor')
    else:
        return redirect('common:login')
