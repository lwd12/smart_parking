from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from datetime import datetime
import requests
import re
from django.core.paginator import Paginator
from requests.exceptions import ConnectTimeout
import hashlib
from dateutil import parser

base_url = 'http://3.34.74.107:8000'
headers = {
    # "Authorization": "ToKen 750b311fec4b7c0a2a023bd557a149fb1f3a5085",  # 토큰값
    "Content-Type": "application/json",
    "charset": "UTF-8",
    "Accept": "*/*",
}
body = {}


def is_date_format(string):  # 시간 데이터 형식 확인
    try:
        datetime.strptime(string, "%Y년 %m월 %d일 %H시 %M분")
        return True
    except ValueError:
        return False


def change():
    try:
        reqs = requests.get(base_url + '/question/')
        responses = reqs.json()
        QData = responses
        sorted_data = []
        for x in range(len(QData)):
            create_date = QData[x]['create_datetime']
            if not is_date_format(create_date):
                create_date = parser.parse(create_date)
                create_date = create_date.strftime("%Y년 %m월 %d일 %H시 %M분")
            QData[x]['create_datetime'] = create_date
            QData[x]['count'] = Adata(QData[x]['question_number'])
            if QData:
                sorted_data = sorted(QData, key=lambda x: x['question_number'], reverse=True)
    except ConnectTimeout:
        sorted_data = []
    return sorted_data


def Adata(question_id):  # 각 질문 별 답 갯수 카운트
    try:
        reqx = requests.get(base_url + '/answer/')
        responsex = reqx.json()
        count = 0
        for x in range(len(responsex)):
            if question_id == responsex[x]['question_number']:
                count += 1
    except ConnectTimeout:
        count = None
    return count


def login_api(request):
    if request.method == 'GET':  # 세션 확인
        context = {'error_message': False}
        if 'session' in request.COOKIES:
            return redirect('pybo:index')
        else:
            return render(request, 'common/login.html', context)

    if request.method == "POST":
        data = {}
        # 폼에서 ID와 PW를 받아서 암호화
        login_ID = request.POST.get('login_ID')
        login_PassWd = request.POST.get('login_PassWd')
        hashed = hashlib.sha256()
        hashed.update(login_PassWd.encode('utf-8'))

        body['login_ID'] = login_ID
        body['login_PassWd'] = hashed.hexdigest()
        hashed.update(login_ID.encode('utf-8'))
        body['seesion'] = hashed.hexdigest()
        try:
            responses = requests.post(base_url + '/loginforAdministrator/', data=body)
            data = responses.json()
        except ConnectTimeout:
            data['error'] = "로그인 성공"
            data['session'] = ""
        if data['error']:
            if data['error'] == "로그인 성공":
                page = request.GET.get('page', '1')  # 페이지
                kw = request.GET.get('kw', '')  # 검색어
                respon = change()
                paginator = Paginator(respon, 10)
                page_obj = paginator.get_page(page)
                context = {
                    'question_list': page_obj,
                    'page': page,
                    'kw': kw,
                    'username': login_ID,
                }

                responses = render(request, 'pybo/question_list.html', context)
                responses.set_cookie('session', data['session'])
                return responses
            else:
                context = {'error_message': data['error']}
                return render(request, 'common/login.html', context)
        else:
            return render(request, 'common/login.html')


def logout(request):  # 세션 데이터 삭제
    response = HttpResponseRedirect('login')
    response.delete_cookie('session')

    return response


def signup(request):  # 회원 가입
    if request.method == 'GET':
        if 'session' in request.COOKIES:
            return redirect('pybo:index')
        else:
            return render(request, 'common/signup.html')

    if request.method == "POST":
        # 폼에서 ID,PW,email 받아오기
        context = {}
        respond = render(request, 'common/signup.html', context)
        login_ID = request.POST.get('username')
        login_PassWd = request.POST.get('password')
        email = request.POST.get('email')
        # 로그인 조건 ID는 15자 미만, PW는 특수문자 1개 이상,숫자 영어 혼용
        if not 8 <= len(login_ID) < 15:
            context = {'error_message': '아이디의 길이가 맞지 않습니다.'}
            return respond

        pattern = r"^(?=.*[!@#$%^&*(),.?\":{}|<>])(?=.*\d)(?=.*[a-zA-Z]).{8,19}$"
        if not re.match(pattern, login_PassWd):
            context = {'error_message': '비밀번호 형식이 맞지 않습니다.'}
            return respond
        # PW 암호화
        hashed_password = hashlib.sha256(login_PassWd.encode('utf-8')).hexdigest()
        hashed_session = hashlib.sha256(login_ID.encode('utf-8')).hexdigest()
        body = {'login_ID': login_ID, 'login_PassWd': hashed_password, 'email': email, 'session': hashed_session}
        print()
        response = requests.post(base_url + '/RegistUser/', data=body)
        data = response.json()

        if data.get('error'):
            context = {'error_message': data['error']}
            return respond

        page = request.GET.get('page', '1')  # 페이지
        kw = request.GET.get('kw', '')  # 검색어
        response_data = change()
        paginator = Paginator(response_data, 10)
        page_obj = paginator.get_page(page)
        context = {
            'question_list': page_obj,
            'page': page,
            'kw': kw,
            'username': login_ID,
        }

        response = render(request, 'pybo/question_list.html', context)
        response.set_cookie('session', data['session'])
        return response


def page_not_found(request, exception):
    if 'session' in request.COOKIES:  # 세션 여부 확인
        session = {}
        session['session'] = request.COOKIES['session']
        responses = requests.post(base_url + '/SessionData/', data=session)
        data = responses.json()
        context = {
            'username': data['username'],
        }
    return render(request, 'common/404.html', context)


def handler500(request):
    if 'session' in request.COOKIES:  # 세션 여부 확인
        session = {}
        session['session'] = request.COOKIES['session']
        responses = requests.post(base_url + '/SessionData/', data=session)
        data = responses.json()
        context = {
            'username': data['username'],
        }
    response = render(request, "common/500.html", context)
    response.status_code = 500
    return response
