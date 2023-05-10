from django.shortcuts import render, redirect
from django.core.paginator import Paginator
import requests
from .SendApi import send_api
from requests.exceptions import ConnectTimeout

API_HOST = 'http://192.168.0.19:9000/residents_information/'

API_HOST2 = "http://192.168.0.19:9000"
API_HOST3 = 'http://192.168.0.19:9000/SessionData/'
headers = {
    # "Authorization": "ToKen 750b311fec4b7c0a2a023bd557a149fb1f3a5085",  # 토큰값
    "Content-Type": "application/json",
    "charset": "UTF-8",
    "Accept": "*/*",
}


def residents(request):
    if request.method == 'GET':
        try:
            req = requests.get(API_HOST)
            response = req.json()
        except ConnectTimeout:
            response = {}
        page = request.GET.get('page', '1')  # 페이지
        kw = request.GET.get('kw', '')  # 검색어

        new_list = []
        results = []
        for x in response:
            new_dict = {k: v for k, v in x.items() if
                        k not in ['residents_number']}
            new_list.append(new_dict)
            for key in new_dict:
                value = new_dict[key]
                if kw in str(value):
                    results.append(x)
                    break
        if kw:
            response = results
        else:
            response = [new_list[i] | response[i] for i in range(len(response))]

        paginator = Paginator(response, 10)
        page_obj = paginator.get_page(page)

        if 'session' in request.COOKIES:
            session = {}
            session['session'] = request.COOKIES['session']
            responses = requests.post(API_HOST3, data=session)
            data = responses.json()
            context = {'resident_list': page_obj,
                       'page': page,
                       'kw': kw,
                       'username': data['username'],
                       }
            return render(request, 'resident/resident.html', context)
        else:
            return redirect('common:login')


def resident_sign(request):
    if request.method == 'GET':

        context = {'error_message': False}
        if 'session' in request.COOKIES:
            session = {}
            session['session'] = request.COOKIES['session']
            responses = requests.post(API_HOST3, data=session)
            data = responses.json()
            context = {
                'username': data['username'],
            }
            return render(request, 'resident/sign.html', context)
        else:
            return render(request, 'common/signup.html', context)

    if request.method == "POST":
        if 'session' in request.COOKIES:
            session = {}
            session['session'] = request.COOKIES['session']
            responses = requests.post(API_HOST3, data=session)
            data = responses.json()

            body = {}
            body['resident_name'] = request.POST.get('resident_name')
            body['resident_dong'] = request.POST.get('resident_dong')
            body['resident_ho'] = request.POST.get('resident_ho')
            body['residents_doorpasswd'] = request.POST.get('residents_doorpasswd')
            body['resident_homephonenumber'] = request.POST.get('resident_homephonenumber')
            body['resident_phone'] = request.POST.get('resident_phone')
            body['resident_carnumber'] = request.POST.get('resident_carnumber')
            body['resident_typeofcar'] = request.POST.get('resident_typeofcar')
            body['login_PassWd'] = request.POST.get('login_PassWd')
            if request.POST.get('resident_residency'):
                body['resident_residency'] = True
            else:
                body['resident_residency'] = False
            requests.post(API_HOST, data=body)
            page = request.GET.get('page', '1')  # 페이지
            kw = request.GET.get('kw', '')  # 검색어
            req = requests.get(API_HOST)
            responses = req.json()
            paginator = Paginator(responses, 10)
            page_obj = paginator.get_page(page)

            context = {
                'resident_list': page_obj,
                'page': page,
                'kw': kw,
                'username': data['username'],
            }
            response = render(request, 'resident/resident.html', context)
            return response
        else:
            return redirect('common:login')


def change(request, residents_number):
    if request.method == 'GET':
        if 'session' in request.COOKIES:
            session = {}
            session['session'] = request.COOKIES['session']
            responses = requests.post(API_HOST3, data=session)
            data = responses.json()
            req = requests.get(API_HOST)
            responses = req.json()
            for x in range(len(responses)):
                if responses[x]['residents_number'] == residents_number:
                    context = {
                        'username': data['username'],
                        'resident_name': responses[x]['resident_name'],
                        'resident_dong': responses[x]['resident_dong'],
                        'resident_ho': responses[x]['resident_ho'],
                        'residents_doorpasswd': responses[x]['residents_doorpasswd'],
                        'resident_homephonenumber': responses[x]['resident_homephonenumber'],
                        'resident_phone': responses[x]['resident_phone'],
                        'resident_carnumber': responses[x]['resident_carnumber'],
                        'resident_typeofcar': responses[x]['resident_typeofcar'],
                        'resident_residency': responses[x]['resident_residency'],
                        'login_PassWd': responses[x]['login_PassWd'],
                    }
                    return render(request, 'resident/change.html', context)
        else:
            return redirect('common:login')

    if request.method == "POST":
        if 'session' in request.COOKIES:
            session = {}
            session['session'] = request.COOKIES['session']
            responses = requests.post(API_HOST3, data=session)
            data = responses.json()
            body = {}
            body['resident_name'] = request.POST.get('resident_name')
            body['resident_dong'] = request.POST.get('resident_dong')
            body['resident_ho'] = request.POST.get('resident_ho')
            body['residents_doorpasswd'] = request.POST.get('residents_doorpasswd')
            body['resident_homephonenumber'] = request.POST.get('resident_homephonenumber')
            body['resident_phone'] = request.POST.get('resident_phone')
            body['resident_carnumber'] = request.POST.get('resident_carnumber')
            body['resident_typeofcar'] = request.POST.get('resident_typeofcar')
            body['login_PassWd'] = request.POST.get('login_PassWd')
            if request.POST.get('resident_residency'):
                body['resident_residency'] = True
            else:
                body['resident_residency'] = False

            send_api(API_HOST2, f"/residents_information/{residents_number}", "PUT", headers, body)

            page = request.GET.get('page', '1')  # 페이지
            kw = request.GET.get('kw', '')  # 검색어
            req = requests.get(API_HOST)
            responses = req.json()
            paginator = Paginator(responses, 10)
            page_obj = paginator.get_page(page)

            context = {
                'resident_list': page_obj,
                'page': page,
                'kw': kw,
                'username': data['username'],
            }
            response = render(request, 'resident/resident.html', context)
            return response
        else:
            return redirect('common:login')
