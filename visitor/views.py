from django.shortcuts import render, redirect
from django.core.paginator import Paginator
import requests
from datetime import datetime
from requests.exceptions import ConnectTimeout
import base64
import os
from .SendApi import send_api

url = 'http://192.168.0.19:9000/unauthorized_parking/'
urls = 'http://192.168.0.19:9000/visitor_information/'
API_HOST2 = 'http://192.168.0.19:9000/SessionData/'
headers = {
    # "Authorization": "ToKen 750b311fec4b7c0a2a023bd557a149fb1f3a5085",  # 토큰값
    "Content-Type": "application/json",
    "charset": "UTF-8",
    "Accept": "*/*",
}
body = {}


def visitchange():
    sorted_data = []
    try:
        requ = requests.get(urls)
        response = requ.json()

    except ConnectTimeout:
        response = []

    for x in range(len(response)):
        car_in = response[x]['visitor_information_datetime']
        if car_in:
            if not is_date_format(car_in):
                car_ins = datetime.fromisoformat(car_in)
                car_in = car_ins.strftime("%Y년 %m월 %d일")
        response[x]['visitor_information_datetime'] = car_in
        request_date = response[x]['visitor_information_date']
        if request_date:
            if not is_date_format(request_date):
                request_dates = datetime.fromisoformat(request_date)
                request_date = request_dates.strftime("%Y년 %m월 %d일")
        response[x]['visitor_information_date'] = request_date

    if response:
        sorted_data = sorted(response, key=lambda x: x['visitor_information_number'], reverse=True)
    return sorted_data


def unauthchange():
    try:
        req = requests.get(url)
        response = req.json()
    except ConnectTimeout:
        response = []
    qdata = response
    sorted_data = []
    for x in range(len(qdata)):
        car_in = qdata[x]['entrydatetime']
        if car_in:
            if not is_date_format(car_in):
                car_ins = datetime.fromisoformat(car_in)
                car_in = car_ins.strftime("%Y년 %m월 %d일")
        qdata[x]['entrydatetime'] = car_in
        car_out = qdata[x]['exitdatetime']
        if car_out:
            if not is_date_format(car_out):
                car_outs = datetime.fromisoformat(car_out)
                car_out = car_outs.strftime("%Y년 %m월 %d일")
        else:
            car_out = ''
        qdata[x]['exitdatetime'] = car_out
        image = qdata[x]['unauthorized_carnumber']
        if image:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            image_dir = os.path.join(base_dir, "../static/images")
            os.makedirs(image_dir, exist_ok=True)

            image_data = base64.b64decode(image)
            image_path = os.path.join(image_dir, f"{qdata[x]['unauthorized_carnumbers']}.png")

            with open(image_path, "wb") as f:
                f.write(image_data)

    if qdata:
        sorted_data = sorted(qdata, key=lambda x: x['parking_log_number'], reverse=True)
    return sorted_data


def is_date_format(string):
    try:
        datetime.strptime(string, "%Y년 %m월 %d일 %H시 %M분")
        return True
    except ValueError:
        return False


def visitor(request):
    if request.method == 'GET':
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        folder_path = os.path.join(BASE_DIR, "static", "images")
        folder_path = os.path.abspath(folder_path)
        for file_name in os.listdir(folder_path):
            if file_name.endswith('.png'):
                file_path = os.path.join(folder_path, file_name)
                os.remove(file_path)

        pages = request.GET.get('page1', '1')  # 페이지
        kws = request.GET.get('kw1', '')  # 검색어

        page = request.GET.get('page2', '1')  # 페이지
        kw = request.GET.get('kw2', '')  # 검색어

        unauthorized = unauthchange()
        visit = visitchange()

        new_list1 = []
        results1 = []
        new_list2 = []
        results2 = []
        for x in visit:
            new_dict = {k: v for k, v in x.items() if
                        k not in ['visitor_information_number']}
            new_list1.append(new_dict)
            for key in new_dict:
                value = new_dict[key]
                if kws in str(value):
                    results1.append(x)
                    break
        if kws:
            visit = results1
        else:
            visit = [new_list1[i] | visit[i] for i in range(len(visit))]

        for x in unauthorized:
            new_dict = {k: v for k, v in x.items() if
                        k not in ['parking_log_number', 'typeofentrysandexit', 'unauthorized_carnumber']}
            new_list2.append(new_dict)
            for key in new_dict:
                value = new_dict[key]
                if kw in str(value):
                    results2.append(x)
                    break
        if kw:
            unauthorized = results2
        else:
            unauthorized = [new_list2[i] | unauthorized[i] for i in range(len(unauthorized))]

        paginator = Paginator(unauthorized, 5)
        page_obj = paginator.get_page(page)

        paginators = Paginator(visit, 5)
        page_objs = paginators.get_page(pages)

        if 'session' in request.COOKIES:
            session = {}
            session['session'] = request.COOKIES['session']
            responses = requests.post(API_HOST2, data=session)
            data = responses.json()
            context = {
                'visitor_list': page_objs,
                'page1': pages,
                'kw1': kws,

                'unauthorized_list': page_obj,
                'page2': page,
                'kw2': kw,

                'username': data['username'],
            }
            return render(request, 'visitor/visitor.html', context)
        else:
            return redirect('common:login')


def delete(request, visitor_information_number):
    if 'session' in request.COOKIES:
        print(visitor_information_number)
        API_HOST = "http://192.168.0.19:9000/"
        send_api(API_HOST, f"visitor_information/{visitor_information_number}", "DELETE", headers, body)
        return redirect('visitor:visitor')
    else:
        return redirect('common:login')
