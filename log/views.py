from django.core.paginator import Paginator
from django.shortcuts import render, redirect
import requests
from datetime import datetime
from requests.exceptions import ConnectTimeout

url = 'http://192.168.0.19:9000/entrancetotheparkinglot/'
urls = 'http://192.168.0.19:9000/unauthorized_parkinglot/'
API_HOST2 = 'http://192.168.0.19:9000/SessionData/'


def get_data_from_api(url, excluded_keys):
    req = requests.get(url)
    response = req.json()

    response = [{k: v for k, v in x.items() if k not in excluded_keys} for x in response]
    return response


def is_valid_date_format(string):
    try:
        datetime.strptime(string, "%Y년 %m월 %d일 %H시 %M분")
        return True
    except ValueError:
        return False


def change():
    try:
        response = get_data_from_api(url, ['typeofentrysandexit'])
        responses = get_data_from_api(urls, ['unauthorized_carnumber',
                                             'residents_doorpasswd', 'residest_number', 'typeofentrysandexit'])
        qdata = response + responses

        sorted_data = sorted((x for x in qdata if x['entrydatetime'] or x['exitdatetime']),
                             key=lambda x: x['entrydatetime'] or x['exitdatetime'], reverse=True)

        for x, data in enumerate(sorted_data):
            entrydatetime = data['entrydatetime']
            if entrydatetime is not None:
                if not is_valid_date_format(entrydatetime):
                    try:
                        entrydatetime = datetime.fromisoformat(entrydatetime).strftime("%Y년 %m월 %d일 %H시 %M분")
                    except ValueError:
                        entrydatetime = ''
            sorted_data[x]['entrydatetime'] = entrydatetime

            exitdatetime = data['exitdatetime']
            if exitdatetime is not None:
                if not is_valid_date_format(exitdatetime):
                    try:
                        exitdatetime = datetime.fromisoformat(exitdatetime).strftime("%Y년 %m월 %d일 %H시 %M분")
                    except ValueError:
                        exitdatetime = ''
            else:
                exitdatetime = ''
            sorted_data[x]['exitdatetime'] = exitdatetime

    except ConnectTimeout:
        sorted_data = []

    return sorted_data or []


def index(request):
    if request.method == 'GET':
        page = request.GET.get('page', '1')  # 페이지
        kw = request.GET.get('kw', '')  # 검색어
        repon = change()

        results = []
        for x in repon:
            new_dict = {k: v for k, v in x.items()}
            for key in new_dict:
                value = new_dict[key]
                if kw in str(value):
                    results.append(x)
                    break
        if kw:
            repon = results
        else:
            repon = [{**x, **new_dict} for x, new_dict in zip(repon, results)]

        paginator = Paginator(repon, 10)
        page_obj = paginator.get_page(page)
        if 'session' in request.COOKIES:
            session = {'session': request.COOKIES['session']}
            responses = requests.post(API_HOST2, data=session)
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
