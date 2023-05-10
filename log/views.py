from django.core.paginator import Paginator
from django.shortcuts import render, redirect
import requests
from datetime import datetime
from requests.exceptions import ConnectTimeout

url = 'http://192.168.0.19:9000/entrancetotheparkinglot/'
urls = 'http://192.168.0.19:9000/unauthorized_parkinglot/'
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
        response = [
            {k: v for k, v in x.items() if k not in ['parking_log_number','typeofentrysandexit']}
            for x in response
        ]
        reqs = requests.get(urls)
        responses = reqs.json()
        responses = [
            {k: v for k, v in x.items() if k not in ['parking_log_number', 'unauthorized_carnumber',
                                                     'residents_doorpasswd', 'residest_number','typeofentrysandexit']}
            for x in responses
        ]
        qdata = response
        qdata.extend(responses)
        if qdata:
            sorted_data = sorted((x for x in qdata if x['entrydatetime'] is not None), key=lambda x: x['entrydatetime'], reverse=True)
        else:
            sorted_data = []
        for x in range(len(sorted_data)):
            entrydatetime = sorted_data[x]['entrydatetime']
            if entrydatetime:
                if not is_date_format(entrydatetime):
                    entrydatetimes = datetime.fromisoformat(entrydatetime)
                    entrydatetime = entrydatetimes.strftime("%Y년 %m월 %d일 %H시 %M분")
            sorted_data[x]['entrydatetime'] = entrydatetime
            exitdatetime = sorted_data[x]['exitdatetime']
            if exitdatetime:
                if not is_date_format(exitdatetime):
                    exitdatetimes = datetime.fromisoformat(exitdatetime)
                    exitdatetime = exitdatetimes.strftime("%Y년 %m월 %d일 %H시 %M분")
            else:
                exitdatetime = ''
            sorted_data[x]['exitdatetime'] = exitdatetime
    except ConnectTimeout:
        sorted_data = []

    return sorted_data


def index(request):
    if request.method == 'GET':

        page = request.GET.get('page', '1')  # 페이지
        kw = request.GET.get('kw', '')  # 검색어
        repon = change()

        new_list = []
        results = []
        for x in repon:
            new_dict = {k: v for k, v in x.items()}
            new_list.append(new_dict)
            for key in new_dict:
                value = new_dict[key]
                if kw in str(value):
                    results.append(x)
                    break
        if kw:
            repon = results
        else:
            repon = [new_list[i] | repon[i] for i in range(len(repon))]
        paginator = Paginator(repon, 10)
        page_obj = paginator.get_page(page)
        if 'session' in request.COOKIES:
            session = {}
            session['session'] = request.COOKIES['session']
            responses = requests.post(API_HOST2, data=session)
            data = responses.json()
            context = {'carlog_list': page_obj,
                       'page': page,
                       'kw': kw,
                       'username': data['username'],
                       }
            return render(request, 'carlog/carlog.html', context)
        else:
            return redirect('common:login')
