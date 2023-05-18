from django.shortcuts import render, redirect
from django.core.paginator import Paginator
import requests
from .SendApi import send_api
from requests.exceptions import ConnectTimeout
from django.http import Http404
import concurrent.futures

base_url = 'http://192.168.0.19:9000'
headers = {
    # "Authorization": "ToKen 750b311fec4b7c0a2a023bd557a149fb1f3a5085",  # 토큰값
    "Content-Type": "application/json",
    "charset": "UTF-8",
    "Accept": "*/*",
}


def get_residents():  # 입주민 정보 가져오기
    try:
        req = requests.get(base_url + '/residents_information/')
        response = req.json()
    except ConnectTimeout:
        response = {}
    return response


def search_residents(response, kw):  # 검색시 입주민 정보 찾기
    results = []
    for resident in response:
        filtered_resident = {k: v for k, v in resident.items() if k != 'residents_number'}
        if any(kw in str(value) for value in filtered_resident.values()):
            results.append(resident)
    return results if kw else [{k: v for k, v in resident.items() if k != 'residents_number'} for resident in response]


def paginate_residents(request, response):
    page = request.GET.get('page', '1')
    paginator = Paginator(response, 10)
    page_obj = paginator.get_page(page)
    return page_obj


def get_session(request):  # 세션 정보 확인
    if 'session' in request.COOKIES:
        session = {'session': request.COOKIES['session']}
        responses = requests.post(base_url + '/SessionData/', data=session)
        data = responses.json()
        return data['username']
    else:
        return None


def residents(request):
    if request.method == 'GET':
        response = get_residents()
        kw = request.GET.get('kw', '')  # 검색어
        if kw:
            response = search_residents(response, kw)

        page_obj = paginate_residents(request, response)
        username = get_session(request)

        if username:
            context = {'resident_list': page_obj,
                       'page': page_obj.number,
                       'kw': kw,
                       'username': username,
                       }
            return render(request, 'resident/resident.html', context)
        else:
            return redirect('common:login')


def resident_sign(request):  # 회원 정보 만들기
    username = get_session(request)

    if request.method == 'GET':
        context = {'error_message': False}

        if username:
            context['username'] = username
            return render(request, 'resident/sign.html', context)
        else:
            return redirect('common:login')

    if request.method == 'POST' and username:
        body = {
            'resident_name': request.POST.get('resident_name'),  # 입주민 이름
            'resident_dong': request.POST.get('resident_dong'),  # 사는 동
            'resident_ho': request.POST.get('resident_ho'),  # 사는 호
            'residents_doorpasswd': request.POST.get('residents_doorpasswd'),  # 건물 입구 비밀번호
            'resident_homephonenumber': request.POST.get('resident_homephonenumber'),  # 집 전화 번호
            'resident_phone': request.POST.get('resident_phone'),  # 핸드폰 번호
            'resident_carnumber': request.POST.get('resident_carnumber'),  # 입주민 차 번호
            'resident_typeofcar': request.POST.get('resident_typeofcar'),  # 입주민 차량 종류
            'login_PassWd': request.POST.get('login_PassWd'),  # 앱 비밀번호
            'resident_residency': bool(request.POST.get('resident_residency')),  # 거주 여부
        }
        requests.post(base_url + '/residents_information/', data=body)

        response = get_residents()
        kw = request.GET.get('kw', '')
        if kw:
            response = search_residents(response, kw)

        page_obj = paginate_residents(request, response)

        context = {
            'resident_list': page_obj,
            'page': request.GET.get('page', '1'),
            'kw': kw,
            'username': username,
        }
        return render(request, 'resident/resident.html', context)
    else:
        return redirect('common:login')


def change(request, residents_number):  # 입주민 정보 수정
    if 'session' not in request.COOKIES:
        return redirect('common:login')

    session = {'session': request.COOKIES['session']}
    username_response = requests.post(base_url + '/SessionData/', data=session)
    username = username_response.json().get('username')

    residents = get_residents()
    resident = next((resident for resident in residents if resident['residents_number'] == residents_number), None)
    if resident is None:
        raise Http404("Resident does not exist")

    if request.method == 'GET':
        context = {'username': username, **resident}
        return render(request, 'resident/change.html', context)

    if request.method == 'POST':
        body = {
            'resident_name': request.POST['resident_name'],
            'resident_dong': request.POST['resident_dong'],
            'resident_ho': request.POST['resident_ho'],
            'residents_doorpasswd': request.POST['residents_doorpasswd'],
            'resident_homephonenumber': request.POST['resident_homephonenumber'],
            'resident_phone': request.POST['resident_phone'],
            'resident_carnumber': request.POST['resident_carnumber'],
            'resident_typeofcar': request.POST['resident_typeofcar'],
            'login_PassWd': request.POST['login_PassWd'],
            'resident_residency': bool(request.POST.get('resident_residency'))
        }

        send_api(base_url, f'/residents_information/{residents_number}', 'PUT', headers, body)

        return redirect('residents:residents')
