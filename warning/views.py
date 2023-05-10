from django.shortcuts import render, redirect
from django.core.paginator import Paginator
import requests
from requests.exceptions import ConnectTimeout
from datetime import datetime
url = 'http://192.168.0.19:9000/safetyaccident/'
API_HOST2 = 'http://192.168.0.19:9000/SessionData/'

def is_date_format(string):
    try:
        datetime.strptime(string, "%Y년 %m월 %d일 %H시 %M분")
        return True
    except ValueError:
        return False


def change():
    try:
        req = requests.get(url)
        response = req.json()
        sorted_data = []
        for x in range(len(response)):
            safetyaccident_datetime = response[x]['safetyaccident_datetime']
            if safetyaccident_datetime:
                if not is_date_format(safetyaccident_datetime):
                    safetyaccident_datetimes = datetime.fromisoformat(safetyaccident_datetime)
                    safetyaccident_datetime = safetyaccident_datetimes.strftime("%Y년 %m월 %d일 %H시 %M분")
            response[x]['safetyaccident_datetime'] = safetyaccident_datetime
        if response:
            sorted_data = sorted(response, key=lambda x: x['safetyaccident_datetime'], reverse=True)
            return sorted_data
        else:
            return sorted_data

    except ConnectTimeout:
        sorted_data = []
        return sorted_data






def warnings(request):
    if request.method == 'GET':
        response = change()

        page = request.GET.get('page', '1')  # 페이지
        kw = request.GET.get('kw', '')  # 검색어

        paginator = Paginator(response, 10)
        page_obj = paginator.get_page(page)

        if 'session' in request.COOKIES:
            session = {}
            session['session'] = request.COOKIES['session']
            responses = requests.post(API_HOST2, data=session)
            data = responses.json()
            context = {'warning_list': page_obj,
                       'page': page,
                       'kw': kw,
                       'username': data['username']

                       }
            return render(request, 'warning/warning.html', context)
        else:
            return redirect('common:login')
