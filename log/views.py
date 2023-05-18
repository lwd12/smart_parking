from django.core.paginator import Paginator
from django.shortcuts import render, redirect
import requests
from datetime import datetime
from requests.exceptions import ConnectTimeout

base_url = 'http://3.34.74.107:8000'


def get_data_from_api(url, excluded_keys):  # 데이터 가져오기
    req = requests.get(url)
    response = req.json()

    response = [{k: v for k, v in x.items() if k not in excluded_keys} for x in response]
    return response


def is_valid_date_format(string):  # 시간 데이터 형식 확인
    try:
        datetime.strptime(string, "%Y년 %m월 %d일 %H시 %M분")
        return True
    except ValueError:
        return False


def format_datetime(datetime_str):  # is_valid_date_format 함수에서 ISO 형식 확인 후 년.월.일.시.분으로 변환
    if datetime_str is not None:
        if is_valid_date_format(datetime_str):
            return datetime_str
        try:
            datetime_obj = datetime.fromisoformat(datetime_str)
            return datetime_obj.strftime("%Y년 %m월 %d일 %H시 %M분")
        except ValueError:
            pass
    return ''


def change():
    try:
        response = get_data_from_api(base_url + '/entrancetotheparkinglot/', ['typeofentrysandexit'])
        responses = get_data_from_api(base_url + '/unauthorized_parkinglot/', ['unauthorized_carnumber',
                                                                               'residents_doorpasswd',
                                                                               'residest_number',
                                                                               'typeofentrysandexit'])
        qdata = response + responses
        sorted_data = sorted(filter(lambda x: x['entrydatetime'] or x['exitdatetime'], qdata),
                             key=lambda x: x['entrydatetime'] or x['exitdatetime'], reverse=True)
        for data in sorted_data:
            data['entrydatetime'] = format_datetime(data['entrydatetime'])
            data['exitdatetime'] = format_datetime(data['exitdatetime'])
    except ConnectTimeout:
        sorted_data = []
    return sorted_data


def index(request):
    if request.method == 'GET':
        page = request.GET.get('page', '1')  # 페이지
        kw = request.GET.get('kw', '')  # 검색어
        repo = change()

        results = []
        for x in repo:
            new_dict = {k: v for k, v in x.items()}
            for key in new_dict:
                value = new_dict[key]
                if kw in str(value):
                    results.append(x)
                    break
        if kw:  # 검색 데이터가 있을 시에 작동
            repo = results
        else:
            repo = [{**x, **new_dict} for x, new_dict in zip(repo, results)]

        paginator = Paginator(repo, 10)
        page_obj = paginator.get_page(page)
        if 'session' in request.COOKIES:
            session = {'session': request.COOKIES['session']}
            responses = requests.post(base_url + '/SessionData/', data=session)
            data = responses.json()
            context = {
                'carlog_list': page_obj,
                'page': page,
                'kw': kw,
                'username': data['username'],
            }
            return render(request, 'carlog/carlog.html', context)
        else:
            return redirect('common:login')
